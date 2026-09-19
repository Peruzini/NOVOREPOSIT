"""Local Fleet reference data and SQL checks; never connects to Snowflake.

The generator is a Python port of the PBIP Power Query formulas, not an M or
DAX execution engine. Compare the exported references in Power BI Desktop.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
MODEL = REPO / "powerbi/fleet/FleetAnalytics.SemanticModel/model.bim"
EQUIPMENT = [
    ("EQ-01", "Caminhão 01", "Caminhão", "Mina Norte"),
    ("EQ-02", "Caminhão 02", "Caminhão", "Mina Norte"),
    ("EQ-03", "Caminhão 03", "Caminhão", "Mina Sul"),
    ("EQ-04", "Caminhão 04", "Caminhão", "Mina Sul"),
    ("EQ-05", "Escavadeira 01", "Escavadeira", "Mina Norte"),
    ("EQ-06", "Escavadeira 02", "Escavadeira", "Mina Sul"),
    ("EQ-07", "Carregadeira 01", "Carregadeira", "Pilha"),
    ("EQ-08", "Trator 01", "Trator", "Infraestrutura"),
]
COLUMNS = [
    "DATA", "EQUIPAMENTO_ID", "EQUIPAMENTO", "TIPO", "AREA", "PRODUCAO_TON",
    "HORAS_OPERACAO", "HORAS_CALENDARIO", "HORAS_MANUTENCAO", "HORAS_CORRETIVAS",
    "FALHAS", "CUSTO_MANUTENCAO", "LITROS", "CUSTO_COMBUSTIVEL", "META_PRODUCAO_TON",
]
TEXT_COLUMNS = set(COLUMNS[:5])


def rounded(value: Decimal, places: int) -> float:
    return float(value.quantize(Decimal(10) ** -places, rounding=ROUND_HALF_EVEN))


def generate_rows():
    """730 days x 8 assets, including non-corrective maintenance costs."""
    rows = []
    for offset in range(730):
        day = date(2025, 1, 1) + timedelta(days=offset)
        doy = day.timetuple().tm_yday
        for idx, (key, name, kind, area) in enumerate(EQUIPMENT, 1):
            downtime = 2 + (doy + idx) % 7 if (doy + idx * 7) % (13 + idx % 4) == 0 else 0
            hours = min(15 + (doy * 3 + idx * 5) % 8, 24 - downtime)
            corrective = downtime > 0 and (doy + idx) % 3 == 0
            tons = rounded(Decimal(110 + idx * 9 + (doy * 11 + idx * 17) % 75) * hours / 20, 1)
            liters = 950 + idx * 35 + (doy * 19 + idx * 31) % 420
            fuel = rounded(Decimal(liters) * (Decimal("5.35") + Decimal(doy % 20) / 100), 2)
            values = [day.isoformat(), key, name, kind, area, tons, hours, 24,
                      downtime, downtime if corrective else 0, int(corrective),
                      downtime * (850 + idx * 90), liters, fuel, 145 + idx * 7]
            rows.append(dict(zip(COLUMNS, values)))
    return rows


def validate_rows(rows):
    seen = set()
    for row in rows:
        key = (row["DATA"], row["EQUIPAMENTO_ID"])
        if key in seen:
            raise ValueError(f"Duplicate daily asset key: {key}")
        seen.add(key)
        if not 0 <= row["HORAS_CORRETIVAS"] <= row["HORAS_MANUTENCAO"] <= row["HORAS_CALENDARIO"]:
            raise ValueError(f"Invalid maintenance hours: {key}")
        if not 0 <= row["HORAS_OPERACAO"] <= row["HORAS_CALENDARIO"] - row["HORAS_MANUTENCAO"]:
            raise ValueError(f"Operation exceeds available hours: {key}")
        if row["FALHAS"] not in (0, 1) or bool(row["FALHAS"]) != bool(row["HORAS_CORRETIVAS"]):
            raise ValueError(f"Corrective event mismatch: {key}")
        if any(row[c] < 0 for c in COLUMNS if c not in TEXT_COLUMNS):
            raise ValueError(f"Negative quantity: {key}")


def connect_local(rows):
    validate_rows(rows)
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    definitions = [f"{c} {'TEXT' if c in TEXT_COLUMNS else 'REAL'}" for c in COLUMNS]
    definitions.append("PRIMARY KEY (DATA, EQUIPAMENTO_ID)")
    db.execute("CREATE TABLE FLEET_DAILY (" + ",".join(definitions) + ")")
    db.executemany("INSERT INTO FLEET_DAILY VALUES (" + ",".join("?" for _ in COLUMNS) + ")",
                   [[row[c] for c in COLUMNS] for row in rows])
    return db


def run_queries(db):
    results = {}
    for path in sorted((ROOT / "evaluation/queries").glob("*.sql")):
        results[path.stem] = [dict(row) for row in db.execute(path.read_text())]
    return results


def render_sql(database, schema, warehouse):
    replacements = {"__DATABASE__": database, "__SCHEMA__": schema, "__WAREHOUSE__": warehouse}
    for value in replacements.values():
        if not re.fullmatch(r"[A-Z_][A-Z0-9_]*", value):
            raise ValueError("Use uppercase, unquoted Snowflake identifiers (letters, digits, underscore).")
    rendered = {}
    for relative in ["sql/01_setup.sql", "sql/02_load.sql", "sql/03_quality.sql", "semantic/04_semantic.sql", "agent/05_agent.sql"]:
        content = (ROOT / relative).read_text()
        for token, value in replacements.items():
            content = content.replace(token, value)
        rendered[Path(relative).name] = content
    return rendered


def build(output, database, schema, warehouse):
    rendered = render_sql(database, schema, warehouse)
    # Refuse accidental overwrite of an earlier verification run.
    output.mkdir(parents=True, exist_ok=False)
    rows = generate_rows()
    validate_rows(rows)
    with (output / "fleet_daily.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    db = connect_local(rows)
    expected = run_queries(db)
    db.close()
    (output / "expected.json").write_text(json.dumps(expected, ensure_ascii=False, indent=2) + "\n")
    for name, content in rendered.items():
        (output / name).write_text(content)
    status = {
        "dataset": "fleet-pilot-v1", "rows": len(rows), "start": rows[0]["DATA"], "end": rows[-1]["DATA"],
        "pbip_model_sha256": hashlib.sha256(MODEL.read_bytes()).hexdigest(),
        "csv_sha256": hashlib.sha256((output / "fleet_daily.csv").read_bytes()).hexdigest(),
        "local_reference": "Python synthetic generator + SQLite queries",
        "power_query_executed": False, "dax_executed": False,
        "snowflake_executed": False, "cortex_executed": False,
    }
    (output / "manifest.json").write_text(json.dumps(status, indent=2) + "\n")
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build")
    parser.add_argument("--database", default="PORTFOLIO")
    parser.add_argument("--schema", default="FLEET_PILOT_V1")
    parser.add_argument("--warehouse", default="COMPUTE_WH")
    args = parser.parse_args()
    print(json.dumps(build(args.output, args.database, args.schema, args.warehouse), indent=2))
