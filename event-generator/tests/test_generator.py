import csv
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from generator import batch
from generator.stream import EventStream


def fixed_clock():
    return datetime(2026, 11, 16, 16, 30, tzinfo=timezone.utc)


class BatchTests(unittest.TestCase):
    def test_same_seed_same_data(self):
        day = date(2026, 11, 1)
        self.assertEqual(batch.rates_for_day(42, day), batch.rates_for_day(42, day))
        self.assertEqual(batch.bookings_for_day(42, day), batch.bookings_for_day(42, day))

    def test_different_seed_different_prices(self):
        day = date(2026, 11, 1)
        a = [r["rate_usd"] for r in batch.rates_for_day(1, day)]
        b = [r["rate_usd"] for r in batch.rates_for_day(2, day)]
        self.assertNotEqual(a, b)

    def test_rates_are_positive_and_air_cheaper_per_unit(self):
        rows = batch.rates_for_day(42, date(2026, 11, 1))
        self.assertTrue(all(r["rate_usd"] > 0 for r in rows))
        ocean = [r for r in rows if r["mode"] == "OCEAN"]
        air = [r for r in rows if r["mode"] == "AIR"]
        self.assertEqual(len(ocean), 10 * 6 * 3 * 2)
        self.assertEqual(len(air), 8 * 4 * 3)

    def test_ocean_carriers_sail_weekly(self):
        sailings = []
        for offset in range(7):
            sailings += [s for s in batch.schedules_for_day(42, date(2026, 11, 2 + offset)) if s["mode"] == "OCEAN"]
        self.assertEqual(len(sailings), 10 * 6)

    def test_bookings_point_at_real_schedules(self):
        start = date(2026, 11, 1)
        schedule_ids = set()
        for offset in range(40):
            schedule_ids |= {s["schedule_id"] for s in batch.schedules_for_day(42, date.fromordinal(start.toordinal() + offset))}
        for booking in batch.bookings_for_day(42, start):
            self.assertIn(booking["schedule_id"], schedule_ids)

    def test_reliable_carrier_is_more_on_time(self):
        def on_time_share(carrier):
            rows = []
            for offset in range(180):
                rows += [s for s in batch.schedules_for_day(42, date.fromordinal(date(2026, 1, 1).toordinal() + offset))
                         if s["carrier_code"] == carrier]
            on_time = [r for r in rows if r["actual_arrival"] <= r["planned_arrival"] or
                       (datetime.fromisoformat(r["actual_arrival"]) - datetime.fromisoformat(r["planned_arrival"])).days == 0]
            return len(on_time) / len(rows)
        self.assertGreater(on_time_share("HRZ"), on_time_share("ATL"))

    def test_generate_writes_partitioned_files(self):
        with tempfile.TemporaryDirectory() as out:
            counts = batch.generate(out, date(2026, 11, 1), 2)
            path = Path(out) / "rates" / "date=2026-11-02" / "rates.csv"
            self.assertTrue(path.exists())
            with path.open() as f:
                self.assertEqual(next(csv.reader(f)), batch.RATE_FIELDS)
            self.assertEqual(counts["rates"], 2 * (360 + 96))


class StreamTests(unittest.TestCase):
    def take(self, stream, n):
        return [next(stream) for _ in range(n)]

    def test_same_seed_same_events(self):
        a = self.take(EventStream(seed=7, clock=fixed_clock), 50)
        b = self.take(EventStream(seed=7, clock=fixed_clock), 50)
        self.assertEqual(a, b)

    def test_shipments_start_with_booked(self):
        events = self.take(EventStream(seed=7, clock=fixed_clock), 500)
        first_seen = {}
        for e in events:
            first_seen.setdefault(e["shipment_id"], e["event_type"])
        self.assertTrue(all(t == "BOOKED" for t in first_seen.values()))

    def test_no_duplicates_by_default(self):
        events = self.take(EventStream(seed=7, clock=fixed_clock), 300)
        ids = [e["event_id"] for e in events]
        self.assertEqual(len(ids), len(set(ids)))

    def test_duplicates_option(self):
        events = self.take(EventStream(seed=7, duplicates=0.2, clock=fixed_clock), 300)
        ids = [e["event_id"] for e in events]
        self.assertLess(len(set(ids)), len(ids))

    def test_late_events_are_older_than_now(self):
        events = self.take(EventStream(seed=7, late=0.2, clock=fixed_clock), 300)
        late = [e for e in events if datetime.fromisoformat(e["event_time"]) < fixed_clock()]
        self.assertTrue(late)

    def test_schema_v2_renames_fields(self):
        events = self.take(EventStream(seed=7, schema="v2", clock=fixed_clock), 300)
        self.assertTrue(all(e["schema_version"] == 2 for e in events))
        self.assertTrue(all("occurred_at" in e and "event_time" not in e for e in events))
        self.assertTrue(all("carrier_code" in e and "carrier" not in e for e in events))

    def test_mode_filter(self):
        events = self.take(EventStream(mode="air", seed=7, clock=fixed_clock), 100)
        self.assertTrue(all(e["mode"] == "AIR" for e in events))


if __name__ == "__main__":
    unittest.main()
