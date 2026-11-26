"""The logic of the pipeline, as plain Python functions.

pipeline.py wires these into a Beam graph. Keeping them here means you can
test them in a second with pytest, without starting a pipeline at all:

    python -m pytest tests -q

There are three TODOs. Each has tests in tests/test_transforms.py that fail
until you finish it.
"""

import json
from datetime import datetime

# The fields every event must have before the pipeline lets it through.
REQUIRED = ("event_id", "shipment_id", "event_type", "event_time", "location")

OCEAN = ["BOOKED", "GATE_IN", "LOADED", "DEPARTED", "ARRIVED", "DISCHARGED", "GATE_OUT"]
AIR = ["BOOKED", "RECEIVED", "DEPARTED", "ARRIVED", "DELIVERED"]
KNOWN_EVENT_TYPES = set(OCEAN) | set(AIR) | {"DELAYED"}


def parse_event(raw):
    """Turn one raw message into an event dict, or None if it's unusable.

    `raw` is bytes or str: one JSON object, as the generator sends it.

    TODO 1: return None, instead of raising, when
      - the message isn't valid JSON, or isn't a JSON object
      - any field in REQUIRED is missing or empty
      - the event_type isn't in KNOWN_EVENT_TYPES
    Otherwise return the dict.

    A pipeline that raises on one bad message retries it for ever and stops
    making progress, so bad messages are dropped here instead.
    """
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    return json.loads(raw)


def event_timestamp(event):
    """The time the event happened, as Unix seconds (a float).

    TODO 2: return the event's own `event_time`, converted to Unix seconds.
    Hint: datetime.fromisoformat() reads the generator's timestamps, and a
    datetime has a .timestamp() method.

    Beam windows by whatever this returns. Returning the time now would window
    by processing time: when the event reached you, not when the ship left.
    """
    return datetime.now().timestamp()


def dedupe_key(event):
    """The key two copies of the same event share.

    TODO 3: return the value that is the same for a duplicate and its
    original, and different for any two real events.

    The generator resends some events, like a carrier retrying a delivery.
    The pipeline keeps the first event it sees for each key and drops the rest.
    """
    return event["shipment_id"]


def to_live_row(event):
    """One row of the live_events table."""
    return {
        "event_id": event["event_id"],
        "shipment_id": event["shipment_id"],
        "shipper_id": event.get("shipper_id"),
        "mode": event.get("mode"),
        "event_type": event["event_type"],
        "event_time": event["event_time"],
        "location": event["location"],
        "carrier": event.get("carrier"),
        "origin": event.get("origin"),
        "destination": event.get("destination"),
        "trade_lane": event.get("trade_lane"),
        "delay_hours": event.get("delay_hours"),
    }


def departure_row(port, count, window_start, window_end):
    """One row of the departures_by_port table: departures from one port in one window."""
    return {
        "window_start": window_start,
        "window_end": window_end,
        "port": port,
        "departures": count,
    }
