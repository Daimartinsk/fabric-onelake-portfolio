# Fabric notebook — attach to the target Lakehouse as default.
#
# OPTIMIZE compacts small files written by frequent dataflow/notebook loads.
# VACUUM removes files no longer referenced by the Delta log.
# Run after ingestion and before materialisation (see pipelines/orchestrator.md).

from datetime import datetime
from pyspark.sql import functions as F

RETENTION_HOURS = 168          # 7 days — keep time travel for a week; don't go lower without a reason
EXCLUDE_PREFIXES = ("ops_",)   # operational log tables

tables = [
    t.name for t in spark.catalog.listTables()
    if t.tableType != "VIEW" and not t.name.startswith(EXCLUDE_PREFIXES)
]

results = []
for t in tables:
    start = datetime.utcnow()
    try:
        before = spark.sql(f"DESCRIBE DETAIL {t}").select("numFiles").first()[0]
        spark.sql(f"OPTIMIZE {t}")
        spark.sql(f"VACUUM {t} RETAIN {RETENTION_HOURS} HOURS")
        after = spark.sql(f"DESCRIBE DETAIL {t}").select("numFiles").first()[0]
        results.append((t, "OK", before, after, (datetime.utcnow() - start).seconds, None))
    except Exception as e:
        results.append((t, "FAILED", None, None, (datetime.utcnow() - start).seconds, str(e)[:500]))

log = spark.createDataFrame(
    results, "table string, status string, files_before long, files_after long, seconds int, error string"
).withColumn("run_at", F.current_timestamp())

log.write.format("delta").mode("append").saveAsTable("ops_maintenance_log")
display(log.orderBy(F.col("files_before").desc_nulls_last()))
