"""Command line entry point.

  python -m generator batch --start 2026-10-01 --days 30 --out data
  python -m generator stream --sink stdout --rate 2 --count 20

Every stream option can also come from an environment variable (SINK, RATE,
MODE, ...), which is how you configure it in a container.
"""

import argparse
import os
import time
from datetime import date

from . import batch, sinks
from .stream import EventStream


def env(name, default=None):
    return os.environ.get(name, default)


def make_sink(args):
    if args.sink == "stdout":
        return sinks.StdoutSink()
    if args.sink == "file":
        return sinks.FileSink(args.file)
    if args.sink == "http":
        if not args.http_url:
            raise SystemExit("--http-url is required for the http sink")
        return sinks.HttpSink(args.http_url)
    if args.sink == "kafka":
        return sinks.KafkaSink(args.kafka_bootstrap, args.kafka_topic)
    if args.sink == "pubsub":
        if not args.pubsub_topic:
            raise SystemExit("--pubsub-topic is required, e.g. projects/my-project/topics/air-events")
        return sinks.PubSubSink(args.pubsub_topic)
    raise SystemExit(f"unknown sink {args.sink}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="generator", description="Synthetic freight data")
    sub = parser.add_subparsers(dest="command", required=True)

    b = sub.add_parser("batch", help="write daily rate, schedule and booking files")
    b.add_argument("--start", default=env("START", "2026-10-01"), help="first day, YYYY-MM-DD")
    b.add_argument("--days", type=int, default=int(env("DAYS", "30")))
    b.add_argument("--out", default=env("OUT", "data"))
    b.add_argument("--seed", type=int, default=int(env("SEED", "42")))

    s = sub.add_parser("stream", help="emit live shipment events")
    s.add_argument("--mode", choices=["ocean", "air", "both"], default=env("MODE", "both"))
    s.add_argument("--sink", choices=["stdout", "file", "http", "kafka", "pubsub"], default=env("SINK", "stdout"))
    s.add_argument("--rate", type=float, default=float(env("RATE", "2")), help="events per second")
    s.add_argument("--count", type=int, default=int(env("COUNT", "0")), help="stop after N events; 0 runs forever")
    s.add_argument("--seed", type=int, default=int(env("SEED")) if env("SEED") else None)
    s.add_argument("--duplicates", type=float, default=float(env("DUPLICATES", "0")), help="share of events sent twice, e.g. 0.05")
    s.add_argument("--late", type=float, default=float(env("LATE", "0")), help="share of events delivered late, e.g. 0.05")
    s.add_argument("--schema", choices=["v1", "v2"], default=env("SCHEMA", "v1"))
    s.add_argument("--file", default=env("FILE", "events.jsonl"))
    s.add_argument("--http-url", default=env("HTTP_URL"))
    s.add_argument("--kafka-bootstrap", default=env("KAFKA_BOOTSTRAP", "localhost:9092"))
    s.add_argument("--kafka-topic", default=env("KAFKA_TOPIC", "ocean-events"))
    s.add_argument("--pubsub-topic", default=env("PUBSUB_TOPIC"))

    args = parser.parse_args(argv)

    if args.command == "batch":
        counts = batch.generate(args.out, date.fromisoformat(args.start), args.days, args.seed)
        print(f"Wrote {args.days} days to {args.out}/: " + ", ".join(f"{v} {k}" for k, v in counts.items()))
        return

    stream = EventStream(args.mode, args.seed, args.duplicates, args.late, args.schema)
    sink = make_sink(args)
    interval = 1 / args.rate if args.rate > 0 else 0
    sent = 0
    try:
        for event in stream:
            sink.send(event)
            sent += 1
            if args.count and sent >= args.count:
                break
            if interval:
                time.sleep(interval)
    except KeyboardInterrupt:
        pass
    finally:
        sink.close()


if __name__ == "__main__":
    main()
