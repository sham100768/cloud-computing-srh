"""Daily batch files: rates, schedules and bookings.

The output depends only on the seed and the date, so every student who runs the
same command gets exactly the same files, whatever start date they pick.
"""

import csv
import math
import random
from datetime import date, datetime, time, timedelta
from pathlib import Path

from . import reference as ref

RATE_FIELDS = [
    "rate_date", "mode", "contract_type", "origin", "destination", "trade_lane",
    "carrier_code", "carrier_name", "equipment", "weight_break", "rate_usd", "unit",
]
SCHEDULE_FIELDS = [
    "schedule_id", "mode", "carrier_code", "origin", "destination", "trade_lane",
    "vessel_or_flight", "planned_departure", "planned_arrival",
    "actual_departure", "actual_arrival",
]
BOOKING_FIELDS = [
    "shipment_id", "booking_date", "shipper_id", "shipper_name", "mode", "origin",
    "destination", "trade_lane", "carrier_code", "equipment", "weight_break",
    "quantity", "unit", "unit_rate_usd", "total_cost_usd", "schedule_id",
]


def _rng(seed, *parts):
    """A random generator that depends only on the seed and the given parts."""
    return random.Random(f"{seed}|" + "|".join(str(p) for p in parts))


def _market_index(seed, day, lane_key):
    """A smooth, repeatable market movement for one lane on one day."""
    n = day.toordinal()
    phase = _rng(seed, "phase", lane_key).random() * 2 * math.pi
    seasonal = 0.15 * math.sin(2 * math.pi * n / 182 + phase)
    monthly = 0.05 * math.sin(2 * math.pi * n / 30 + phase)
    noise = _rng(seed, "noise", lane_key, n).uniform(-0.03, 0.03)
    return 1 + seasonal + monthly + noise


def _sailing_weekday(carrier, origin, destination):
    """Each carrier sails each ocean lane once a week, on a fixed weekday."""
    return sum(ord(c) for c in carrier + origin + destination) % 7


def _schedule_id(mode, carrier, origin, destination, departure):
    prefix = "S" if mode == "OCEAN" else "F"
    return f"{prefix}-{carrier}-{origin}{destination}-{departure:%Y%m%d}"


