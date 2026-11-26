-- The same table, built two ways, side by side.
SELECT
  COALESCE(b.carrier, s.carrier)           AS carrier,
  COALESCE(b.arrival_date, s.arrival_date) AS arrival_date,
  b.shipments_arrived                      AS batch_arrived,
  s.shipments_arrived                      AS stream_arrived,
  b.on_time_share                          AS batch_on_time,
  s.on_time_share                          AS stream_on_time
FROM freight.carrier_reliability_batch AS b
FULL OUTER JOIN freight.carrier_reliability_stream AS s
  ON b.carrier = s.carrier AND b.arrival_date = s.arrival_date
ORDER BY arrival_date, carrier;
