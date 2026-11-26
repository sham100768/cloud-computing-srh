# Workshop: one table, two ways

**Time:** about 80 minutes, on your own, in Cloud Shell, plus 10 minutes at the start of class. You need everything from session 7: the cluster, Kafka with its `vpc` listener, the Dataflow pipeline and the raw archive.

Today you build the executive side's table, **carrier reliability per day**: of the ocean shipments that arrived, how many reported a delay. You build it twice:

- **Lambda:** a Spark batch job on Dataproc reads the raw archive and computes it.
- **Kappa:** no batch job. Replay the whole Kafka log through the same streaming code as yesterday, and compute it from that.

Then you compare the two.

## 0. Before the lecture: start today's traffic (10 min)

Do this at the start of class, so traffic builds up while we talk.

```bash
cd ~/cloud-computing-srh && git pull upstream main
terraform version                              # should print Terraform v1.9.8
cd sessions/04-docker-and-kubernetes-on-gke/starter
terraform apply                                # node_count back to 1
$(terraform output -raw get_credentials)
```

Today's generator image is v3. Build and push it:

```bash
cd ~/cloud-computing-srh/event-generator
PROJECT_ID=$(gcloud config get-value project)
REPO=europe-west3-docker.pkg.dev/$PROJECT_ID/freight
docker build -t generator:v3 .
docker tag generator:v3 $REPO/generator:v3
docker push $REPO/generator:v3
```

A working push ends with a line containing `digest:`. If it stops with `connection refused`, run `docker push` again.

Start today's producers, two carrier feeds, once the Kafka pods are Running:

```bash
cd ~/cloud-computing-srh/sessions/08-spark-on-dataproc/starter/kafka
sed -i "s/PROJECT_ID/$PROJECT_ID/" producers.yaml
kubectl -n kafka get pods                       # wait for the freight-dual pods
kubectl apply -f producers.yaml
```

And start yesterday's pipeline again, in your Beam environment:

```bash
source ~/beam/bin/activate
cd ~/cloud-computing-srh/sessions/07-dataflow/starter/pipeline
./run-on-dataflow.sh
```

Its consumer group has run before, so it carries on from where it stopped yesterday: everything Kafka received since then reaches the archive too.

## 1. Stop the feeds and the live job (5 min)

After the lecture, stop the producers, so the Kafka log stops growing:

```bash
kubectl -n kafka scale deployment/ocean-producer deployment/partner-feed --replicas=0
```

Wait until the live job has caught up with the last of it. In a second tab, with yesterday's shortcuts:

```bash
B=freight-kafka-bootstrap:9092
kk() { kubectl -n kafka exec -i kafka-client -- /opt/kafka/bin/"$1" "${@:2}"; }
kk kafka-consumer-groups.sh --bootstrap-server $B --describe --group dataflow-live
```

When `LAG` is 0 on all three partitions, drain the job:

```bash
JOB=$(gcloud dataflow jobs list --region europe-west3 --status=active --format="value(id)")
gcloud dataflow jobs drain $JOB --region europe-west3
```

Now the raw archive holds everything in the Kafka log. Both ways of building the table start from the same events.

## 2. Create today's resources and the cluster (10 min)

```bash
PROJECT_ID=$(gcloud config get-value project)
cd ~/cloud-computing-srh/sessions/08-spark-on-dataproc/starter
cp terraform.tfvars.example terraform.tfvars   # set project_id
terraform init
terraform apply
```

It creates a service account for Spark, a bucket for its files, and the `freight.replay_events` table the Kappa path writes to.

Then the cluster: one machine, which deletes itself after 30 idle minutes.

```bash
gcloud dataproc clusters create freight-spark \
  --region europe-west3 \
  --single-node \
  --master-machine-type e2-standard-4 \
  --master-boot-disk-type pd-balanced \
  --master-boot-disk-size 50 \
  --image-version 2.2-debian12 \
  --max-idle 30m \
  --bucket $PROJECT_ID-dataproc \
  --service-account dataproc-worker@$PROJECT_ID.iam.gserviceaccount.com
```

It takes about 2 minutes. Your node uses 4 vCPUs and this cluster 4, which is your trial's limit: the Dataflow job has to be drained first.

## 3. Look at the archive with Spark (10 min)

```bash
./run-batch.sh --explore
```

The job reads every file in `gs://<project-id>-raw/events/` and prints the columns Spark found, how many messages there are, and a count per event type. The output appears in Cloud Shell; the full log is under **Dataproc → Jobs** in the console.

