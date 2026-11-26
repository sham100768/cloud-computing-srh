import json
from pathlib import Path

from transforms import dedupe_key, event_timestamp, parse_event

GOOD = {
    "schema_version": 1,
    "event_id": "3488f876-05e9-49f3-842e-7fc229540a6e",
    "shipment_id": "LIVE-SHP01-000045",
    "event_type": "DEPARTED",
    "event_time": "2026-12-02T15:00:00+00:00",
    "location": "CNNGB",
}


# ---------------------------------------------------------------- TODO 1

def test_parse_keeps_a_good_event():
    assert parse_event(json.dumps(GOOD))["shipment_id"] == "LIVE-SHP01-000045"


def test_parse_accepts_bytes():
    assert parse_event(json.dumps(GOOD).encode())["event_type"] == "DEPARTED"


def test_parse_drops_broken_json():
    assert parse_event('{"event_id": "x", "shipment_id": "LIVE') is None


def test_parse_drops_something_that_is_not_an_object():
    assert parse_event("[1, 2, 3]") is None


def test_parse_drops_a_missing_field():
    event = dict(GOOD)
    del event["event_time"]
    assert parse_event(json.dumps(event)) is None


def test_parse_drops_an_empty_field():
    assert parse_event(json.dumps(dict(GOOD, location=""))) is None


def test_parse_drops_an_unknown_event_type():
    assert parse_event(json.dumps(dict(GOOD, event_type="TELEPORTED"))) is None


def test_the_sample_file_has_three_bad_lines():
    lines = (Path(__file__).parent.parent / "sample-events.jsonl").read_text().splitlines()
    assert sum(parse_event(line) is None for line in lines) == 3


# ---------------------------------------------------------------- TODO 2

def test_timestamp_is_the_event_time():
    assert event_timestamp(GOOD) == 1796223600.0  # 2026-12-02 15:00 UTC


def test_timestamp_respects_the_time_zone():
    later = dict(GOOD, event_time="2026-12-02T16:00:00+01:00")  # the same moment
    assert event_timestamp(later) == event_timestamp(GOOD)


# ---------------------------------------------------------------- TODO 3

def test_a_duplicate_has_the_same_key():
    assert dedupe_key(dict(GOOD)) == dedupe_key(GOOD)


def test_two_events_of_one_shipment_have_different_keys():
    arrived = dict(GOOD, event_id="b1e0c2d4-0000-4000-8000-000000000002", event_type="ARRIVED")
    assert dedupe_key(arrived) != dedupe_key(GOOD)


def test_the_sample_file_has_17_duplicates():
    lines = (Path(__file__).parent.parent / "sample-events.jsonl").read_text().splitlines()
    events = [e for e in map(parse_event, lines) if e]
    assert len(events) - len({dedupe_key(e) for e in events}) == 17
