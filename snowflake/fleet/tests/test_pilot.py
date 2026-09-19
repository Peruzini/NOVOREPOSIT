import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pilot


def fixture(**changes):
    row = dict(zip(pilot.COLUMNS, ["2026-01-01", "A", "Asset A", "Truck", "North",
                                   10, 16, 24, 4, 0, 0, 60, 10, 40, 20]))
    row.update(changes)
    return row


def january(rows):
    db = pilot.connect_local(rows)
    try:
        query = (pilot.ROOT / "evaluation/queries/01_january_2026.sql").read_text()
        return dict(db.execute(query).fetchone())
    finally:
        db.close()


class FleetPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = pilot.generate_rows()

    def test_calendar_and_grain(self):
        self.assertEqual(len(self.rows), 5840)
        self.assertEqual(self.rows[0]["DATA"], "2025-01-01")
        self.assertEqual(self.rows[-1]["DATA"], "2026-12-31")
        self.assertEqual(len({(r['DATA'], r['EQUIPAMENTO_ID']) for r in self.rows}), 5840)

    def test_operation_never_exceeds_available_hours(self):
        pilot.validate_rows(self.rows)
        self.assertTrue(any(r['HORAS_MANUTENCAO'] > 0 for r in self.rows))

    def test_known_synthetic_rows_and_rounding(self):
        first = self.rows[0]
        self.assertEqual(first['PRODUCAO_TON'], 110.2)  # 147 * 15 / 20 -> half-even
        self.assertEqual(first['CUSTO_COMBUSTIVEL'], 5547.60)  # 1035 * 5.36
        selected = {r['DATA']: r for r in self.rows if r['EQUIPAMENTO_ID'] == 'EQ-01'}
        self.assertEqual(selected['2025-01-07']['HORAS_MANUTENCAO'], 3)
        self.assertEqual(selected['2025-01-07']['FALHAS'], 0)  # inspection
        self.assertEqual(selected['2025-02-04']['HORAS_CORRETIVAS'], 3)
        self.assertEqual(selected['2025-02-04']['FALHAS'], 1)

    def test_weighted_ratios_and_corrective_only_mttr(self):
        # Unequal tons and hours expose AVG(ratio) and preventive-as-failure bugs.
        result = january([fixture(), fixture(EQUIPAMENTO_ID='B', EQUIPAMENTO='Asset B',
                          PRODUCAO_TON=90, HORAS_OPERACAO=12, HORAS_MANUTENCAO=6,
                          HORAS_CORRETIVAS=6, FALHAS=1, CUSTO_MANUTENCAO=160,
                          CUSTO_COMBUSTIVEL=40, META_PRODUCAO_TON=80)])
        self.assertEqual(result['PRODUCAO_TON'], 100)
        self.assertEqual(result['CUSTO_POR_TONELADA'], 3)
        self.assertEqual(result['FALHAS'], 1)
        self.assertEqual(result['MTTR'], 6)
        self.assertEqual(result['MTBF'], 28)
        self.assertAlmostEqual(result['DISPONIBILIDADE'], 38/48)
        self.assertAlmostEqual(result['UTILIZACAO'], 28/38)

    def test_no_failure_has_null_reliability_metrics(self):
        result = january([fixture()])
        self.assertEqual(result['FALHAS'], 0)
        self.assertIsNone(result['MTTR'])
        self.assertIsNone(result['MTBF'])

    def test_zero_production_is_not_division_error(self):
        result = january([fixture(PRODUCAO_TON=0)])
        self.assertEqual(result['PRODUCAO_TON'], 0)
        self.assertIsNone(result['CUSTO_POR_TONELADA'])

    def test_empty_period_does_not_fabricate_production(self):
        result = january([fixture(DATA='2025-12-31')])
        self.assertIsNone(result['PRODUCAO_TON'])
        self.assertEqual(result['FALHAS'], 0)
        self.assertIsNone(result['MTTR'])

    def test_month_boundaries(self):
        result = january([fixture(DATA='2025-12-31', PRODUCAO_TON=999),
                          fixture(), fixture(DATA='2026-01-31', PRODUCAO_TON=20),
                          fixture(DATA='2026-02-01', PRODUCAO_TON=999)])
        self.assertEqual(result['PRODUCAO_TON'], 30)

    def test_duplicates_and_impossible_hours_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            pilot.validate_rows([fixture(), fixture()])
        with self.assertRaisesRegex(ValueError, 'exceeds'):
            pilot.validate_rows([fixture(HORAS_OPERACAO=24)])

    def test_grouped_totals_reconcile_and_top5_is_deterministic(self):
        db = pilot.connect_local(self.rows)
        try:
            results = pilot.run_queries(db)
        finally:
            db.close()
        total = results['01_january_2026'][0]['PRODUCAO_TON']
        self.assertAlmostEqual(sum(r['PRODUCAO_TON'] for r in results['02_equipment_january']), total)
        top = results['03_top5_maintenance']
        self.assertEqual(len(top), 5)
        self.assertEqual(top, sorted(top, key=lambda r: (-r['HORAS_MANUTENCAO'], r['EQUIPAMENTO_ID'])))

    def test_render_rejects_invalid_identifiers(self):
        with self.assertRaises(ValueError):
            pilot.render_sql('DB; DROP DATABASE X', 'PILOT', 'WH')
        for sql in pilot.render_sql('DB', 'PILOT', 'WH').values():
            self.assertNotIn('__DATABASE__', sql)
            self.assertNotIn('__SCHEMA__', sql)
            self.assertNotIn('__WAREHOUSE__', sql)


if __name__ == '__main__':
    unittest.main()
