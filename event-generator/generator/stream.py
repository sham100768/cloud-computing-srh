"""Live shipment events: the speed layer's input.

Shipments move through their milestones, and each milestone becomes one event.
Chaos options make the stream behave like real carrier feeds: duplicates,
late arrivals, and a schema change.
"""

import random
import uuid
from datetime import datetime, timedelta, timezone

from . import reference as ref

MILESTONES = {
    "OCEAN": ["BOOKED", "GATE_IN", "LOADED", "DEPARTED", "ARRIVED", "DISCHARGED", "GATE_OUT"],
    "AIR": ["BOOKED", "RECEIVED", "DEPARTED", "ARRIVED", "DELIVERED"],
}


class EventStream:
    """Yields events one at a time. Deterministic for a given seed."""

    def __init__(self, mode="both", seed=None, duplicates=0.0, late=0.0,
                 schema="v1", active_shipments=50, clock=None):
        if mode not in ("ocean", "air", "both"):
            raise ValueError("mode must be ocean, air or both")
        if schema not in ("v1", "v2"):
            raise ValueError("schema must be v1 or v2")
        self.modes = ["OCEAN", "AIR"] if mode == "both" else [mode.upper()]
        self.random = random.Random(seed)
        self.duplicates = duplicates
        self.late = late
        self.schema = schema
        self.active_shipments = active_shipments
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.shipments = []
        self.late_buffer = []
        self.counter = 0
        self.last_event = None

    def _new_shipment(self):
        r = self.random
        mode = r.choice(self.modes)
        shipper = r.choice([s for s in ref.SHIPPERS if mode in s[3]])
        if mode == "OCEAN":
            origin, destination, trade_lane, _, _ = r.choice(ref.OCEAN_LANES)
            carrier = r.choice(ref.OCEAN_CARRIERS)
        else:
            origin, destination, trade_lane, _, _ = r.choice(ref.AIR_LANES)
            carrier = r.choice(ref.AIRLINES)
        self.counter += 1
        return {
            "shipment_id": f"LIVE-{shipper[0]}-{self.counter:06d}",
            "shipper_id": shipper[0], "mode": mode, "origin": origin,
            "destination": destination, "trade_lane": trade_lane,
            "carrier": carrier[0], "reliability": carrier[3], "step": 0,
        }

    def _event(self, shipment, event_type, when, location, extra=None):
        r = self.random
        event = {
            "schema_version": 1,
            "event_id": str(uuid.UUID(int=r.getrandbits(128), version=4)),
            "shipment_id": shipment["shipment_id"],
            "shipper_id": shipment["shipper_id"],
            "mode": shipment["mode"],
            "event_type": event_type,
            "event_time": when.isoformat(),
            "location": location,
            "carrier": shipment["carrier"],
            "origin": shipment["origin"],
            "destination": shipment["destination"],
            "trade_lane": shipment["trade_lane"],
        }
        if extra:
            event.update(extra)
        if self.schema == "v2":
            # The carrier changed its feed: renamed fields, new version number.
            event["schema_version"] = 2
            event["occurred_at"] = event.pop("event_time")
            event["carrier_code"] = event.pop("carrier")
        return event

    def _advance(self):
        r = self.random
        while len(self.shipments) < self.active_shipments:
            self.shipments.append(self._new_shipment())
        shipment = r.choice(self.shipments)
        milestones = MILESTONES[shipment["mode"]]
        now = self.clock()

        # Unreliable carriers sometimes report a delay instead of progress.
        if shipment["step"] not in (0, len(milestones) - 1) and r.random() > shipment["reliability"] + 0.25:
            return self._event(shipment, "DELAYED", now, shipment["origin"],
                               {"delay_hours": r.randint(2, 72)})
        # Schema v2 also introduces an event type consumers have never seen.
        if self.schema == "v2" and shipment["step"] == len(milestones) - 2 and r.random() < 0.1:
            return self._event(shipment, "CUSTOMS_HOLD", now, shipment["destination"])

        event_type = milestones[shipment["step"]]
        location = shipment["origin"] if shipment["step"] < milestones.index("DEPARTED") + 1 else shipment["destination"]
        event = self._event(shipment, event_type, now, location)
        shipment["step"] += 1
        if shipment["step"] == len(milestones):
            self.shipments.remove(shipment)
        return event

    def __iter__(self):
        return self

    def __next__(self):
        r = self.random
        # Resend the previous event: at-least-once delivery in action.
        if self.last_event and r.random() < self.duplicates:
            return dict(self.last_event)
        # Release a held-back event, now late and out of order.
        if self.late_buffer and r.random() < 0.3:
            return self.late_buffer.pop(0)
        event = self._advance()
        if r.random() < self.late:
            minutes = r.randint(5, 180)
            key = "occurred_at" if self.schema == "v2" else "event_time"
            event[key] = (datetime.fromisoformat(event[key]) - timedelta(minutes=minutes)).isoformat()
            self.late_buffer.append(event)
            return self.__next__()
        self.last_event = event
        return event
