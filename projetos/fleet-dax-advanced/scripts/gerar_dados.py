from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 26092026
START = date(2025, 1, 1)
END = date(2026, 12, 31)
OUTPUT = Path(__file__).resolve().parents[1] / "dados"

random.seed(SEED)

EQUIPAMENTOS = []
for i in range(1, 13):
    EQUIPAMENTOS.append({
        "EquipamentoID": f"CT-{i:02d}",
        "Equipamento": f"Caminhao {i:02d}",
        "TipoEquipamento": "Caminhao",
        "Modelo": random.choice(["CAT 777", "Komatsu HD785", "Volvo R100E"]),
        "CapacidadeTon": random.choice([90, 95, 100]),
        "CentroCusto": random.choice(["Mina Norte", "Mina Sul"]),
        "AnoFabricacao": random.randint(2017, 2024),
    })

for i in range(1, 7):
    EQUIPAMENTOS.append({
        "EquipamentoID": f"EX-{i:02d}",
        "Equipamento": f"Escavadeira {i:02d}",
        "TipoEquipamento": "Escavadeira",
        "Modelo": random.choice(["CAT 6015", "Komatsu PC2000", "Liebherr R 9100"]),
        "CapacidadeTon": random.choice([14, 16, 18]),
        "CentroCusto": random.choice(["Mina Norte", "Mina Sul"]),
        "AnoFabricacao": random.randint(2017, 2024),
    })

META = {
    "Caminhao": {
        "producao": 1450.0,
        "disp": 0.90,
        "util": 0.78,
        "consumo": 0.36,
    },
    "Escavadeira": {
        "producao": 2350.0,
        "disp": 0.92,
        "util": 0.82,
        "consumo": 0.22,
    },
}

SISTEMAS = ["Motor", "Transmissao", "Freios", "Hidraulico", "Eletrico", "Pneus"]


