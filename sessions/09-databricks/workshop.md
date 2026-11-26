# Workshop: your freight data in a lakehouse

**Time:** about 80 minutes, on your own, in Cloud Shell and Databricks Free Edition. You need yesterday's two reliability tables and your raw archive. Nothing on Google Cloud needs to run today: leave the cluster at zero nodes.

Today the same data goes into a different kind of platform. You'll refine your raw events in three stages, bronze, silver and gold, as Delta tables in Databricks; build the reliability table a third time; undo a mistake with time travel; and train a first model.

If you haven't signed up for Databricks Free Edition yet, do it first: [setup/databricks.md](../../setup/databricks.md).

## 1. Export your data from Google Cloud (10 min)

```bash
cd ~/cloud-computing-srh && git pull upstream main
cd sessions/09-databricks/starter
./export.sh
```

It joins your whole raw archive into one compressed file and saves yesterday's two tables as CSV, all in `~/session-09`. Then download the three files to your laptop:

```bash
cloudshell download ~/session-09/events.jsonl.gz
cloudshell download ~/session-09/carrier_reliability_batch.csv
cloudshell download ~/session-09/carrier_reliability_stream.csv
```

Your browser asks where to save each one. You need the notebook too: download `freight-lakehouse.ipynb` from the starter folder in the course repo on GitHub.

## 2. Into Databricks (10 min)

1. In Databricks, open **Catalog**, then **workspace → default**. Choose **Create → Volume**, name it `freight`, and create it. A volume is a folder for files, inside the catalog.
2. Open the volume, choose **Upload to this volume**, and upload the three files.
3. Open **Workspace**, choose **Import**, and import `freight-lakehouse.ipynb`.
4. Open the notebook and connect it to **Serverless** compute at the top right.

Run the first cell. It lists the three files in your volume. If it says the path doesn't exist, check the volume's name and change `VOLUME` in the cell.

## 3. Bronze (5 min)

Run the cells in step 2 of the notebook. Bronze is your raw archive as a Delta table, unchanged: every message, good or bad.

Read the schema and the counts per event type before you go on. Silver depends on what you find here.

## 4. Silver (15 min)

Silver is the version you'd let other people use: one row per real event, with proper types.

1. **TODO 1:** keep only rows with everything the gold table needs.
2. **TODO 2:** keep one row per `event_id`.

The cell after it compares bronze rows, silver rows and distinct events. Silver rows and distinct events should be equal. Think about what you've thrown away between bronze and silver, and whether all of it deserved to go.

## 5. Gold, and a third comparison (10 min)

**TODO 3:** paste your final `SELECT` from yesterday's `reliability.sql` into the gold cell. It reads a view called `events`, as in BigQuery and Spark, so nothing else changes.

Then run the comparison: yesterday's batch table, yesterday's replay table, and today's gold table, side by side. Which of the three would you show your launch customer's exec?

## 6. Time travel (5 min)

Run step 5 of the notebook. You overwrite silver with one carrier's events, on purpose, then look at the table's history. Find the version before your mistake, put its number in `before`, and run the cell: it reads the old version, then restores it.

A plain Parquet folder can't do this. The transaction log is what turns files into a table.

## 7. A first model (15 min)

Step 6 builds one row per shipment that arrived, with what was known when it was booked and whether it reported a delay. The first run trains a model on the lane only.

**TODO 4:** train a second run that also knows the carrier. Then open **Experiments** in the left bar, find this notebook's experiment, and compare the two runs.

Look at `always_on_time_accuracy`: the score of a "model" that always says *on time*. How do your two runs compare with it? And who could use the second model: a shipper choosing between carriers, or an ops team watching shipments already on the water?

## Checkpoint

1. In the notebook, **File → Export → IPython Notebook**.
2. Commit it to your fork, with a short note:

```bash
cd ~/cloud-computing-srh
mkdir -p docs
# copy the exported notebook to docs/freight-lakehouse.ipynb, and write docs/week-3.md
git add docs/
git commit -m "Session 9: lakehouse"
git push origin main
```

Upload the notebook to Cloud Shell with **More → Upload**, or add it on GitHub in your browser.

`docs/week-3.md`, one page. This is the end of week 3:

- Both your versions, Lambda and Kappa: what each one runs on, and that both work
- What yesterday's comparison showed, and what today's gold table adds
- Where a lakehouse would or wouldn't fit your launch customer, next to BigQuery

## Stretch

- **A dashboard.** In Databricks, open **SQL Editor**, query `gold_carrier_reliability`, and add the result to a new dashboard.
- **A better model.** What else was known at booking time that might predict a delay? Add it to the shipment query and train again.
- **Partitioning.** Rewrite silver with `PARTITIONED BY (DATE(event_time))`. What does it change for a query on one day?

## Teardown

Databricks Free Edition doesn't bill. On Google Cloud, check that nothing is still running from this week:

```bash
gcloud dataflow jobs list --region europe-west3 --status=active
gcloud dataproc clusters list --region europe-west3
gcloud compute instances list
```

All three should be empty.

## If something goes wrong

- **`gcloud storage cat` says no URLs matched:** the raw archive is empty. Check `gcloud storage ls gs://$PROJECT_ID-raw/events/`: the files come from session 7's pipeline.
- **The CSV files are empty:** yesterday's tables weren't built. Check them in the BigQuery console; you can carry on without the comparison.
- **`cloudshell download` does nothing:** use **More → Download** in Cloud Shell's menu, and type the path.
- **The volume path doesn't exist:** the catalog may not be called `workspace` in your account. Open **Catalog**, find the volume, and copy its path from the volume's page into `VOLUME`.
- **`QUALIFY` gives a syntax error:** it goes after `WHERE`, at the very end of the query.
- **`toPandas()` is slow:** it pulls every shipment onto one machine. That's fine for a few thousand rows; it's also why the cell keeps one row per shipment, not per event.
- **MLflow says no experiment:** run the training cell again. The first run creates the notebook's experiment.
