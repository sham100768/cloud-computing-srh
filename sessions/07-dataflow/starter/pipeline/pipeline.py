"""The speed layer: shipment events into live BigQuery tables.

Two ways to run it:

  On your laptop or in Cloud Shell, from the sample file, printing the results:
      python pipeline.py --source file

  On Dataflow, from Kafka (ocean) and Pub/Sub (air), writing to BigQuery:
      ./run-on-dataflow.sh

The graph is the same both times. Only the first box (where events come from)
and the last ones (where results go) change.

    read -+-> archive files, every message as it came, per 5 minutes
          +-> parse -> dedupe -> event time -+-> live_events
                                             +-> departures per port, per window

The logic in each box lives in transforms.py. That's where your TODOs are.
"""

import argparse
import logging
import time

import apache_beam as beam
from apache_beam.io import fileio
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions, StandardOptions
from apache_beam.transforms import window
from apache_beam.transforms.deduplicate import DeduplicatePerKey
from apache_beam.utils.timestamp import Duration

from transforms import dedupe_key, departure_row, event_timestamp, parse_event, to_live_row

WINDOW_SECONDS = 5 * 60          # departures per port, per 5 minutes
DEDUPE_FOR = Duration(seconds=10 * 60)   # remember each event_id for 10 minutes

LIVE_SCHEMA = ",".join([
    "event_id:STRING", "shipment_id:STRING", "shipper_id:STRING", "mode:STRING",
    "event_type:STRING", "event_time:TIMESTAMP", "location:STRING", "carrier:STRING",
    "origin:STRING", "destination:STRING", "trade_lane:STRING", "delay_hours:INTEGER",
])
DEPARTURES_SCHEMA = "window_start:TIMESTAMP,window_end:TIMESTAMP,port:STRING,departures:INTEGER"


def read_events(p, args):
    """The first box: raw messages, as bytes or text."""
    if args.source == "file":
        return p | "Read sample file" >> beam.io.ReadFromText(args.input)

    from apache_beam.io.kafka import ReadFromKafka

    ocean = (
        p
        | "Read Kafka" >> ReadFromKafka(
            consumer_config={
                "bootstrap.servers": args.kafka_bootstrap,
                "group.id": args.kafka_group,
                "auto.offset.reset": args.kafka_offset_reset,
            },
            topics=[args.kafka_topic],
            # Save the group's position in Kafka as it goes, so a restarted job
            # carries on where it stopped. A replay doesn't need to.
            commit_offset_in_finalize=not args.replay,
            # Kafka stamps each record when the producer sends it, which is
            # close to the event time. The watermark follows these stamps.
            timestamp_policy=ReadFromKafka.create_time_policy,
        )
        | "Kafka value" >> beam.Map(lambda record: record[1])  # (key, value) -> value
    )
    if args.replay:
        return ocean  # a replay rebuilds from the Kafka log alone
    air = p | "Read Pub/Sub" >> beam.io.ReadFromPubSub(subscription=args.pubsub_subscription)
    return (ocean, air) | "Ocean and air together" >> beam.Flatten()


def window_bounds(w):
    return w.start.to_utc_datetime().isoformat(), w.end.to_utc_datetime().isoformat()