def daterange(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def write_csv(name: str, rows: list[dict], fieldnames: list[str]) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with (OUTPUT / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def gerar_dim_data() -> list[dict]:
    rows = []
    meses = [
        "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
        "Jul", "Ago", "Set", "Out", "Nov", "Dez",
    ]
    for d in daterange(START, END):
        rows.append({
            "Data": d.isoformat(),
            "Ano": d.year,
            "MesNumero": d.month,
            "Mes": meses[d.month - 1],
            "AnoMes": f"{d.year}-{d.month:02d}",
            "Trimestre": f"T{((d.month - 1) // 3) + 1}",
            "DiaSemana": d.strftime("%A"),
        })
    return rows


def gerar_operacao() -> tuple[list[dict], list[dict]]:
    operacao = []
    manutencao = []
    manutencao_id = 1

    perfil = {
        e["EquipamentoID"]: {
            "eficiencia": random.uniform(0.88, 1.08),
            "confiabilidade": random.uniform(0.90, 1.05),
        }
        for e in EQUIPAMENTOS
    }

    for d in daterange(START, END):
        sazonal = 0.94 if d.month in {1, 2, 12} else 1.00

        for e in EQUIPAMENTOS:
            p = perfil[e["EquipamentoID"]]
            horas_cal = 24.0
            prob_falha = 0.020 if e["TipoEquipamento"] == "Caminhao" else 0.026
            prob_falha *= (2.0 - p["confiabilidade"])

            falhou = random.random() < prob_falha
            preventiva = random.random() < 0.010
            horas_parada = 0.0

            if falhou:
                horas_parada += round(random.uniform(2.0, 12.0), 2)
                tipo = "Corretiva"
                sistema = random.choice(SISTEMAS)
                custo = round(horas_parada * random.uniform(650, 2200), 2)
                manutencao.append({
                    "ManutencaoID": manutencao_id,
                    "DataInicio": d.isoformat(),
                    "EquipamentoID": e["EquipamentoID"],
                    "TipoManutencao": tipo,
                    "Sistema": sistema,
                    "HorasParada": horas_parada,
                    "CustoManutencao": custo,
                    "FalhaFlag": 1,
                })
                manutencao_id += 1

            if preventiva:
                hp = round(random.uniform(1.0, 5.0), 2)
                horas_parada += hp
                manutencao.append({
                    "ManutencaoID": manutencao_id,
                    "DataInicio": d.isoformat(),
                    "EquipamentoID": e["EquipamentoID"],
                    "TipoManutencao": "Preventiva",
                    "Sistema": random.choice(SISTEMAS),
                    "HorasParada": hp,
                    "CustoManutencao": round(hp * random.uniform(350, 1100), 2),
                    "FalhaFlag": 0,
                })
                manutencao_id += 1

            horas_disp = max(0.0, horas_cal - horas_parada)
            meta_util = META[e["TipoEquipamento"]]["util"]
            util = min(0.98, max(0.45, random.gauss(meta_util * p["eficiencia"], 0.055)))
            horas_op = round(horas_disp * util, 2)

            if e["TipoEquipamento"] == "Caminhao":
                produtividade = random.uniform(62, 76) * p["eficiencia"] * sazonal
                ciclos_h = random.uniform(0.65, 0.90)
                litros_h = random.uniform(48, 62)
            else:
                produtividade = random.uniform(100, 128) * p["eficiencia"] * sazonal
                ciclos_h = random.uniform(0.22, 0.36)
                litros_h = random.uniform(25, 38)

            toneladas = round(horas_op * produtividade, 2)
            ciclos = max(0, int(horas_op * ciclos_h))
            combustivel = round(horas_op * litros_h * random.uniform(0.94, 1.08), 2)

            operacao.append({
                "Data": d.isoformat(),
                "EquipamentoID": e["EquipamentoID"],
                "HorasCalendario": horas_cal,
                "HorasDisponiveis": round(horas_disp, 2),
                "HorasOperadas": horas_op,
                "Ciclos": ciclos,
                "Toneladas": toneladas,
                "CombustivelLitros": combustivel,
            })

    return operacao, manutencao


def gerar_metas() -> list[dict]:
    rows = []
    qtd_por_tipo = {
        tipo: sum(1 for e in EQUIPAMENTOS if e["TipoEquipamento"] == tipo)
        for tipo in META
    }
    for d in daterange(START, END):
        for tipo, m in META.items():
            rows.append({
                "Data": d.isoformat(),
                "TipoEquipamento": tipo,
                "MetaProducaoTon": round(m["producao"] * qtd_por_tipo[tipo], 2),
                "MetaDisponibilidadePct": m["disp"],
                "MetaUtilizacaoPct": m["util"],
                "MetaConsumoLPorTon": m["consumo"],
            })
    return rows


def main() -> None:
    dim_data = gerar_dim_data()
    operacao, manutencao = gerar_operacao()
    metas = gerar_metas()

    write_csv(
        "dim_data.csv",
        dim_data,
        ["Data", "Ano", "MesNumero", "Mes", "AnoMes", "Trimestre", "DiaSemana"],
    )
    write_csv(
        "dim_equipamento.csv",
        EQUIPAMENTOS,
        ["EquipamentoID", "Equipamento", "TipoEquipamento", "Modelo", "CapacidadeTon", "CentroCusto", "AnoFabricacao"],
    )
    write_csv(
        "fato_operacao.csv",
        operacao,
        ["Data", "EquipamentoID", "HorasCalendario", "HorasDisponiveis", "HorasOperadas", "Ciclos", "Toneladas", "CombustivelLitros"],
    )
    write_csv(
        "fato_manutencao.csv",
        manutencao,
        ["ManutencaoID", "DataInicio", "EquipamentoID", "TipoManutencao", "Sistema", "HorasParada", "CustoManutencao", "FalhaFlag"],
    )
    write_csv(
        "fato_meta.csv",
        metas,
        ["Data", "TipoEquipamento", "MetaProducaoTon", "MetaDisponibilidadePct", "MetaUtilizacaoPct", "MetaConsumoLPorTon"],
    )

    print(f"Dados gerados em: {OUTPUT}")
    print(f"Equipamentos: {len(EQUIPAMENTOS)}")
    print(f"Linhas FatoOperacao: {len(operacao)}")
    print(f"Eventos FatoManutencao: {len(manutencao)}")
    print(f"Linhas FatoMeta: {len(metas)}")


if __name__ == "__main__":
    main()
