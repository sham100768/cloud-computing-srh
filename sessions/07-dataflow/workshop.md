# Workshop: the speed layer on Dataflow

**Time:** about 80 minutes, on your own, in Cloud Shell. You need your GKE cluster and Kafka from sessions 4 and 5, and the `air-events` topic and webhook from session 6.

Today you finish the speed layer. One Beam pipeline reads ocean events from Kafka and air events from Pub/Sub, and writes three things: an archive of every message exactly as it arrived, as files in your raw bucket; every good event, once, into a live table; and departures per port per 5 minutes.

Steps 1 and 2 both wait on things that take a few minutes. Start them in two Cloud Shell tabs and let them run side by side.

## 1. Wake the cluster and open Kafka to your VPC (10 min)

Get today's material, check Terraform, and bring the node back:

```bash
cd ~/cloud-computing-srh && git pull upstream main
terraform version                              # should print Terraform v1.9.8
cd sessions/04-docker-and-kubernetes-on-gke/starter
terraform apply                                # node_count goes back to 1
$(terraform output -raw get_credentials)
kubectl -n kafka get pods                      # wait until the freight-dual pods are Running
```

If `terraform version` prints installation instructions, follow tip 3 in the [Cloud Shell tips](../../setup/gcp.md#cloud-shell-tips) first.

Dataflow's workers are virtual machines in your VPC, outside the cluster, so they can't use `freight-kafka-bootstrap:9092`. Give Kafka a second listener on the node's internal IP:

```bash
cd ~/cloud-computing-srh/sessions/07-dataflow/starter/kafka
./open-kafka-to-vpc.sh
```

Strimzi restarts the three brokers one at a time to add it, which takes 3 to 5 minutes. Watch it in another tab with `kubectl -n kafka get pods --watch`: the producer keeps writing throughout, for the same reason it survived a broker dying on Wednesday. The script ends by printing an address like `10.156.0.12:31094`.

## 2. Install Beam and create today's resources (5 min, then waiting)

In a second tab. Beam is a big install, so start it now:

```bash
cd ~/cloud-computing-srh/sessions/07-dataflow/starter/pipeline
python3 -m venv ~/beam
source ~/beam/bin/activate
pip install -r requirements.txt               # 1 to 2 minutes
```

While that runs, in a third tab, apply today's Terraform:

```bash
cd ~/cloud-computing-srh/sessions/07-dataflow/starter
cp terraform.tfvars.example terraform.tfvars   # set project_id
terraform init
terraform apply
```

Read the plan. It creates:

- a service account, `dataflow-worker`, that may write to your dataset and raw bucket and read one subscription, and nothing else
- a bucket, `<project-id>-dataflow`, where Dataflow stages your code
- a subscription, `air-events-dataflow`, on Monday's topic, so the pipeline gets its own copy of every air event
- two tables, `freight.live_events` and `freight.departures_by_port`, and a view, `freight.live_status`: the latest event for every shipment
- a firewall rule that lets machines inside your VPC reach Kafka's port, and nothing outside it

## 3. Run the pipeline on a file (10 min)

Back in the Beam tab, once `pip` has finished. Open `pipeline.py` and read the docstring at the top: it's the graph from the slides. Then run it on the sample file, an hour of ocean events:

```bash
python pipeline.py --source file
```

It crashes. Scroll up to the first error: a `JSONDecodeError` on a line that was cut off in transit. Real carrier feeds have lines like that, and a streaming pipeline that crashes on one bad message retries it for ever. That's your first TODO.

## 4. Finish the three TODOs (15 min)

All three are in `transforms.py`, and each has tests:

```bash
python -m pytest tests -q
```

1. **`parse_event`:** return `None` for anything unusable, instead of raising.
2. **`event_timestamp`:** return the time the event happened, not the time now.
3. **`dedupe_key`:** return the key a duplicate shares with its original.

Run the tests after each one. When all 13 pass, run the pipeline on the file again:

```bash
python pipeline.py --source file
ls out/
```

It prints how many events reached `live_events`, then departures per port per 5-minute window, and writes the archive to `out/`: all 403 lines, bad ones included. Think about the second TODO: if `event_timestamp` returned the time now, every departure in the file would land in one window, because the whole file is read in under a second.

## 5. Launch it on Dataflow (10 min)

```bash
./run-on-dataflow.sh
```

The script finds Kafka's internal address, then launches the job with one `e2-standard-2` worker. Launching takes about 4 minutes: it packages your code, uploads it and hands the job to Dataflow, then prints `Submitted` and gives you the prompt back. The job keeps running on Dataflow after that. The first time, it also downloads Kafka's connector, which runs in Java: that's normal.

Open **Dataflow → Jobs → freight-live** in the console. The graph is the same one you read in step 3, box for box. It takes 3 to 5 minutes before the worker starts and the boxes show elements going through.

The first time it runs, its consumer group is new, so it starts at the beginning of the Kafka log: everything since Wednesday's workshop goes through first, then it keeps up with new events. That's a replay, and it's what Kafka's log is for. Next time the job starts, the group carries on where it stopped.

## 6. Feed it and query it (10 min)

Ocean events are already flowing: Wednesday's producer started again with the cluster. Check it:

```bash
kubectl -n kafka logs deployment/ocean-producer --tail=3
```

Send some air events through Monday's webhook:

```bash
cd ~/cloud-computing-srh/event-generator
URL=$(gcloud app browse --no-launch-browser)
python3 -m generator stream --mode air --sink http --http-url $URL/events --rate 2 --count 300
```

Then query the live tables in the BigQuery console:

```sql
-- How fresh is the live table? Compare with your launch customer's target.
-- Right after launch it's catching up on the log, so give it a few minutes.
SELECT TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(event_time), SECOND) AS seconds_behind
FROM freight.live_events;

-- The ops view: shipments whose latest event is a delay.
SELECT shipment_id, mode, carrier, location, delay_hours, event_time
FROM freight.live_status
WHERE event_type = 'DELAYED'
ORDER BY event_time DESC
LIMIT 10;

-- Departures per port, per 5 minutes of event time.
SELECT window_start, port, departures
FROM freight.departures_by_port
ORDER BY window_start DESC, departures DESC
LIMIT 20;
```

`departures_by_port` fills much more slowly than `live_events`: a window is only written once the watermark has passed its end. Expect the first rows about 15 minutes after launch. The pipeline remembers each event ID for 10 minutes to catch duplicates, and the watermark waits for that memory too.

## 7. Read the watermark (5 min)

On the job page, open **Job metrics**. Find **data freshness** and **system latency**, and look at both for a minute.

- Data freshness is how far behind real time the watermark is: the age of the oldest event the pipeline is still waiting for.
- System latency is how long an event spends inside the pipeline.

Which of the two is closer to `seconds_behind` from step 6, and why?

## 8. Check the archive (5 min)

```bash
PROJECT_ID=$(gcloud config get-value project)
gcloud storage ls gs://$PROJECT_ID-raw/events/ | head
gcloud storage cat $(gcloud storage ls gs://$PROJECT_ID-raw/events/ | head -1) | head -2
```

A few files per 5 minutes of arrival, one message per line, exactly as it came in: duplicates and broken lines included. This is your lake. Whatever the pipeline drops or gets wrong, the original messages are still here, and tomorrow's Spark job reads them.

## Checkpoint

Commit your pipeline and a short note to your fork:

```bash
cd ~/cloud-computing-srh
mkdir -p docs
cp sessions/07-dataflow/starter/pipeline/transforms.py docs/
# write docs/dataflow.md
git add docs/
git commit -m "Session 7: speed layer on Dataflow"
git push origin main
```

`docs/dataflow.md`, half a page:

- What your pipeline does, box by box, in your own words
- Your launch customer's freshness target, and the `seconds_behind` you measured
- One thing you'd change in the pipeline for your launch customer, and why

## Stretch

- **Sliding windows.** Add a second count with `window.SlidingWindows(30 * 60, 5 * 60)`: departures in the last 30 minutes, updated every 5. What's the difference in the output?
- **Session windows.** How long does a container spend between `GATE_IN` and `LOADED`? Key by `shipment_id`, use `window.Sessions(...)`, and think about what gap to choose.
- **Lateness.** The departures count uses the default allowed lateness of zero. What happens to an event that arrives after its window has been counted? Find the answer in the Beam docs before you change anything.

## Teardown

A streaming job bills for its worker every hour it runs. **Drain it**, which finishes the work in flight and then stops, and scale the cluster to zero:

```bash
JOB=$(gcloud dataflow jobs list --region europe-west3 --status=active --format="value(id)")
gcloud dataflow jobs drain $JOB --region europe-west3
cd ~/cloud-computing-srh/sessions/04-docker-and-kubernetes-on-gke/starter
terraform apply -var node_count=0
```

Draining takes 10 to 15 minutes, because the job finishes its open windows and its 10-minute duplicate check first. Check that nothing is still running before you leave:

```bash
gcloud dataflow jobs list --region europe-west3 --status=active
gcloud compute instances list
```

Both should be empty. Keep today's tables, subscription and archive: tomorrow uses all three.

## If something goes wrong

- **`run-on-dataflow.sh` fails on `setup.py sdist`, or says there's no module named `setuptools`:** run `pip install -r requirements.txt` again in the active environment; it installs `setuptools`.
- **`pip install` fails on a package with no wheel:** check `python3 --version`. Beam needs Python 3.9 to 3.12. If Cloud Shell's is newer, create the environment with `python3.12 -m venv ~/beam` instead.
- **`open-kafka-to-vpc.sh` times out:** read the operator's log, `kubectl -n kafka logs deployment/strimzi-cluster-operator --tail=50`. Run the script again: it doesn't add the listener twice.
- **`run-on-dataflow.sh` says Kafka has no vpc listener:** run `open-kafka-to-vpc.sh` first, and wait until it prints the address.
- **Launching fails on `java` or the expansion service:** check `java -version`. Kafka's connector runs in Java, and Cloud Shell has it; on your own laptop you need Java 11 or newer.
- **The job is running but `live_events` stays empty:** open the job's **Logs**. A timeout to Kafka means the worker can't reach the node: check the firewall rule exists with `gcloud compute firewall-rules list`. `PermissionDenied` on BigQuery means today's `terraform apply` didn't finish.
- **Quota exceeded for CPUS:** the trial allows about 8 vCPUs in Frankfurt. Your node uses 4 and the worker 2. Check `gcloud compute instances list` for anything else.
- **`departures_by_port` is empty but `live_events` isn't:** wait 15 minutes from launch. A window is written only after the watermark passes its end, and the watermark waits for the 10-minute duplicate check.
