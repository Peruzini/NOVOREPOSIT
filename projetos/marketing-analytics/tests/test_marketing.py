import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACT = ROOT / "dados" / "tratados" / "FatoMarketing.csv"

class MarketingPortfolioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with FACT.open(encoding="utf-8") as stream:
            cls.rows = list(csv.DictReader(stream))

    def test_tem_96_linhas(self):
        self.assertEqual(len(self.rows), 96)

    def test_chaves_e_metricas_positivas(self):
        for row in self.rows:
            self.assertTrue(row["CampanhaID"].startswith("CMP"))
            self.assertTrue(row["CanalID"].startswith("CAN"))
            for field in ["InvestimentoCentavos","Impressoes","Cliques","Leads","Oportunidades","Clientes","ReceitaCentavos"]:
                self.assertGreater(int(row[field]), 0)

    def test_funil_nao_cresce(self):
        for row in self.rows:
            self.assertLessEqual(int(row["Leads"]), int(row["Cliques"]))
            self.assertLessEqual(int(row["Oportunidades"]), int(row["Leads"]))
            self.assertLessEqual(int(row["Clientes"]), int(row["Oportunidades"]))

    def test_totais_versionados(self):
        investimento = sum(int(r["InvestimentoCentavos"]) for r in self.rows) / 100
        receita = sum(int(r["ReceitaCentavos"]) for r in self.rows) / 100
        leads = sum(int(r["Leads"]) for r in self.rows)
        clientes = sum(int(r["Clientes"]) for r in self.rows)
        self.assertEqual(investimento, 536699.0)
        self.assertEqual(receita, 4843591.0)
        self.assertEqual(leads, 30933)
        self.assertEqual(clientes, 2360)

    def test_roas_global(self):
        investimento = sum(int(r["InvestimentoCentavos"]) for r in self.rows)
        receita = sum(int(r["ReceitaCentavos"]) for r in self.rows)
        self.assertAlmostEqual(receita / investimento, 9.024781115672, places=9)

if __name__ == "__main__":
    unittest.main()