def rate(seed, day, mode, carrier, lane, unit_key, contract_type="spot"):
    """The price for one carrier, lane and equipment or weight break on one day."""
    origin, destination, _, base, _ = lane
    lane_key = f"{mode}-{origin}-{destination}"
    carriers = ref.OCEAN_CARRIERS if mode == "OCEAN" else ref.AIRLINES
    premium = next(c[2] for c in carriers if c[0] == carrier)
    multiplier = (ref.EQUIPMENT if mode == "OCEAN" else ref.WEIGHT_BREAKS)[unit_key]
    if contract_type == "long_term":
        quarter_start = date(day.year, 3 * ((day.month - 1) // 3) + 1, 1)
        index = 0.92 * _market_index(seed, quarter_start, lane_key)
    else:
        index = _market_index(seed, day, lane_key)
    carrier_noise = _rng(seed, "carrier", carrier, lane_key, day.toordinal()).uniform(-0.02, 0.02)
    value = base * multiplier * premium * index * (1 + carrier_noise)
    return round(value, 2 if mode == "OCEAN" else 3)


def rates_for_day(seed, day):
    rows = []
    for lane in ref.OCEAN_LANES:
        origin, destination, trade_lane, _, _ = lane
        for code, name, _, _ in ref.OCEAN_CARRIERS:
            for equipment in ref.EQUIPMENT:
                for contract_type in ("spot", "long_term"):
                    rows.append({
                        "rate_date": day.isoformat(), "mode": "OCEAN",
                        "contract_type": contract_type, "origin": origin,
                        "destination": destination, "trade_lane": trade_lane,
                        "carrier_code": code, "carrier_name": name,
                        "equipment": equipment, "weight_break": "",
                        "rate_usd": rate(seed, day, "OCEAN", code, lane, equipment, contract_type),
                        "unit": "per_container",
                    })
    for lane in ref.AIR_LANES:
        origin, destination, trade_lane, _, _ = lane
        for code, name, _, _ in ref.AIRLINES:
            for weight_break in ref.WEIGHT_BREAKS:
                rows.append({
                    "rate_date": day.isoformat(), "mode": "AIR", "contract_type": "spot",
                    "origin": origin, "destination": destination, "trade_lane": trade_lane,
                    "carrier_code": code, "carrier_name": name, "equipment": "",
                    "weight_break": weight_break,
                    "rate_usd": rate(seed, day, "AIR", code, lane, weight_break),
                    "unit": "per_kg",
                })
    return rows


def schedules_for_day(seed, day):
    """Sailings and flights planned to depart on this day, with what actually happened."""
    rows = []
    for origin, destination, trade_lane, _, transit_days in ref.OCEAN_LANES:
        for code, _, _, reliability in ref.OCEAN_CARRIERS:
            if day.weekday() != _sailing_weekday(code, origin, destination):
                continue
            r = _rng(seed, "sailing", code, origin, destination, day.toordinal())
            departure = datetime.combine(day, time(r.randint(6, 20)))
            arrival = departure + timedelta(days=transit_days)
            late_departure = timedelta(hours=r.choice([0, 0, 0, 6, 12, 24, 48]))
            delay = timedelta(0) if r.random() < reliability else timedelta(days=r.randint(1, 6))
            rows.append({
                "schedule_id": _schedule_id("OCEAN", code, origin, destination, day),
                "mode": "OCEAN", "carrier_code": code, "origin": origin,
                "destination": destination, "trade_lane": trade_lane,
                "vessel_or_flight": r.choice(ref.VESSEL_NAMES),
                "planned_departure": departure.isoformat(),
                "planned_arrival": arrival.isoformat(),
                "actual_departure": (departure + late_departure).isoformat(),
                "actual_arrival": (arrival + late_departure + delay).isoformat(),
            })
    for origin, destination, trade_lane, _, transit_hours in ref.AIR_LANES:
        for code, _, _, reliability in ref.AIRLINES:
            r = _rng(seed, "flight", code, origin, destination, day.toordinal())
            departure = datetime.combine(day, time(r.randint(0, 23)))
            arrival = departure + timedelta(hours=transit_hours)
            delay = timedelta(0) if r.random() < reliability else timedelta(hours=r.randint(2, 30))
            rows.append({
                "schedule_id": _schedule_id("AIR", code, origin, destination, day),
                "mode": "AIR", "carrier_code": code, "origin": origin,
                "destination": destination, "trade_lane": trade_lane,
                "vessel_or_flight": f"{code}{r.randint(100, 999)}",
                "planned_departure": departure.isoformat(),
                "planned_arrival": arrival.isoformat(),
                "actual_departure": (departure + delay / 2).isoformat(),
                "actual_arrival": (arrival + delay).isoformat(),
            })
    return rows


def _next_departure(mode, carrier, origin, destination, booking_day):
    """The carrier's first departure at least three days after booking (ocean) or next day (air)."""
    if mode == "AIR":
        return booking_day + timedelta(days=1)
    target = _sailing_weekday(carrier, origin, destination)
    first = booking_day + timedelta(days=3)
    return first + timedelta(days=(target - first.weekday()) % 7)


def _pick_carrier(r, focus, carriers):
    if focus == "cost":
        weights = [1 / (c[2] ** 8) for c in carriers]
    elif focus == "reliability":
        weights = [c[3] ** 6 for c in carriers]
    else:
        weights = [1] * len(carriers)
    return r.choices(carriers, weights=weights)[0]


def bookings_for_day(seed, day):
    rows = []
    for shipper_id, shipper_name, focus, modes, per_day in ref.SHIPPERS:
        r = _rng(seed, "bookings", shipper_id, day.toordinal())
        lanes_r = _rng(seed, "shipper-lanes", shipper_id)
        ocean_lanes = lanes_r.sample(ref.OCEAN_LANES, 4)
        air_lanes = lanes_r.sample(ref.AIR_LANES, 3)
        count = max(0, per_day + r.randint(-2, 2))
        for i in range(count):
            mode = r.choice(modes)
            if mode == "OCEAN":
                lane = r.choice(ocean_lanes)
                carrier = _pick_carrier(r, focus, ref.OCEAN_CARRIERS)
                unit_key = r.choices(list(ref.EQUIPMENT), weights=[2, 3, 5])[0]
                quantity = r.randint(1, 12)
                unit = "containers"
            else:
                lane = r.choice(air_lanes)
                carrier = _pick_carrier(r, focus, ref.AIRLINES)
                quantity = r.randint(80, 4000)
                unit_key = "+1000" if quantity >= 1000 else "+500" if quantity >= 500 else "+100"
                unit = "kg"
            origin, destination, trade_lane, _, _ = lane
            unit_rate = rate(seed, day, mode, carrier[0], lane, unit_key)
            departure = _next_departure(mode, carrier[0], origin, destination, day)
            rows.append({
                "shipment_id": f"{shipper_id}-{day:%Y%m%d}-{i + 1:03d}",
                "booking_date": day.isoformat(), "shipper_id": shipper_id,
                "shipper_name": shipper_name, "mode": mode, "origin": origin,
                "destination": destination, "trade_lane": trade_lane,
                "carrier_code": carrier[0],
                "equipment": unit_key if mode == "OCEAN" else "",
                "weight_break": unit_key if mode == "AIR" else "",
                "quantity": quantity, "unit": unit, "unit_rate_usd": unit_rate,
                "total_cost_usd": round(unit_rate * quantity, 2),
                "schedule_id": _schedule_id(mode, carrier[0], origin, destination, departure),
            })
    return rows


def _write(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def generate(out_dir, start, days, seed=42):
    """Write one folder per file type, one CSV per day, in a lake-style layout.

    out/rates/date=2026-11-01/rates.csv and so on, which BigQuery and Spark
    can read as date-partitioned data.
    """
    out = Path(out_dir)
    counts = {"rates": 0, "schedules": 0, "bookings": 0}
    for offset in range(days):
        day = start + timedelta(days=offset)
        for name, fields, rows in (
            ("rates", RATE_FIELDS, rates_for_day(seed, day)),
            ("schedules", SCHEDULE_FIELDS, schedules_for_day(seed, day)),
            ("bookings", BOOKING_FIELDS, bookings_for_day(seed, day)),
        ):
            _write(out / name / f"date={day.isoformat()}" / f"{name}.csv", fields, rows)
            counts[name] += len(rows)
    return counts
