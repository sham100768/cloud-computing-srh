#!/usr/bin/env bash
# Runs reliability.sql in BigQuery over the replayed events, the same query
# Spark ran over the archive, into freight.carrier_reliability_stream.
set -euo pipefail
cd "$(dirname "$0")"
QUERY=$(python3 - <<'PY'
sql = open("reliability.sql").read()
body = "\n".join(l for l in sql.splitlines() if not l.lstrip().startswith("--"))
body = body.strip()
assert body.upper().startswith("WITH"), "reliability.sql should start with WITH"
print("CREATE OR REPLACE TABLE freight.carrier_reliability_stream AS\n"
      "WITH events AS (SELECT * FROM freight.replay_events WHERE mode = 'OCEAN'),\n"
      + body[4:].lstrip())
PY
)
bq query --use_legacy_sql=false --location=europe-west3 "$QUERY"
bq head -n 20 freight.carrier_reliability_stream
