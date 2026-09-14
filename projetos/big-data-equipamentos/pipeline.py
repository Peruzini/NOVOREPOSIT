"""Batch analítico de demonstração. Todos os dados são sintéticos."""
import argparse
import json
import time
from pathlib import Path

from pyspark.sql import SparkSession, Window, functions as F

RAW_SCHEMA = """event_id string, equipment_id string, event_time string,
liters string, operating_minutes string, price_cents_per_liter string,
ingest_sequence long"""

def equipment_dimension(spark):
    return (
        spark.range(1000).withColumnRenamed("id", "equipment_id")
        .withColumn("unit", F.concat(F.lit("Unidade "), (F.col("equipment_id") % 4 + 1).cast("string")))
        .withColumn("equipment_type", F.when(F.col("equipment_id") % 3 == 0, "Caminhao")
                    .when(F.col("equipment_id") % 3 == 1, "Escavadeira").otherwise("Carregadeira"))
        .withColumn("reference_lph", F.when(F.col("equipment_id") % 3 == 0, 90)
                    .when(F.col("equipment_id") % 3 == 1, 50).otherwise(70))
    )

def generate(spark, rows, partitions, seed=42):
    """Expressões nativas: nenhum loop Python nem lista de eventos no driver."""
    base = spark.range(rows, numPartitions=partitions)
    target = (F.when(F.col("id") % 1000 % 3 == 0, 90)
              .when(F.col("id") % 1000 % 3 == 1, 50).otherwise(70))
    noise = F.pmod(F.xxhash64("id", F.lit(seed)), F.lit(21)) - 10
    liters = target + noise + F.when(F.col("id") % 113 == 0, target).otherwise(0)
    df = base.select(
        F.col("id").cast("string").alias("event_id"),
        F.when(F.col("id") % 991 == 0, "9999")
         .otherwise((F.col("id") % 1000).cast("string")).alias("equipment_id"),
        F.when(F.col("id") % 983 == 0, "invalid-date").otherwise(
            F.from_unixtime(F.lit(1735689600) + F.floor(F.col("id") / 1000) * 3600)
        ).alias("event_time"),
        F.when(F.col("id") % 997 == 0, "-1").otherwise(liters.cast("string")).alias("liters"),
        F.lit("60").alias("operating_minutes"),
        (F.lit(580) + F.pmod(F.xxhash64("id", F.lit(seed + 1)), F.lit(41)))
            .cast("string").alias("price_cents_per_liter"),
        F.col("id").alias("ingest_sequence"),
    )
    duplicates = df.where(F.col("ingest_sequence") % 500 == 0).withColumn(
        "ingest_sequence", F.col("ingest_sequence") + F.lit(rows)
    )
    return df.unionByName(duplicates)

