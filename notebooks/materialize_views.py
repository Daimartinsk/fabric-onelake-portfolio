# Fabric notebook — attach to the target Lakehouse as default.
#
# Materialises business views (vw_*) into physical Delta tables (tb_*).
# Views remain the single source of business logic; this notebook only
# persists their result so semantic models read precomputed data instead of
# recomputing joins/KPIs on every query.
#
# Runs as a step in the orchestrating Data Pipeline, after ingestion.

from datetime import datetime
from pyspark.sql import functions as F

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
VIEWS = [
    "vw_Consolidated",
    "vw_UnitA",
    "vw_UnitA_WorkingDays",
    "vw_UnitA_KPI_Monthly",
    "vw_UnitA_Forecasts",
    "vw_UnitB",
    "vw_UnitB_WorkingDays",
    "vw_UnitB_Forecasts",
    "vw_IndividualOrders",
]

# Columns that arrive as text from the source API and occasionally contain
# invalid values. Converting in Spark returns NULL instead of failing the load.
DATE_COLUMNS = {
    # "vw_UnitA": {"OrderDate": "yyyy-MM-dd"},
}

FAIL_PIPELINE_ON_ERROR = True  # surface failures to the pipeline instead of "succeeded with errors"


def target_name(view: str) -> str:
    return "tb_" + view[len("vw_"):] if view.startswith("vw_") else f"tb_{view}"


def read_view(view: str):
    """Views live on the SQL analytics endpoint. Read through the Lakehouse SQL."""
    return spark.sql(f"SELECT * FROM {view}")


def clean_dates(df, view: str):
    for col_name, fmt in DATE_COLUMNS.get(view, {}).items():
        df = df.withColumn(col_name, F.to_date(F.col(col_name).cast("string"), fmt))
    return df


results = []
for view in VIEWS:
    tgt = target_name(view)
    start = datetime.utcnow()
    try:
        df = clean_dates(read_view(view), view)
        (
            df.withColumn("_materialised_at", F.current_timestamp())
              .write.format("delta")
              .mode("overwrite")
              .option("overwriteSchema", "true")
              .saveAsTable(tgt)
        )
        rows = spark.table(tgt).count()
        results.append((view, tgt, "OK", rows, (datetime.utcnow() - start).seconds, None))
    except Exception as e:  # keep going, report at the end
        results.append((view, tgt, "FAILED", None, (datetime.utcnow() - start).seconds, str(e)[:500]))

log = spark.createDataFrame(
    results, "view string, target string, status string, rows long, seconds int, error string"
).withColumn("run_at", F.current_timestamp())

log.write.format("delta").mode("append").saveAsTable("ops_materialisation_log")
display(log)

failed = [r for r in results if r[2] == "FAILED"]
if failed and FAIL_PIPELINE_ON_ERROR:
    raise RuntimeError(
        "Materialisation failed for: " + ", ".join(f"{v} ({err})" for v, _, _, _, _, err in failed)
    )
