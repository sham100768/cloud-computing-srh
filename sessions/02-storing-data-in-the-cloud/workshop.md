# Workshop: freight data into BigQuery

**Time:** about 80 minutes, in Cloud Shell, in your own project. You need Monday's `<project-id>-raw` bucket.

## 1. Generate a month of freight data

```bash
cd ~/cloud-computing-srh && git pull
cd event-generator
python3 -m generator batch --start 2026-10-01 --days 31 --out ~/freight-data
```

You get three datasets, one CSV per day: `rates`, `schedules` and `bookings`. Open one and look at the columns:

```bash
head -5 ~/freight-data/bookings/date=2026-10-01/bookings.csv
```

Everyone uses the default seed, so everyone has exactly the same data.

## 2. Upload it to your raw bucket

```bash
PROJECT_ID=$(gcloud config get-value project)
gcloud storage cp -r ~/freight-data/* gs://${PROJECT_ID}-raw/
gcloud storage ls gs://${PROJECT_ID}-raw/rates/ | head
```

Open the bucket in the console. The `date=` "folders" are just part of each object's key.

## 3. Create the tables with Terraform

```bash
cd ~/cloud-computing-srh/sessions/02-storing-data-in-the-cloud/starter
cp terraform.tfvars.example terraform.tfvars   # set project_id
terraform init
terraform plan
terraform apply
```

This creates a `freight` dataset with three tables: `rates_unpartitioned`, `rates` (partitioned by date, clustered by lane and carrier) and `bookings`.

**Your turn:** `main.tf` has a TODO for a `schedules` table. Write it, then `terraform apply` again.

## 4. Load the files

```bash
./load.sh
```

It loads every CSV from your bucket into its table and prints the row counts. You should see 14,136 rates, 1,140 bookings and 1,261 schedules.

## 5. Dry-run and compare

Run the same query against both rates tables, as a dry run. It tells you the bytes it would scan, without running it.

```bash
bq query --use_legacy_sql=false --dry_run \
  "SELECT trade_lane, rate_usd FROM freight.rates_unpartitioned WHERE rate_date = '2026-10-15'"

bq query --use_legacy_sql=false --dry_run \
  "SELECT trade_lane, rate_usd FROM freight.rates WHERE rate_date = '2026-10-15'"
```

How many times fewer bytes does the partitioned table scan? Now try `SELECT *` instead of the two columns. What changes?

## Checkpoint: three exec questions in SQL

Write each query in the BigQuery console, and dry-run it before you run it.

1. **What did shippers spend per trade lane in October?** Use `bookings`. Highest first.
2. **Which ocean carrier had the cheapest average spot rate for a 40HC on Asia-North Europe in October?** Use `rates`.
3. **What share of each ocean carrier's sailings arrived no more than 24 hours late?** Use `schedules`. Hint: `DATETIME_DIFF(actual_arrival, planned_arrival, HOUR)`.

Look at your answers to 2 and 3 together. What would you tell a shipper choosing a carrier?

## Stretch

- **Lifecycle rule.** In session 1's `main.tf`, add a `lifecycle_rule` to the raw bucket that moves objects to `NEARLINE` after 30 days. Run `terraform plan` in the session 1 folder: why does Terraform change the existing bucket instead of creating a new one?
- **Join.** Using `bookings.schedule_id` and `schedules.schedule_id`, find each shipper's share of shipments that arrived late.
- **Formats.** Export `rates` to Parquet in your bucket with `bq extract --destination_format=PARQUET`, and compare its size with the CSVs.
- **A dashboard for a real user.** Pick one shipper from `bookings`. You're their procurement manager, and before next quarter's carrier negotiations you want one page that answers:
  - Where is our freight money going?
  - Are we paying more than we need to?
  - Can we trust the carriers we book?

  Build it in [Data Studio](https://datastudio.google.com) (formerly Looker Studio): free, in the browser, and it reads your BigQuery tables directly. Deciding which tables, columns and charts answer each question is the task. If a measure you need isn't in the data, create it. Then open **Job history** in BigQuery and find the queries your dashboard ran: every chart queries on every refresh. What would make your page cheaper to run?

## Teardown

Nothing today bills by the hour, and this much data stays inside the free tier. Keep the tables: Friday builds on them.

## If something goes wrong

- **`Not found: Dataset`** in `load.sh`: run `terraform apply` first, and check `gcloud config get-value project` is your project.
- **Location mismatch** when loading: the dataset and bucket must be in the same region. Both default to `europe-west3`.
- **`Already Exists`** in Terraform: someone created the table by hand. Delete it in the console, or ask me about `terraform import`.
