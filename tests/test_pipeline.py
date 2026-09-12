import sqlite3
import unittest
from datetime import date

from pipeline import ROOT, calendar, clean_projects, clean_sales, install_tables


class CommercialTests(unittest.TestCase):
    def setUp(self):
        self.shops = [{"LojaID": "L01", "Loja": "Exemplo", "UF": "MG"}]
        self.products = [{"ProdutoID": "P01", "Produto": "Exemplo", "Categoria": "Casa"}]
        self.sellers = [{"VendedorID": "VND01", "Vendedor": "Exemplo"}]
        self.row = {"VendaID": "V001", "Data": "2025-01-01", "LojaID": "L01", "ProdutoID": "P01",
                    "VendedorID": "VND01", "Quantidade": 2, "PrecoUnitarioCentavos": 10000,
                    "CustoUnitarioCentavos": 6000, "DescontoPct": 10, "Status": "Concluida"}

    def clean(self, rows):
        return clean_sales(rows, self.shops, self.products, self.sellers)

    def test_money_and_sql_reconciliation(self):
        rows, rejected = self.clean([self.row])
        self.assertEqual(rejected, [])
        self.assertEqual(rows[0]["ReceitaLiquidaCentavos"], 18000)
        self.assertEqual(rows[0]["LucroBrutoCentavos"], 6000)
        with sqlite3.connect(":memory:") as connection:
            install_tables(connection, (ROOT / "projetos/analise-comercial/sql/modelo.sql").read_text(),
                           {"DimCalendario": calendar(), "DimLoja": self.shops,
                            "DimProduto": self.products, "DimVendedor": self.sellers, "FatoVendas": rows})
            value = connection.execute("SELECT SUM(ReceitaLiquidaCentavos) / 100.0 FROM FatoVendas").fetchone()[0]
            self.assertEqual(value, 180.0)

    def test_identical_duplicate_is_not_double_counted(self):
        rows, rejected = self.clean([self.row, self.row])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rejected[0]["Motivo"], "duplicata_identica")

    def test_conflicting_id_quarantines_both_rows(self):
        rows, rejected = self.clean([self.row, {**self.row, "Quantidade": 9}])
        self.assertEqual(rows, [])
        self.assertEqual([r["Motivo"] for r in rejected], ["id_conflitante", "id_conflitante"])

    def test_invalid_foreign_key_and_cancelled_sale_have_distinct_reasons(self):
        rows, rejected = self.clean([{**self.row, "LojaID": "L99"},
                                     {**self.row, "VendaID": "V002", "Status": "Cancelada"}])
        self.assertEqual(rows, [])
        self.assertEqual({r["Motivo"] for r in rejected}, {"chave_LojaID_invalida", "venda_cancelada"})

    def test_fractional_quantity_is_rejected(self):
        rows, rejected = self.clean([{**self.row, "Quantidade": "1.5"}])
        self.assertEqual(rows, [])
        self.assertEqual(rejected[0]["Motivo"], "numero_invalido")


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.teams = [{"EquipeID": "E01", "Equipe": "BI"}]
        self.row = {"DemandaID": "D001", "DataCriacao": "2025-12-01", "DataInicio": "2025-12-03",
                    "DataConclusao": "2025-12-10", "DataPrazo": "2025-12-10", "EquipeID": "E01",
                    "TipoDemanda": "Dashboard", "Prioridade": "Alta", "Status": "Concluida",
                    "EsforcoPlanejadoHoras": 8, "EsforcoRealHoras": 10}

    def test_on_deadline_is_on_time_and_cycle_excludes_queue(self):
        rows, rejected = clean_projects([self.row], self.teams)
        self.assertEqual(rejected, [])
        self.assertEqual(rows[0]["EntregueNoPrazo"], 1)
        self.assertEqual(rows[0]["TempoCicloDias"], 7)
        self.assertEqual(rows[0]["LeadTimeDias"], 9)
        self.assertEqual(rows[0]["EmAtraso"], 0)

    def test_open_overdue_is_not_a_completed_late_delivery(self):
        rows, rejected = clean_projects([{**self.row, "Status": "Em andamento", "DataConclusao": ""}], self.teams)
        self.assertEqual(rejected, [])
        self.assertEqual(rows[0]["EmAtraso"], 1)
        self.assertIsNone(rows[0]["EntregueNoPrazo"])
        self.assertIsNone(rows[0]["TempoCicloDias"])

    def test_snapshot_reference_is_respected(self):
        raw = {**self.row, "Status": "Em andamento", "DataConclusao": ""}
        rows, _ = clean_projects([raw], self.teams, date(2025, 12, 10))
        self.assertEqual(rows[0]["EmAtraso"], 0)

    def test_concluded_without_end_date_is_rejected(self):
        rows, rejected = clean_projects([{**self.row, "DataConclusao": ""}], self.teams)
        self.assertEqual(rows, [])
        self.assertEqual(rejected[0]["Motivo"], "conclusao_sem_datas")


if __name__ == "__main__":
    unittest.main()