def clean(raw, dimension):
    """Retorna aceitos, rejeitados e versões duplicadas; uma razão por rejeição."""
    if dimension.groupBy("equipment_id").count().where("count > 1").limit(1).count():
        raise ValueError("Dimensão contém equipment_id duplicado")
    typed = (raw
        .withColumn("_event_id", F.col("event_id").cast("long"))
        .withColumn("_equipment_id", F.col("equipment_id").cast("long"))
        .withColumn("_timestamp", F.to_timestamp("event_time", "yyyy-MM-dd HH:mm:ss"))
        .withColumn("_liters", F.col("liters").cast("decimal(18,3)"))
        .withColumn("_minutes", F.col("operating_minutes").cast("decimal(12,3)"))
        .withColumn("_price", F.col("price_cents_per_liter").cast("decimal(12,3)")))
    # A impressão digital desempata versões com a mesma sequência.
    typed = typed.withColumn("_fingerprint", F.sha2(F.to_json(F.struct(*raw.columns)), 256))
    rank = Window.partitionBy("_event_id").orderBy(
        F.col("ingest_sequence").desc_nulls_last(), F.col("_fingerprint").desc())
    ranked = typed.withColumn("_rank", F.row_number().over(rank))
    duplicates = ranked.where(F.col("_event_id").isNotNull() & (F.col("_rank") > 1))
    current = ranked.where(F.col("_event_id").isNull() | (F.col("_rank") == 1))
    dim = dimension.withColumnRenamed("equipment_id", "_dim_id")
    joined = current.join(F.broadcast(dim), current["_equipment_id"] == dim["_dim_id"], "left")
    reason = (F.when(F.col("_event_id").isNull() | (F.col("_event_id") < 0), "INVALID_EVENT_ID")
              .when(F.col("_timestamp").isNull(), "INVALID_TIMESTAMP")
              .when(F.col("_dim_id").isNull(), "UNKNOWN_EQUIPMENT")
              .when(F.col("_liters").isNull() | (F.col("_liters") <= 0), "INVALID_LITERS")
              .when(F.col("_minutes").isNull() | (F.col("_minutes") <= 0) |
                    (F.col("_minutes") > 1440), "INVALID_OPERATING_MINUTES")
              .when(F.col("_price").isNull() | (F.col("_price") <= 0), "INVALID_PRICE"))
    classified = joined.withColumn("rejection_reason", reason)
    rejected = classified.where(F.col("rejection_reason").isNotNull()).select(
        *raw.columns, "rejection_reason")
    accepted = classified.where(F.col("rejection_reason").isNull()).select(
        F.col("_event_id").alias("event_id"),
        F.col("_equipment_id").alias("equipment_id"),
        F.col("_timestamp").alias("event_timestamp"),
        F.col("_liters").alias("liters"),
        F.col("_minutes").alias("operating_minutes"),
        F.col("_price").alias("price_cents_per_liter"),
        "unit", "equipment_type", "reference_lph",
    )
    accepted = (accepted
        .withColumn("event_date", F.to_date("event_timestamp"))
        .withColumn("year_month", F.date_format("event_timestamp", "yyyy-MM"))
        .withColumn("cost_brl", (F.col("liters") * F.col("price_cents_per_liter") / 100).cast("decimal(20,2)"))
        .withColumn("liters_per_hour", F.col("liters") * 60 / F.col("operating_minutes"))
        .withColumn("high_consumption", F.col("liters_per_hour") > F.col("reference_lph") * F.lit(1.5)))
    return accepted, rejected, duplicates.select(*raw.columns)

def aggregate(accepted, group_columns):
    grouped = accepted.groupBy(*group_columns).agg(
        F.count("*").alias("events"),
        F.sum("liters").alias("liters"),
        F.sum("operating_minutes").alias("operating_minutes"),
        F.sum("cost_brl").alias("cost_brl"),
        F.sum(F.col("high_consumption").cast("long")).alias("high_consumption_events"),
    )
    return (grouped
        .withColumn("operating_hours", F.col("operating_minutes") / 60)
        .withColumn("liters_per_hour", F.col("liters") * 60 / F.col("operating_minutes"))
        .withColumn("high_consumption_rate", F.col("high_consumption_events") / F.col("events")))

