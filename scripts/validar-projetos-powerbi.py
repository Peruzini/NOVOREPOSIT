"""Validação estática; não abre o Desktop nem executa DAX/Power Query.

Requer jsonschema >= 4.18 e uma cópia de microsoft/json-schemas.
Uso: python scripts/validar-projetos-powerbi.py --schemas CAMINHO --write-report
"""
import argparse
import csv
import json
import re
from datetime import date, timedelta
from pathlib import Path

from jsonschema import Draft7Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PREFIX = "https://developer.microsoft.com/json-schemas/"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def registry_from(folder):
    registry = Registry()
    for path in sorted(folder.rglob("*.json")):
        value = read_json(path)
        if "$id" not in value:
            continue
        resource = Resource.from_contents(value, default_specification=DRAFT7)
        actual_url = SCHEMA_PREFIX + path.relative_to(folder).as_posix()
        # Embedded schema filenames and their $id use different separators.
        registry = registry.with_resource(actual_url, resource)
        registry = registry.with_resource(value["$id"], resource)
    return registry


def inspect_model(study_id, study_folder, title):
    path = ROOT / "powerbi" / study_id / (title + ".SemanticModel") / "model.bim"
    model = read_json(path)["model"]
    tables = {t["name"]: t for t in model["tables"]}
    rows = {}
    measure_names = {m["name"] for t in tables.values() for m in t.get("measures", [])}
    for name, table in tables.items():
        with (ROOT / "projetos" / study_folder / "dados/tratados" / (name + ".csv")).open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            require(reader.fieldnames == [c["name"] for c in table["columns"]], "Cabeçalho divergente: " + name)
            rows[name] = list(reader)
        for row in rows[name]:
            for column in table["columns"]:
                value = row[column["name"]]
                if not value:
                    continue
                if column["dataType"] == "int64":
                    require(str(int(value)) == value, "Inteiro inválido: " + name + "." + column["name"])
                if column["dataType"] == "dateTime":
                    date.fromisoformat(value)
        for column in table["columns"]:
            if column.get("isKey"):
                keys = [r[column["name"]] for r in rows[name]]
                require(len(keys) == len(set(keys)) and all(keys), "Chave inválida: " + name)
        for measure in table.get("measures", []):
            expression = "\n".join(measure["expression"])
            for entity, field in re.findall(r"(\w+)?\[([^\]]+)\]", expression):
                valid = field in measure_names if not entity else entity in tables and field in {c["name"] for c in tables[entity]["columns"]}
                require(valid, "Referência DAX ausente: " + measure["name"] + " -> " + entity + "." + field)
    calendar_dates = [date.fromisoformat(r["Data"]) for r in rows["DimCalendario"]]
    start = min(calendar_dates).replace(month=1, day=1)
    end = max(calendar_dates).replace(month=12, day=31)
    calendar_keys = {(start + timedelta(days=i)).isoformat() for i in range((end - start).days + 1)}
    for rel in model["relationships"]:
        source = tables[rel["fromTable"]]
        target = tables[rel["toTable"]]
        source_type = next(c["dataType"] for c in source["columns"] if c["name"] == rel["fromColumn"])
        target_type = next(c["dataType"] for c in target["columns"] if c["name"] == rel["toColumn"])
        require(source_type == target_type, "Tipos incompatíveis: " + rel["name"])
        keys = calendar_keys if rel["toTable"] == "DimCalendario" else {r[rel["toColumn"]] for r in rows[rel["toTable"]]}
        require(all(not r[rel["fromColumn"]] or r[rel["fromColumn"]] in keys for r in rows[rel["fromTable"]]), "Chave órfã: " + rel["name"])
        require(rel["fromCardinality"] == "many" and rel["toCardinality"] == "one" and rel["crossFilteringBehavior"] == "oneDirection", "Relação inesperada: " + rel["name"])
    return model, rows


