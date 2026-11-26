"""The Lambda batch path: carrier reliability from the raw archive, with Spark.

Submitted to your Dataproc cluster by ../run-batch.sh. Two modes:

  --explore   print what's in the archive, and stop
  (default)   run reliability.sql over it and write the result to BigQuery
"""

import argparse

from pyspark import SparkFiles
from pyspark.sql import SparkSession

parser = argparse.ArgumentParser()
parser.add_argument("--archive", required=True, help="gs://<project>-raw/events/")
parser.add_argument("--table", required=True, help="<project>.freight.carrier_reliability_batch")
parser.add_argument("--explore", action="store_true")
args = parser.parse_args()

spark = SparkSession.builder.appName("carrier-reliability").getOrCreate()

# Every file in the archive, one JSON message per line. Spark works out the
# columns from the data itself. A line that isn't valid JSON lands in a
# column called _corrupt_record instead of failing the job.
raw = spark.read.json(args.archive)

if args.explore:
    print("\n=== The columns Spark found in the archive ===")
    raw.printSchema()
    print(f"=== {raw.count()} messages ===")
    raw.groupBy("mode", "event_type").count().orderBy("mode", "event_type").show(30, truncate=False)
    spark.stop()
    raise SystemExit

# Ocean only: the replay reads Kafka, which only carries ocean events.
raw.where("mode = 'OCEAN'").createOrReplaceTempView("events")

with open(SparkFiles.get("reliability.sql")) as f:
    result = spark.sql(f.read())

# Nothing has run yet: Spark has only built a plan. explain() prints it.
# Look for Exchange: that's a shuffle, data moving between machines.
print("\n=== The plan ===")
result.explain()

# write() is an action, so this is where the work happens.
(result.write.format("bigquery")
    .option("table", args.table)
    .option("writeMethod", "direct")
    .mode("overwrite")
    .save())

print(f"\n=== Wrote {result.count()} rows to {args.table} ===")
result.orderBy("carrier", "arrival_date").show(50, truncate=False)
spark.stop()