def run(spark, rows, partitions, output, seed=42, raw=None):
    """Cada execução exige uma pasta nova; não sobrescreve resultados anteriores."""
    root = Path(output).resolve()
    if root.exists():
        raise FileExistsError("Use uma pasta de saída nova: " + str(root))
    root.mkdir(parents=True)
    started = time.perf_counter()
    generated = raw is None
    raw = raw if raw is not None else generate(spark, rows, partitions, seed)
    raw.write.mode("errorifexists").parquet(str(root / "bronze/events"))
    bronze = spark.read.parquet(str(root / "bronze/events"))
    accepted, rejected, duplicates = clean(bronze, equipment_dimension(spark))
    # Materializar cada saída corta a linhagem para as leituras analíticas.
    writer = accepted.write.mode("errorifexists")
    if accepted.limit(1).count():
        writer = writer.partitionBy("year_month")
    writer.parquet(str(root / "silver/events"))
    rejected.write.mode("errorifexists").parquet(str(root / "quarantine/rejected"))
    duplicates.write.mode("errorifexists").parquet(str(root / "quarantine/duplicates"))
    silver = spark.read.parquet(str(root / "silver/events"))
    gold = aggregate(silver, ["year_month", "unit", "equipment_type"])
    gold_writer = gold.write.mode("errorifexists")
    if gold.limit(1).count():
        gold_writer = gold_writer.partitionBy("year_month")
    gold_writer.parquet(str(root / "gold/monthly"))
    equipment_dimension(spark).write.mode("errorifexists").parquet(str(root / "gold/equipment"))

    metrics = {
        "synthetic_data": True,
        "spark_version": spark.version,
        "master": spark.sparkContext.master,
        "seed": seed,
        "requested_unique_events": rows if generated else None,
        "input_partitions": bronze.rdd.getNumPartitions(),
        "bronze_rows": bronze.count(),
        "silver_rows": silver.count(),
        "rejected_rows": spark.read.parquet(str(root / "quarantine/rejected")).count(),
        "duplicate_rows": spark.read.parquet(str(root / "quarantine/duplicates")).count(),
    }
    if metrics["bronze_rows"] != metrics["silver_rows"] + metrics["rejected_rows"] + metrics["duplicate_rows"]:
        raise AssertionError("Falha na reconciliação das linhas")
    metrics["rejection_rate_after_dedup"] = (
        metrics["rejected_rows"] / (metrics["silver_rows"] + metrics["rejected_rows"])
        if metrics["silver_rows"] + metrics["rejected_rows"] else 0
    )
    metrics["rejection_reasons"] = {
        row["rejection_reason"]: row["count"]
        for row in spark.read.parquet(str(root / "quarantine/rejected"))
            .groupBy("rejection_reason").count().collect()
    }
    metrics["elapsed_seconds"] = round(time.perf_counter() - started, 3)
    metrics["scope"] = "single-machine demonstration" if metrics["master"].startswith("local") else "configured Spark master; inspect deployment separately"
    (root / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    silver.createOrReplaceTempView("silver_events")
    sql_dir = Path(__file__).parent / "sql"
    # Apenas resultados agregados limitados são exportados para consulta e Power BI.
    export = root / "exports"
    export.mkdir()
    for name in ("monthly_kpis", "equipment_alerts"):
        result = spark.sql((sql_dir / (name + ".sql")).read_text(encoding="utf-8"))
        if result.limit(10001).count() > 10000:
            raise ValueError("Exportação excedeu 10.000 grupos; use a saída Parquet")
        (result.coalesce(1).write.mode("errorifexists").option("header", True)
         .csv(str(export / name)))
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return metrics

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=100000)
    parser.add_argument("--partitions", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="data/run-100k")
    parser.add_argument("--input", help="CSV sintético com RAW_SCHEMA; ignora a geração")
    parser.add_argument("--master", default="local[2]")
    args = parser.parse_args()
    if not 1 <= args.rows <= 10000000 or args.partitions < 1:
        parser.error("rows deve estar entre 1 e 10 milhões; partitions deve ser positivo")
    spark = (SparkSession.builder.master(args.master).appName("EquipAnalytics")
             .config("spark.sql.session.timeZone", "UTC")
             .config("spark.sql.ansi.enabled", "false")
             .config("spark.sql.legacy.timeParserPolicy", "CORRECTED")
             .config("spark.sql.shuffle.partitions", str(args.partitions))
             .config("spark.sql.adaptive.enabled", "true").getOrCreate())
    spark.sparkContext.setLogLevel("WARN")
    try:
        raw = spark.read.option("header", True).schema(RAW_SCHEMA).csv(args.input) if args.input else None
        run(spark, args.rows, args.partitions, args.output, args.seed, raw)
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
