-- Carrier reliability per day: of the ocean shipments that arrived, how many
-- reported a delay on the way.
--
-- This one query builds the table both ways. Spark runs it over the raw
-- archive (Lambda); BigQuery runs it over the replayed events (Kappa). Either
-- way it reads a table called `events` with event_type, event_time, carrier
-- and shipment_id.
--
-- The two building blocks are done for you:
WITH arrivals AS (
  SELECT carrier, shipment_id, DATE(event_time) AS arrival_date
  FROM events
  WHERE event_type = 'ARRIVED'
),
delayed AS (
  SELECT DISTINCT shipment_id
  FROM events
  WHERE event_type = 'DELAYED'
)
-- TODO: for each carrier and arrival_date, return
--   shipments_arrived   how many shipments arrived
--   shipments_delayed   how many of those reported a delay
--   on_time_share       the share that didn't, rounded to 3 decimals
--
-- Join arrivals to delayed, then group. Think about what a shipment that never
-- reported a delay looks like after the join, and about what a duplicate
-- event would do to your counts.
--
-- Write `* 1.0` before dividing, so Spark and BigQuery both divide as decimals.
SELECT
  a.carrier,
  a.arrival_date
FROM arrivals AS a
GROUP BY a.carrier, a.arrival_date
