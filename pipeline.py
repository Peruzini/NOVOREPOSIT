"""Estudos de BI com dados sintéticos, sem dependências externas.

Execute: python pipeline.py
As saídas geradas são regravadas nas pastas dos estudos.
"""

import csv
import json
import random
import sqlite3
from collections import Counter, defaultdict
from datetime import date, timedelta
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = 2412
REFERENCE = date(2025, 12, 31)


def write_csv(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def deduplicate(rows, key):
    """Remove cópias idênticas; coloca todo ID conflitante em quarentena."""
    groups = defaultdict(list)
    rejected = []
    for line, row in enumerate(rows, 2):
        normalized = {k: "" if v is None else str(v).strip() for k, v in row.items()}
        identifier = normalized.get(key, "").upper()
        normalized[key] = identifier
        if not identifier:
            rejected.append({"LinhaOrigem": line, "ID": "", "Motivo": "id_ausente"})
        else:
            groups[identifier].append((line, normalized))
    unique = []
    for identifier, items in groups.items():
        first = items[0][1]
        if any(row != first for _, row in items[1:]):
            rejected.extend({"LinhaOrigem": line, "ID": identifier, "Motivo": "id_conflitante"}
                            for line, _ in items)
        else:
            unique.append(items[0])
            rejected.extend({"LinhaOrigem": line, "ID": identifier, "Motivo": "duplicata_identica"}
                            for line, _ in items[1:])
    return unique, rejected


def calendar(end=date(2026, 2, 28)):
    start = date(2025, 1, 1)
    return [{"Data": (day := start + timedelta(days=i)).isoformat(),
             "Ano": day.year, "Mes": day.month, "AnoMes": day.strftime("%Y-%m"),
             "Dia": day.day}
            for i in range((end - start).days + 1)]


def sales_sources():
    rng = random.Random(SEED)
    shops = [{"LojaID": f"L{i:02}", "Loja": f"Loja {i:02}", "UF": ["MG", "RJ", "SP"][(i - 1) % 3]}
             for i in range(1, 9)]
    products = [{"ProdutoID": f"P{i:02}", "Produto": f"Produto {i:02}",
                 "Categoria": ["Casa", "Tecnologia", "Esporte"][(i - 1) % 3]}
                for i in range(1, 13)]
    sellers = [{"VendedorID": f"VND{i:02}", "Vendedor": f"Vendedor {i:02}"}
               for i in range(1, 17)]
    rows = []
    for i in range(1, 1201):
        shop = rng.randint(1, 8)
        product = rng.randint(1, 12)
        rows.append({"VendaID": f"VEN{i:05}",
                     "Data": (date(2025, 1, 1) + timedelta(days=rng.randrange(365))).isoformat(),
                     "LojaID": f"L{shop:02}", "ProdutoID": f"P{product:02}",
                     "VendedorID": f"VND{shop * 2 - rng.randint(0, 1):02}",
                     "Quantidade": rng.randint(1, 5), "PrecoUnitarioCentavos": 2500 + product * 1800,
                     "CustoUnitarioCentavos": 1400 + product * 1050,
                     "DescontoPct": rng.choice([0, 0, 5, 10]),
                     "Status": "Cancelada" if i % 17 == 0 else "Concluida"})
    rows += [dict(row) for row in rows[:10]]
    invalid = [("LojaID", "L99"), ("Quantidade", -2), ("Data", "2025-02-30"),
               ("DescontoPct", 120), ("ProdutoID", "P99"), ("PrecoUnitarioCentavos", -1)]
    for i, (field, value) in enumerate(invalid, 1):
        rows.append({**rows[0], "VendaID": f"ERRO{i:03}", field: value})
    rows.append({**rows[199], "Quantidade": 99})
    return rows, shops, products, sellers


def clean_sales(rows, shops, products, sellers):
    unique, rejected = deduplicate(rows, "VendaID")
    ids = [{row[key] for row in source} for source, key in
           [(shops, "LojaID"), (products, "ProdutoID"), (sellers, "VendedorID")]]
    accepted = []
    for line, raw in unique:
        r = dict(raw)
        try:
            if r.get("Status") == "Cancelada":
                raise ValueError("venda_cancelada")
            if r.get("Status") != "Concluida":
                raise ValueError("status_invalido")
            for key, valid in zip(["LojaID", "ProdutoID", "VendedorID"], ids):
                r[key] = r.get(key, "").upper()
                if r[key] not in valid:
                    raise ValueError("chave_" + key + "_invalida")
            try:
                day = date.fromisoformat(r["Data"])
                if day.year != 2025:
                    raise ValueError()
            except (ValueError, KeyError):
                raise ValueError("data_invalida") from None
            try:
                for key in ["Quantidade", "PrecoUnitarioCentavos", "CustoUnitarioCentavos", "DescontoPct"]:
                    r[key] = int(r[key])
            except (ValueError, KeyError):
                raise ValueError("numero_invalido") from None
            if r["Quantidade"] <= 0:
                raise ValueError("quantidade_invalida")
            if r["PrecoUnitarioCentavos"] < 0 or r["CustoUnitarioCentavos"] < 0:
                raise ValueError("valor_negativo")
            if not 0 <= r["DescontoPct"] <= 100:
                raise ValueError("desconto_invalido")
            r["ReceitaBrutaCentavos"] = r["Quantidade"] * r["PrecoUnitarioCentavos"]
            r["DescontoCentavos"] = (r["ReceitaBrutaCentavos"] * r["DescontoPct"] + 50) // 100
            r["ReceitaLiquidaCentavos"] = r["ReceitaBrutaCentavos"] - r["DescontoCentavos"]
            r["CustoCentavos"] = r["Quantidade"] * r["CustoUnitarioCentavos"]
            r["LucroBrutoCentavos"] = r["ReceitaLiquidaCentavos"] - r["CustoCentavos"]
            accepted.append(r)
        except ValueError as error:
            rejected.append({"LinhaOrigem": line, "ID": r["VendaID"], "Motivo": str(error)})
    return accepted, sorted(rejected, key=lambda row: row["LinhaOrigem"])


def project_sources():
    rng = random.Random(SEED + 1)
    teams = [{"EquipeID": f"E{i:02}", "Equipe": name}
             for i, name in enumerate(["BI", "Engenharia de Dados", "Automação", "Processos"], 1)]
    rows = []
    for i in range(1, 181):
        created = date(2025, 1, 1) + timedelta(days=rng.randrange(365))
        start = created + timedelta(days=rng.randint(1, 6))
        due = created + timedelta(days=rng.randint(7, 40))
        finish = start + timedelta(days=rng.randint(2, 35))
        done = i % 5 < 3 and finish <= REFERENCE
        active = not done and i % 5 != 4 and start <= REFERENCE
        rows.append({"DemandaID": f"DEM{i:04}", "DataCriacao": created.isoformat(),
                     "DataInicio": start.isoformat() if done or active else "",
                     "DataConclusao": finish.isoformat() if done else "", "DataPrazo": due.isoformat(),
                     "EquipeID": f"E{rng.randint(1, 4):02}",
                     "TipoDemanda": rng.choice(["Dashboard", "Integracao", "Automacao", "Melhoria"]),
                     "Prioridade": rng.choice(["Alta", "Media", "Baixa"]),
                     "Status": "Concluida" if done else "Em andamento" if active else "A fazer",
                     "EsforcoPlanejadoHoras": rng.randint(4, 60),
                     "EsforcoRealHoras": rng.randint(2, 72) if done or active else 0})
    rows += [dict(row) for row in rows[:5]]
    rows += [{**rows[0], "DemandaID": "ERRO001", "EquipeID": "E99"},
             {**rows[0], "DemandaID": "ERRO002", "Status": "Concluida", "DataConclusao": ""},
             {**rows[0], "DemandaID": "ERRO003", "DataPrazo": "data invalida"}]
    return rows, teams


def clean_projects(rows, teams, reference=REFERENCE):
    unique, rejected = deduplicate(rows, "DemandaID")
    valid_teams = {row["EquipeID"] for row in teams}
    accepted = []
    for line, raw in unique:
        r = dict(raw)
        try:
            if r.get("EquipeID") not in valid_teams:
                raise ValueError("equipe_invalida")
            if r.get("Status") not in {"Concluida", "Em andamento", "A fazer"}:
                raise ValueError("status_invalido")
            try:
                created, due = date.fromisoformat(r["DataCriacao"]), date.fromisoformat(r["DataPrazo"])
                start = date.fromisoformat(r["DataInicio"]) if r.get("DataInicio") else None
                finish = date.fromisoformat(r["DataConclusao"]) if r.get("DataConclusao") else None
            except (ValueError, KeyError):
                raise ValueError("data_invalida") from None
            if created > reference or due < created or (start and (start < created or start > reference)):
                raise ValueError("cronologia_invalida")
            if r["Status"] == "Concluida":
                if not start or not finish:
                    raise ValueError("conclusao_sem_datas")
                if finish < start or finish > reference:
                    raise ValueError("cronologia_invalida")
            elif finish or (r["Status"] == "Em andamento" and not start) or (r["Status"] == "A fazer" and start):
                raise ValueError("status_datas_incompativeis")
            try:
                r["EsforcoPlanejadoHoras"] = int(r["EsforcoPlanejadoHoras"])
                r["EsforcoRealHoras"] = int(r["EsforcoRealHoras"])
            except (ValueError, KeyError):
                raise ValueError("esforco_invalido") from None
            if min(r["EsforcoPlanejadoHoras"], r["EsforcoRealHoras"]) < 0:
                raise ValueError("esforco_invalido")
            r["DataInicio"] = start.isoformat() if start else None
            r["DataConclusao"] = finish.isoformat() if finish else None
            r["DataReferencia"] = reference.isoformat()
            r["TempoCicloDias"] = (finish - start).days if finish else None
            r["LeadTimeDias"] = (finish - created).days if finish else None
            r["EmAtraso"] = int(not finish and due < reference)
            r["EntregueNoPrazo"] = int(finish <= due) if finish else None
            accepted.append(r)
        except ValueError as error:
            rejected.append({"LinhaOrigem": line, "ID": r["DemandaID"], "Motivo": str(error)})
    return accepted, sorted(rejected, key=lambda row: row["LinhaOrigem"])


def install_tables(connection, schema, tables):
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(schema)
    for name, rows in tables.items():
        if not rows:
            continue
        fields = list(rows[0])
        columns = ", ".join('"' + field + '"' for field in fields)
        placeholders = ", ".join("?" for _ in fields)
        connection.executemany(f'INSERT INTO "{name}" ({columns}) VALUES ({placeholders})',
                               [[row[field] for field in fields] for row in rows])
    connection.commit()
    if connection.execute("PRAGMA foreign_key_check").fetchall():
        raise AssertionError("Falha de integridade referencial")


def overview_svg(path, title, values, money=False):
    values = sorted(values, key=lambda pair: (-pair[1], pair[0]))
    maximum = max((value for _, value in values), default=1) or 1
    height = 170 + len(values) * 48
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{height}" viewBox="0 0 960 {height}">',
             f'<rect width="960" height="{height}" fill="#F8FAFC"/>',
             '<g font-family="Arial, sans-serif" fill="#0F172A">',
             f'<text x="32" y="46" font-size="25" font-weight="bold">{escape(title)}</text>',
             '<text x="32" y="76" font-size="15" fill="#475569">Estudo de portfólio • Dados sintéticos • Referência 2025</text>']
    for index, (label, value) in enumerate(values):
        y = 108 + index * 48
        width = round(470 * value / maximum, 2)
        number = ("R$ " + f"{value / 100:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")) if money else str(value)
        parts += [f'<text x="32" y="{y + 22}" font-size="16">{escape(label)}</text>',
                  f'<rect x="255" y="{y}" width="{width}" height="30" rx="4" fill="#2563EB"/>',
                  f'<text x="920" y="{y + 22}" text-anchor="end" font-size="16">{escape(number)}</text>']
    parts += [f'<text x="32" y="{height - 28}" font-size="13" fill="#475569">Visualização estática gerada pelo Python. O relatório Power BI é uma entrega separada.</text>', '</g></svg>']
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_outputs(folder, raw_name, raw, tables, rejected, summary, chart_values, chart_title, money=False):
    write_csv(folder / "dados/brutos" / raw_name, raw)
    for name, rows in tables.items():
        write_csv(folder / "dados/tratados" / (name + ".csv"), rows)
    write_csv(folder / "resultados/linhas-excluidas.csv", rejected, ["LinhaOrigem", "ID", "Motivo"])
    summary.update({"origem": "dados totalmente sinteticos", "semente": SEED if money else SEED + 1,
                    "data_referencia": REFERENCE.isoformat(), "linhas_brutas": len(raw),
                    "linhas_excluidas": len(rejected), "exclusoes_por_motivo": dict(Counter(row["Motivo"] for row in rejected))})
    if summary["linhas_validas"] + len(rejected) != len(raw):
        raise AssertionError("Contagens de entrada e saida divergentes")
    result = folder / "resultados"
    result.mkdir(parents=True, exist_ok=True)
    (result / "resumo.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    overview_svg(result / "visao-geral.svg", chart_title, chart_values, money)
    checks = ["# Validações da execução", "", "Dados sintéticos. Relatório gerado por `python pipeline.py`.", "",
              f"- Linhas brutas: {len(raw)}", f"- Linhas válidas: {summary['linhas_validas']}",
              f"- Linhas excluídas: {len(rejected)}", "- Entrada = linhas válidas + linhas excluídas: OK",
              "- Chaves primárias únicas e não nulas: OK", "- Integridade referencial no SQLite: OK",
              "- Indicadores calculados em Python conciliados com SQL: OK", "", "## Exclusões", "",
              "| Motivo | Linhas |", "| --- | ---: |"]
    checks += [f"| {reason} | {count} |" for reason, count in sorted(summary["exclusoes_por_motivo"].items())]
    checks += ["", "Os motivos são mutuamente exclusivos neste relatório. Para um ID conflitante, todas as linhas do ID são excluídas.",
               "Uma linha com mais de um problema recebe o primeiro motivo detectado. Veja o CSV para identificar a linha da base bruta.", ""]
    (result / "validacoes.md").write_text("\n".join(checks), encoding="utf-8")


def build_case(name, raw, tables, rejected, summary, chart_values, chart_title, money=False):
    folder = ROOT / "projetos" / name
    result = folder / "resultados"
    result.mkdir(parents=True, exist_ok=True)
    database = result / "analise.sqlite"
    # A base gerada é reconstruída sem apagar outros arquivos do usuário.
    with sqlite3.connect(database) as connection:
        existing = connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        if existing:
            connection.execute("PRAGMA foreign_keys = OFF")
            for table in ["FatoVendas", "FatoDemandas", "DimCalendario", "DimLoja", "DimProduto", "DimVendedor", "DimEquipe"]:
                connection.execute(f'DROP TABLE IF EXISTS "{table}"')
            connection.commit()
        schema = (folder / "sql/modelo.sql").read_text(encoding="utf-8")
        install_tables(connection, schema, tables)
        connection.row_factory = sqlite3.Row
        queries = []
        for statement in (folder / "sql/consultas.sql").read_text(encoding="utf-8").split(";"):
            if statement.strip():
                queries.append([dict(row) for row in connection.execute(statement)])
        aggregate = queries[0][0]
        for key in summary:
            if key in aggregate and summary[key] != aggregate[key]:
                raise AssertionError(f"Conciliacao SQL/Python: {key}")
        (result / "consultas.json").write_text(json.dumps(queries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_outputs(folder, "vendas.csv" if money else "demandas.csv", raw, tables, rejected, summary,
                  chart_values, chart_title, money)
    return summary


def main():
    raw, shops, products, sellers = sales_sources()
    sales, rejected = clean_sales(raw, shops, products, sellers)
    tables = {"DimCalendario": calendar(), "DimLoja": shops, "DimProduto": products,
              "DimVendedor": sellers, "FatoVendas": sales}
    summary = {"linhas_validas": len(sales),
               "receita_liquida_centavos": sum(r["ReceitaLiquidaCentavos"] for r in sales),
               "lucro_bruto_centavos": sum(r["LucroBrutoCentavos"] for r in sales)}
    values = [(shop["Loja"] + " - " + shop["UF"], sum(r["ReceitaLiquidaCentavos"] for r in sales if r["LojaID"] == shop["LojaID"])) for shop in shops]
    commercial = build_case("analise-comercial", raw, tables, rejected, summary, values, "Receita líquida por loja", True)
    raw_projects, teams = project_sources()
    demands, rejected_projects = clean_projects(raw_projects, teams)
    tables_projects = {"DimCalendario": calendar(), "DimEquipe": teams, "FatoDemandas": demands}
    project_summary = {"linhas_validas": len(demands), "concluidas": sum(r["Status"] == "Concluida" for r in demands),
                       "backlog": sum(r["Status"] != "Concluida" for r in demands),
                       "em_atraso": sum(r["EmAtraso"] for r in demands)}
    project_values = [(team["Equipe"], sum(r["EmAtraso"] for r in demands if r["EquipeID"] == team["EquipeID"])) for team in teams]
    projects = build_case("indicadores-projetos", raw_projects, tables_projects, rejected_projects, project_summary,
                          project_values, "Demandas abertas em atraso por equipe")
    print(json.dumps({"analise_comercial": commercial, "indicadores_projetos": projects}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
