#!/usr/bin/env bash
# The Kappa path: replays the whole Kafka log through session 7's pipeline, as
# a new consumer group, into freight.replay_events. Same code as the live job.
set -euo pipefail
cd "$(dirname "$0")/../../07-dataflow/starter/pipeline"
./run-on-dataflow.sh --replay --job_name freight-replay