Read the columns carefully. You know this data, because you've been sending it for a week. Is everything there what you expected?

## 4. Write the reliability query (15 min)

Open `reliability.sql`. The two building blocks are done: `arrivals`, one row per shipment that arrived, and `delayed`, every shipment that ever reported a delay. Your TODO is the final `SELECT`: for each carrier and day, shipments arrived, shipments delayed, and the on-time share.

This one query builds the table both ways today: Spark runs it over the archive, and BigQuery over the replay. So it uses only SQL that both understand.

## 5. Run the batch path (10 min)

```bash
./run-batch.sh
```

The job prints its plan first. Find the lines that start with `Exchange`: each one is a shuffle, data moving between machines for your join and your `GROUP BY`. Then it writes `freight.carrier_reliability_batch` and prints the table.

When it's done, delete the cluster. It would delete itself after 30 idle minutes, but you need its CPUs for step 6:

```bash
gcloud dataproc clusters delete freight-spark --region europe-west3 --quiet
```

## 6. Build it again by replay (15 min)

The Kappa way: no batch job, no archive. Replay the whole Kafka log through yesterday's streaming code:

```bash
./run-replay.sh
```

It launches yesterday's pipeline with `--replay`: a new consumer group that starts at the first offset, reading Kafka only and writing to `freight.replay_events`. When the job is running, watch its group catch up:

```bash
kk kafka-consumer-groups.sh --bootstrap-server $B --describe --all-groups | grep replay
```

When the lag is 0, the replay is done. Drain it the same way as in step 1, then run the same query in BigQuery:

```bash
./build-stream-table.sh
```

## 7. Compare (10 min)

Run `compare.sql` in the BigQuery console: both tables side by side, carrier by carrier and day by day.

Do they match? Where they don't, find out why. You have the raw archive, the replayed events and the Spark output from step 3 to work with.

## Checkpoint

`docs/lambda-vs-kappa.md` in your fork, one page:

- How long each path took to build the table, roughly, and what it cost to run
- How much code each path needs you to maintain
- Whether the two tables matched, and if not, why
- Which one you'd keep for your launch customer, and why

```bash
cd ~/cloud-computing-srh
cp sessions/08-spark-on-dataproc/starter/reliability.sql docs/
git add docs/
git commit -m "Session 8: one table, two ways"
git push origin main
```

## Stretch

- **The Spark UI.** Create the cluster with `--enable-component-gateway`, run the job again, and open **Web interfaces → Spark History Server** on the cluster page. Find the stage with the shuffle.
- **Read less.** The archive is one folder. How would you lay it out so a job for one day reads one day's files?
- **Fix it.** If your tables didn't match, change the step that caused it, rebuild, and compare again.

## Teardown

```bash
gcloud dataproc clusters list --region europe-west3        # empty
gcloud dataflow jobs list --region europe-west3 --status=active   # empty
cd ~/cloud-computing-srh/sessions/04-docker-and-kubernetes-on-gke/starter
terraform apply -var node_count=0
```

Keep the tables, the archive and the Kafka disks: tomorrow uses them.

## If something goes wrong

- **Creating the cluster fails with `Permission 'dataproc.nodeGroups.create' denied`:** `terraform apply` only just switched on Dataproc, and its permissions take a few minutes to apply. Delete the failed cluster with `gcloud dataproc clusters delete freight-spark --region europe-west3 --quiet`, wait two minutes, and create it again.
- **`Insufficient 'CPUS' quota` creating the cluster:** something else is still running. Check `gcloud dataflow jobs list --region europe-west3 --status=active` and drain it.
- **`run-batch.sh` says the cluster isn't found:** it deleted itself after 30 idle minutes. Create it again.
- **The job fails with `Permission denied` on BigQuery:** today's `terraform apply` didn't finish, or the cluster was created without `--service-account`.
- **The job fails on your SQL:** the error points at the line. Spark is stricter about `GROUP BY` than you might expect: every column you select that isn't counted must be in it.
- **The replay's lag doesn't go down:** check the job is running in the Dataflow console. The replay reads with a new group each time you launch it.
- **`build-stream-table.sh` says `replay_events` is empty:** the replay hasn't written yet. Give it a few minutes after the worker starts.
- **The producers don't start:** `kubectl -n kafka describe pod -l app=partner-feed`. `ImagePullBackOff` means the v3 image wasn't pushed.
