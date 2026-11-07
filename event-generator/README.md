# Event generator

This tool makes the freight data you build your platform on. It has two modes:

- **Batch** writes daily files of freight rates, schedules and bookings. You use it from session 2.
- **Stream** sends live shipment events, one at a time. You use it from session 4.

Every carrier, shipper and price is invented. The port codes (UN/LOCODE) and airport codes (IATA) are real, but nothing else is real market data.

You need Python 3.10 or newer and nothing else. Cloud Shell already has it.

## Generate your files

These steps run in **Cloud Shell**: open the Google Cloud console and click the `>_` icon, top right.

**1. Get the course repo.** Skip this if you already cloned it in session 1.

```bash
git clone https://github.com/sham100768/cloud-computing-srh.git
```

If you already have it, update it instead:

```bash
cd ~/cloud-computing-srh && git pull
```

**2. Go to the generator folder.**

```bash
cd ~/cloud-computing-srh/event-generator
```

The commands below only work from this folder.

**3. Generate 30 days of data.**

```bash
python3 -m generator batch --start 2026-10-01 --days 30 --out data
```

It finishes in a few seconds and prints:

```
Wrote 30 days to data/: 13680 rates, 1216 schedules, 1102 bookings
```

**4. Look at what you made.**

```bash
ls data
ls data/rates | head -3
head -3 data/rates/date=2026-10-01/rates.csv
```

You get three folders with one CSV per day in each, 90 files and about 2 MB in total:

```
data/
  rates/date=2026-10-01/rates.csv
  rates/date=2026-10-02/rates.csv
  ...
  schedules/date=2026-10-01/schedules.csv
  ...
  bookings/date=2026-10-01/bookings.csv
  ...
```

The `date=` folder names are a convention BigQuery and Spark understand: they read the date from the path, so a query for one day only needs to read that day's files.

**5. Upload the files to your bucket.** You do this in session 2. It copies everything into the `-raw` bucket you created with Terraform in session 1:

```bash
PROJECT_ID=$(gcloud config get-value project)
gcloud storage cp --recursive data "gs://${PROJECT_ID}-raw/"
gcloud storage ls "gs://${PROJECT_ID}-raw/data/"
```

### Everyone gets the same data

The files depend only on the seed and the date. Run the same command as your neighbour and you get identical files, so your query results should match theirs, which makes it easy to check your work.

To change what you generate:

| You want | Add |
|---|---|
| A different time period | `--start 2026-07-01 --days 90` |
| A different market (your own prices and bookings) | `--seed 7`, or any number |
| Files somewhere else | `--out my-folder` |

Running the command again overwrites any day that already exists, so it is safe to repeat.

## What's in the files

| Dataset | One row is | Key columns |
|---|---|---|
| `rates` | a carrier's price on one lane, for one container type or weight break, contract type and day | `rate_date`, `mode`, `contract_type`, `origin`, `destination`, `carrier_code`, `equipment`, `weight_break`, `rate_usd`, `unit` |
| `schedules` | a sailing or flight planned to leave that day, with what actually happened | `schedule_id`, `carrier_code`, `planned_departure`, `planned_arrival`, `actual_departure`, `actual_arrival` |
| `bookings` | one shipment a shipper booked that day | `shipment_id`, `shipper_id`, `carrier_code`, `quantity`, `unit_rate_usd`, `total_cost_usd`, `schedule_id` |

A few things to know:

- **Ocean and air are in the same files.** Use the `mode` column (`OCEAN` or `AIR`). Ocean rows fill `equipment` (`20DC`, `40DC`, `40HC`) and leave `weight_break` empty. Air rows do the opposite (`+100`, `+500`, `+1000` kg).
- **Prices are in USD.** Ocean prices are per container, air prices per kg, as the `unit` column says.
- **Ocean rates come in two contract types.** `spot` changes daily. `long_term` is fixed for each quarter and usually cheaper.
- **Bookings join to schedules.** `bookings.schedule_id` matches `schedules.schedule_id`, so you can work out which shipments arrived late. Ocean bookings sail at least three days after they're booked, so bookings near the end of your period can point to a departure you didn't generate. Generate a couple of extra weeks if you need those schedules too.