def inspect_report(study_id, title, model):
    report = ROOT / "powerbi" / study_id / (title + ".Report")
    definitions = report / "definition"
    metadata = read_json(definitions / "pages/pages.json")
    tables = {t["name"]: t for t in model["tables"]}
    page_results, bindings = [], 0
    require(metadata["activePageName"] in metadata["pageOrder"], "Página inicial ausente")
    require(len(metadata["pageOrder"]) == len(set(metadata["pageOrder"])), "Páginas duplicadas")
    for page_id in metadata["pageOrder"]:
        page_folder = definitions / "pages" / page_id
        page = read_json(page_folder / "page.json")
        require(page["name"] == page_id, "Nome da página divergente")
        visuals = [read_json(p) for p in sorted((page_folder / "visuals").glob("*/visual.json"))]
        ids = {v["name"] for v in visuals}
        require(len(ids) == len(visuals), "Identificadores visuais duplicados")
        for i, container in enumerate(visuals):
            p = container["position"]
            require(min(p["x"], p["y"]) >= 0 and p["width"] > 0 and p["height"] > 0 and p["x"] + p["width"] <= page["width"] and p["y"] + p["height"] <= page["height"], "Visual fora da página: " + container["name"])
            for other in visuals[i + 1:]:
                q = other["position"]
                overlap = p["x"] < q["x"] + q["width"] and p["x"] + p["width"] > q["x"] and p["y"] < q["y"] + q["height"] and p["y"] + p["height"] > q["y"]
                require(not overlap, "Sobreposição: " + container["name"] + " / " + other["name"])
            visual = container["visual"]
            roles = visual.get("query", {}).get("queryState", {})
            expected = {"cardVisual": {"Data"}, "slicer": {"Values"}, "tableEx": {"Values"}, "lineChart": {"Category", "Y"}, "clusteredBarChart": {"Category", "Y"}, "textbox": set()}
            require(set(roles) == expected[visual["visualType"]], "Papéis do visual inválidos")
            for role in roles.values():
                for projection in role["projections"]:
                    kind, field = next(iter(projection["field"].items()))
                    entity, name = field["Expression"]["SourceRef"]["Entity"], field["Property"]
                    require(entity in tables, "Tabela do visual inexistente: " + entity)
                    fields = tables[entity]["columns" if kind == "Column" else "measures"]
                    require(name in {f["name"] for f in fields}, "Campo do visual inexistente: " + name)
                    require(projection["queryRef"] == entity + "." + name, "queryRef divergente")
                    bindings += 1
            if visual["visualType"] == "cardVisual":
                # Conservative height estimate for the explicit formatting used here.
                required_height = 2 + 24 + 16 + 36 + 6 + 18
                require(p["height"] >= required_height, "Cartão com altura insuficiente")
            if visual["visualType"] == "slicer":
                require(p["height"] >= 76, "Segmentação com altura insuficiente")
            if visual["visualType"] == "textbox":
                require(isinstance(visual["objects"]["general"][0]["properties"]["paragraphs"], list), "Textbox sem parágrafos nativos")
        for interaction in page.get("visualInteractions", []):
            require(interaction["source"] in ids and interaction["target"] in ids, "Interação aponta para visual ausente")
        page_results.append({"name": page["displayName"], "visuals": len(visuals)})
    report_json = read_json(definitions / "report.json")
    theme_name = report_json["themeCollection"]["customTheme"]["name"]
    resource = report_json["resourcePackages"][0]["items"][0]
    require(theme_name == resource["name"] == resource["path"], "Referências do tema divergentes")
    require((report / "StaticResources/RegisteredResources" / theme_name).is_file(), "Tema ausente")
    pbir = read_json(report / "definition.pbir")
    require((report / pbir["datasetReference"]["byPath"]["path"] / "model.bim").is_file(), "Modelo referenciado ausente")
    return page_results, bindings


def reference_totals(sales, demands):
    revenue = sum(int(r["ReceitaLiquidaCentavos"]) for r in sales)
    profit = sum(int(r["LucroBrutoCentavos"]) for r in sales)
    require((len(sales), revenue, profit) == (1129, 45090300, 17926800), "Totais comerciais inesperados")
    for month, store, count, value in [("2025-01", None, 89, 3883990), (None, "L04", 143, 6029755), ("2025-01", "L04", 15, 655980)]:
        selected = [r for r in sales if (month is None or r["Data"].startswith(month)) and (store is None or r["LojaID"] == store)]
        require((len(selected), sum(int(r["ReceitaLiquidaCentavos"]) for r in selected)) == (count, value), "Recorte comercial divergente")
    complete = [r for r in demands if r["Status"] == "Concluida"]
    overdue = sum(int(r["EmAtraso"]) for r in demands)
    ontime = sum(int(r["EntregueNoPrazo"] or 0) for r in demands)
    require((len(demands), len(complete), overdue, ontime) == (180, 102, 68, 64), "Totais de demandas inesperados")
    require(sum(r["DataConclusao"].startswith("2025-01") for r in complete) == 2, "Entregas de janeiro divergentes")
    require(sum(r["DataConclusao"].startswith("2025-12") for r in complete) == 14, "Entregas de dezembro divergentes")
    return {"comercial": {"pedidos": len(sales), "receitaCentavos": revenue, "lucroCentavos": profit}, "projetos": {"demandas": len(demands), "concluidas": len(complete), "backlog": len(demands) - len(complete), "abertasEmAtraso": overdue, "entregasNoPrazo": ontime}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schemas", required=True, type=Path, help="Raiz da cópia de microsoft/json-schemas, contendo fabric/")
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    registry = registry_from(args.schemas.resolve())
    schema_count = 0
    for path in sorted((ROOT / "powerbi").rglob("*")):
        if not path.is_file() or path.suffix not in {".json", ".bim", ".pbip", ".pbir", ".pbism"}:
            continue
        value = read_json(path)
        if "$schema" not in value:
            continue
        schema = registry.contents(value["$schema"])
        errors = list(Draft7Validator(schema, registry=registry).iter_errors(value))
        require(not errors, str(path.relative_to(ROOT)) + ": " + " | ".join(e.message for e in errors[:3]))
        schema_count += 1
    studies, facts, total_bindings = [], {}, 0
    for study_id, folder, title, fact in [("comercial", "analise-comercial", "Comercial", "FatoVendas"), ("projetos", "indicadores-projetos", "Projetos", "FatoDemandas")]:
        model, rows = inspect_model(study_id, folder, title)
        pages, bindings = inspect_report(study_id, title, model)
        studies.append({"project": title, "tables": len(model["tables"]), "measures": sum(len(t.get("measures", [])) for t in model["tables"]), "relationships": len(model["relationships"]), "pages": pages})
        facts[study_id] = rows[fact]
        total_bindings += bindings
    totals = reference_totals(facts["comercial"], facts["projetos"])
    report = {
        "scope": "Verificação estática de esquemas Microsoft, referências, layout e dados CSV. Não executa Power BI Desktop.",
        "schemasSource": "https://github.com/microsoft/json-schemas",
        "schemaValidatedDocuments": schema_count,
        "visualFieldBindingsChecked": total_bindings,
        "overlappingVisualRectangles": 0,
        "missingRelationshipsOrKeys": 0,
        "studies": studies,
        "referenceTotalsFromCSV": totals,
        "desktop": {"opened": False, "refreshed": False, "daxEngineValidated": False, "powerQueryEngineValidated": False, "visualRenderVerified": False, "pbixExported": False}
    }
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.write_report:
        (ROOT / "powerbi/validacao-estrutural.json").write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
