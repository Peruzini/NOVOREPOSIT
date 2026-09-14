import json
import tempfile
import unittest
from pathlib import Path

from pyspark.sql import SparkSession
from pipeline import RAW_SCHEMA, aggregate, clean, equipment_dimension, generate, run

ROOT = Path(__file__).resolve().parents[1]

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = (SparkSession.builder.master("local[2]").appName("EquipAnalyticsTests")
            .config("spark.sql.session.timeZone", "UTC")
            .config("spark.sql.ansi.enabled", "false")
            .config("spark.sql.legacy.timeParserPolicy", "CORRECTED")
            .config("spark.sql.shuffle.partitions", "2")
            .config("spark.ui.enabled", "false").getOrCreate())
        cls.spark.sparkContext.setLogLevel("ERROR")
        cls.dim = equipment_dimension(cls.spark)

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def fixture(self):
        return self.spark.read.option("header", True).schema(RAW_SCHEMA).csv(str(ROOT / "examples/events.csv"))

    def frame(self, rows):
        return self.spark.createDataFrame(rows, RAW_SCHEMA)

    def test_fixture_reconciliation_and_known_totals(self):
        valid, rejected, duplicates = clean(self.fixture(), self.dim)
        self.assertEqual((valid.count(), rejected.count(), duplicates.count()), (4, 5, 1))
        total = aggregate(valid, []).first()
        self.assertEqual(float(total.liters), 360)
        self.assertEqual(float(total.cost_brl), 2160)
        self.assertEqual(float(total.operating_hours), 4)
        self.assertEqual(float(total.liters_per_hour), 90)
        self.assertEqual(total.high_consumption_events, 1)
        reasons = {r.rejection_reason: r["count"] for r in rejected.groupBy("rejection_reason").count().collect()}
        expected = json.loads((ROOT / "examples/expected.json").read_text())
        self.assertEqual(reasons, expected["rejection_reasons"])

    def test_latest_invalid_version_is_quarantined(self):
        raw = self.frame([
            ("1", "0", "2025-01-01 00:00:00", "90", "60", "600", 1),
            ("1", "0", "2025-01-01 00:00:00", "-1", "60", "600", 2),
        ])
        valid, rejected, duplicates = clean(raw, self.dim)
        self.assertEqual((valid.count(), rejected.count(), duplicates.count()), (0, 1, 1))
        self.assertEqual(rejected.first().rejection_reason, "INVALID_LITERS")
        self.assertEqual(duplicates.first().ingest_sequence, 1)

    def test_weighted_rate_and_strict_threshold(self):
        raw = self.frame([
            ("1", "0", "2025-01-01 00:00:00", "90", "60", "600", 1),
            ("2", "0", "2025-01-01 01:00:00", "90", "30", "600", 2),
            ("3", "0", "2025-01-01 02:00:00", "135", "60", "600", 3),
        ])
        valid, _, _ = clean(raw, self.dim)
        total = aggregate(valid, []).first()
        self.assertAlmostEqual(float(total.liters_per_hour), 126.0)
        self.assertEqual(total.high_consumption_events, 1)

    def test_nonfinite_missing_and_invalid_identifiers(self):
        rows = [
            (str(i), "0", "2025-01-01 00:00:00", liters, "60", "600", i)
            for i, liters in enumerate(["NaN", "Infinity", "-Infinity", None, "abc"])
        ]
        rows.extend([
            (None, "0", "2025-01-01 00:00:00", "90", "60", "600", 6),
            ("x", "0", "2025-01-01 00:00:00", "90", "60", "600", 7),
            ("8", "0", "2025-01-01 00:00:00", "90", "60", None, 8),
        ])
        valid, rejected, duplicates = clean(self.frame(rows), self.dim)
        self.assertEqual((valid.count(), rejected.count(), duplicates.count()), (0, 8, 0))

    def test_dimension_duplicate_is_blocked(self):
        duplicated_dim = self.dim.unionByName(self.dim.where("equipment_id = 0"))
        with self.assertRaises(ValueError):
            clean(self.fixture(), duplicated_dim)

    def test_native_generator_cardinality_and_reproducibility(self):
        first = generate(self.spark, 2000, 2, 42)
        second = generate(self.spark, 2000, 3, 42)
        self.assertEqual(first.count(), 2004)
        self.assertEqual(first.exceptAll(second).count(), 0)
        self.assertEqual(second.exceptAll(first).count(), 0)

    def test_end_to_end_sql_exports_and_output_protection(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "run"
            metrics = run(self.spark, 10, 2, output, raw=self.fixture())
            self.assertEqual(metrics["silver_rows"], 4)
            self.assertIsNone(metrics["requested_unique_events"])
            gold = self.spark.read.parquet(str(output / "gold/monthly"))
            self.assertEqual(float(gold.groupBy().sum("liters").first()[0]), 360)
            exported = self.spark.read.option("header", True).csv(str(output / "exports/monthly_kpis"))
            self.assertEqual(exported.count(), 3)
            self.assertEqual(sum(float(r.liters) for r in exported.collect()), 360)
            self.assertTrue((output / "metrics.json").exists())
            with self.assertRaises(FileExistsError):
                run(self.spark, 10, 2, output, raw=self.fixture())

if __name__ == "__main__":
    unittest.main()