Some patterns are built into the market for you to find. Carriers differ in price and reliability, shippers choose carriers based on what they care about, and prices move with the seasons.

## Live events

The stream sends one shipment event at a time, as a carrier's live feed would. Try it in Cloud Shell:

```bash
python3 -m generator stream --sink stdout --rate 2 --count 20
```

This prints 20 events, two per second. An event looks like this:

```json
{"schema_version": 1, "event_id": "0994940e-...", "shipment_id": "LIVE-SHP06-000050",
 "shipper_id": "SHP06", "mode": "OCEAN", "event_type": "DEPARTED",
 "event_time": "2026-11-30T16:45:02+00:00", "location": "DEHAM", "carrier": "BLC",
 "origin": "DEHAM", "destination": "USNYC", "trade_lane": "Transatlantic"}
```

Ocean shipments move through BOOKED, GATE_IN, LOADED, DEPARTED, ARRIVED, DISCHARGED and GATE_OUT. Air shipments move through BOOKED, RECEIVED, DEPARTED, ARRIVED and DELIVERED. Any shipment can also report DELAYED, with `delay_hours`.

To save events to a file instead, one JSON object per line:

```bash
python3 -m generator stream --sink file --file events.jsonl --count 500 --rate 0
```

`--rate 0` sends as fast as possible.

### Options

Each option can also be set with an environment variable, which is how you configure it in a container.

| Option | Environment variable | What it does |
|---|---|---|
| `--mode ocean\|air\|both` | `MODE` | which shipments to simulate |
| `--sink stdout\|file\|http\|kafka\|pubsub` | `SINK` | where events go |
| `--rate 2` | `RATE` | events per second; 0 means as fast as possible |
| `--count 0` | `COUNT` | stop after N events; 0 runs until you press Ctrl+C |
| `--seed 7` | `SEED` | the same seed gives the same stream |
| `--file events.jsonl` | `FILE` | output file for the file sink |
| `--http-url URL` | `HTTP_URL` | webhook to POST each event to |
| `--kafka-bootstrap host:9092` | `KAFKA_BOOTSTRAP` | Kafka broker |
| `--kafka-topic ocean-events` | `KAFKA_TOPIC` | Kafka topic; messages are keyed by `shipment_id` |
| `--pubsub-topic projects/P/topics/T` | `PUBSUB_TOPIC` | Pub/Sub topic |
| `--duplicates 0.05` | `DUPLICATES` | share of events sent twice |
| `--late 0.05` | `LATE` | share of events that arrive late and out of order |
| `--schema v1\|v2` | `SCHEMA` | the event format; v2 renames fields and adds a new event type |

The last three make the stream behave like a real carrier feed. You switch them on in later sessions to test how your pipeline copes.

The Kafka and Pub/Sub sinks need two extra packages. Install them once, from this folder:

```bash
pip install -r requirements-sinks.txt
```

## In a container

You use this from session 4. Build the image once from this folder:

```bash
docker build -t event-generator .
```

Stream ten events:

```bash
docker run --rm -e RATE=1 -e COUNT=10 event-generator
```

To generate batch files, mount a folder so the files end up on your machine. Without `-v`, they stay inside the container and disappear when it stops:

```bash
mkdir -p data
docker run --rm -v "$PWD/data:/data" event-generator batch --days 7 --out /data
```

## If something goes wrong

- **`No module named generator`:** you're in the wrong folder. Run `cd ~/cloud-computing-srh/event-generator` first.
- **`python3: command not found`** on your own laptop: install Python 3.10 or newer, or use Cloud Shell.
- **Your numbers don't match your neighbour's:** check you both used the same `--seed` and `--start`.
- **`Kafka sink needs kafka-python`** or **`Pub/Sub sink needs google-cloud-pubsub`:** run `pip install -r requirements-sinks.txt`.
- **`Permission denied` when uploading to the bucket:** check `gcloud config get-value project` is your own project.

## Tests

For changes to the generator itself:

```bash
python3 -m unittest -v
```
