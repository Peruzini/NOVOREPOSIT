from __future__ import annotations
from pathlib import Path
import csv, math, random

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dados" / "tratados"
SEED = 20260914

CHANNELS = [
    ("CAN01","Google Ads","Mídia paga","Busca e intenção"),
    ("CAN02","Meta Ads","Mídia paga","Social e descoberta"),
    ("CAN03","LinkedIn Ads","Mídia paga","B2B e consideração"),
    ("CAN04","E-mail","Canal próprio","Nutrição e reativação"),
]
CAMPAIGNS = [
    ("CMP01","Search | Soluções BI","CAN01","Geração de leads"),
    ("CMP02","Search | Automação","CAN01","Geração de leads"),
    ("CMP03","Social | Conteúdo BI","CAN02","Geração de leads"),
    ("CMP04","Social | Remarketing","CAN02","Conversão"),
    ("CMP05","B2B | Dados & Analytics","CAN03","Geração de leads"),
    ("CMP06","B2B | Power BI","CAN03","Conversão"),
    ("CMP07","Newsletter | Conteúdo","CAN04","Nutrição"),
    ("CMP08","E-mail | Reativação","CAN04","Conversão"),
]
PARAMS = {
    "CMP01": (9000,180000,.046,.095,.32,.28,2100),
    "CMP02": (7000,140000,.042,.090,.30,.27,1850),
    "CMP03": (6500,310000,.012,.085,.22,.21,1450),
    "CMP04": (5000,120000,.019,.105,.28,.25,1650),
    "CMP05": (8000,90000,.010,.120,.42,.30,3300),
    "CMP06": (6500,70000,.012,.130,.45,.32,3700),
    "CMP07": (1200,110000,.032,.070,.18,.20,1000),
    "CMP08": (1500,65000,.041,.095,.24,.24,1200),
}

def generate_rows():
    random.seed(SEED)
    rows = []
    for month in range(1, 13):
        season = 1 + 0.10 * math.sin((month - 1) / 12 * 2 * math.pi)
        if month in (3, 9, 10):
            season += 0.07
        if month in (1, 12):
            season -= 0.10
        for campaign_id, _, channel_id, _ in CAMPAIGNS:
            spend, impressions, ctr, lead_rate, opportunity_rate, win_rate, revenue_per_customer = PARAMS[campaign_id]
            noise = lambda spread=.07: 1 + random.uniform(-spread, spread)
            investment = round(spend * season * noise())
            impressions_value = round(impressions * season * noise(.09))
            clicks = max(1, round(impressions_value * ctr * noise(.06)))
            leads = max(1, round(clicks * lead_rate * noise(.08)))
            opportunities = max(1, round(leads * opportunity_rate * noise(.08)))
            customers = max(1, round(opportunities * win_rate * noise(.08)))
            revenue = round(customers * revenue_per_customer * noise(.06))
            rows.append({
                "Data": f"2025-{month:02d}-01",
                "CampanhaID": campaign_id,
                "CanalID": channel_id,
                "InvestimentoCentavos": investment * 100,
                "Impressoes": impressions_value,
                "Cliques": clicks,
                "Leads": leads,
                "Oportunidades": opportunities,
                "Clientes": customers,
                "ReceitaCentavos": revenue * 100,
            })
    return rows

def write_csv(path, header, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)

def main():
    rows = generate_rows()
    OUT.mkdir(parents=True, exist_ok=True)
    write_csv(OUT / "DimCanal.csv", ["CanalID","Canal","TipoCanal","PapelNoFunil"], CHANNELS)
    write_csv(OUT / "DimCampanha.csv", ["CampanhaID","Campanha","CanalID","Objetivo"], CAMPAIGNS)
    write_csv(OUT / "DimCalendario.csv", ["Data","Ano","Mes","AnoMes"],
              [(f"2025-{m:02d}-01", 2025, m, f"2025-{m:02d}") for m in range(1, 13)])
    fact_path = OUT / "FatoMarketing.csv"
    with fact_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Gerados {len(rows)} registros em {fact_path}")

if __name__ == "__main__":
    main()