def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["file", "live"], default="file")
    parser.add_argument("--input", default="sample-events.jsonl")
    parser.add_argument("--out", default="out", help="file source: where the archive files go")
    parser.add_argument("--kafka-bootstrap")
    parser.add_argument("--kafka-topic", default="ocean-events")
    parser.add_argument("--kafka-group", default="dataflow-live")
    # Where a new consumer group starts. A group that has run before carries on
    # where it stopped, so the archive never misses what Kafka has.
    parser.add_argument("--kafka-offset-reset", default="earliest", choices=["latest", "earliest"])
    parser.add_argument("--pubsub-subscription", help="projects/<project>/subscriptions/air-events-dataflow")
    parser.add_argument("--dataset", help="<project>:freight")
    parser.add_argument("--archive", help="gs://<project>-raw/events/")
    parser.add_argument("--replay", action="store_true",
                        help="read the whole Kafka log again, as a new group, into replay_events only")
    args, beam_args = parser.parse_known_args(argv)
    if args.replay:
        args.kafka_group = f"replay-{int(time.time())}"
        args.kafka_offset_reset = "earliest"

    options = PipelineOptions(beam_args)
    # The lambdas below use functions imported at the top of this file, so the
    # workers need this file's imports too.
    options.view_as(SetupOptions).save_main_session = True
    live = args.source == "live"
    options.view_as(StandardOptions).streaming = live

    p = beam.Pipeline(options=options)
    raw = read_events(p, args)

    # The raw archive: every message exactly as it arrived, good or bad,
    # in files per 5 minutes of arrival. This is your lake: whatever the
    # pipeline gets wrong today, the original messages are still here.
    archive_lines = raw | "As text" >> beam.Map(
        lambda m: m.decode("utf-8", errors="replace") if isinstance(m, bytes) else m)
    if live:
        # A file has no arrival times, so only a live stream gets 5-minute files.
        archive_lines = archive_lines | "Archive windows" >> beam.WindowInto(window.FixedWindows(WINDOW_SECONDS))

    keyed = (
        raw
        | "Parse" >> beam.Map(parse_event)
        | "Drop bad messages" >> beam.Filter(lambda event: event is not None)
        | "Key by dedupe key" >> beam.Map(lambda event: (dedupe_key(event), event))
    )
    if live:
        # Keep the first event per key, and forget the key after 10 minutes.
        unique = keyed | "Drop duplicates" >> DeduplicatePerKey(processing_time_duration=DEDUPE_FOR) | beam.Values()
    else:
        # A file has an end, so group everything by key and keep one.
        unique = keyed | "Group duplicates" >> beam.GroupByKey() | "Keep one" >> beam.Map(lambda kv: list(kv[1])[0])
    # From here on, Beam knows each event by the time it happened.
    events = unique | "Event time" >> beam.Map(lambda event: window.TimestampedValue(event, event_timestamp(event)))

    # 1. Every event, as it arrives: the ops view reads this.
    live_rows = events | "Live row" >> beam.Map(to_live_row)

    # 2. Departures per port, per 5-minute window of event time. A window
    #    is counted once the watermark passes its end.
    departures = (
        events
        | "Departures only" >> beam.Filter(lambda event: event["event_type"] == "DEPARTED")
        | "Departure windows" >> beam.WindowInto(window.FixedWindows(WINDOW_SECONDS))
        | "Port" >> beam.Map(lambda event: (event["location"], 1))
        | "Count per port" >> beam.CombinePerKey(sum)
        | "Departure row" >> beam.Map(
            lambda kv, w=beam.DoFn.WindowParam: departure_row(kv[0], kv[1], *window_bounds(w)))
    )

    if live:
        bq = dict(
            create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            method=beam.io.WriteToBigQuery.Method.STREAMING_INSERTS,
        )
        if args.replay:
            # Same code, same logic, written somewhere new: nothing else changes.
            live_rows | "Write replay_events" >> beam.io.WriteToBigQuery(
                f"{args.dataset}.replay_events", schema=LIVE_SCHEMA, **bq)
        else:
            live_rows | "Write live_events" >> beam.io.WriteToBigQuery(
                f"{args.dataset}.live_events", schema=LIVE_SCHEMA, **bq)
            departures | "Write departures_by_port" >> beam.io.WriteToBigQuery(
                f"{args.dataset}.departures_by_port", schema=DEPARTURES_SCHEMA, **bq)
        archive_path = args.archive
    else:
        live_rows | "Count live rows" >> beam.combiners.Count.Globally() | "Print count" >> beam.Map(
            lambda n: print(f"live_events: {n} rows"))
        departures | "Print departures" >> beam.Map(
            lambda row: print(f"departures {row['window_start'][11:16]} {row['port']}: {row['departures']}"))
        archive_path = args.out

    if not args.replay:
        archive_lines | "Write archive" >> fileio.WriteToFiles(
            path=archive_path,
            file_naming=fileio.default_file_naming(prefix="events", suffix=".jsonl"),
            shards=1,
        )

    result = p.run()
    if live:
        # A streaming job never finishes, so don't wait for it: it keeps running on
        # Dataflow after this script ends. Drain it when you're done (teardown).
        print("Submitted. Watch it in the console: Dataflow, Jobs.")
    else:
        result.wait_until_finish()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.WARNING)
    run()
