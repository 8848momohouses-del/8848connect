from datetime import date

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install', 'baseline_8848')
class TestFinancialStatements(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.franchise = cls.env['res.partner'].create({
            'name': 'Baseline Financial Franchise',
            'is_franchise': True,
            'royalty_percentage': 5.0,
            'marketing_fee_percentage': 2.0,
        })

    def _has_chart_of_accounts(self):
        return bool(self.env['account.journal'].search(
            [('type', '=', 'sale')], limit=1))

    def test_royalty_amount_compute(self):
        statement = self.env['8848.royalty.statement'].create({
            'franchise_id': self.franchise.id,
            'date_start': date(2026, 7, 1),
            'date_end': date(2026, 7, 31),
            'total_sales': 100000.0,
        })
        self.assertEqual(statement.royalty_amount, 5000.0)
        self.assertNotEqual(statement.name, 'New', 'sequence must assign a reference')

    def test_marketing_fee_compute(self):
        statement = self.env['8848.marketing.fee.statement'].create({
            'franchise_id': self.franchise.id,
            'date_start': date(2026, 7, 1),
            'date_end': date(2026, 7, 31),
            'total_sales': 100000.0,
        })
        self.assertEqual(statement.marketing_fee_amount, 2000.0)

    def test_royalty_invoice_generation(self):
        if not self._has_chart_of_accounts():
            self.skipTest('no chart of accounts configured (fresh CI database)')
        statement = self.env['8848.royalty.statement'].create({
            'franchise_id': self.franchise.id,
            'date_start': date(2026, 7, 1),
            'date_end': date(2026, 7, 31),
            'total_sales': 50000.0,
        })
        statement.action_generate_invoice()
        self.assertEqual(statement.state, 'invoiced')
        self.assertTrue(statement.invoice_id)
        self.assertEqual(statement.invoice_id.amount_untaxed, 2500.0)

    def test_store_performance_score(self):
        perf = self.env['8848.store.performance'].create({
            'franchise_id': self.franchise.id,
            'period': '2026-07',
            'monthly_sales': 100000.0,
            'customer_rating': 5.0,
            'compliance_score': 100.0,
        })
        self.assertEqual(perf.total_score, 100.0,
                         'perfect inputs must score 100 (40+30+30 weighting)')

    def test_smart_button_counts(self):
        self.env['8848.royalty.statement'].create({
            'franchise_id': self.franchise.id,
            'date_start': date(2026, 7, 1),
            'date_end': date(2026, 7, 31),
            'total_sales': 1000.0,
        })
        self.assertEqual(self.franchise.royalty_statement_count, 1)
        self.assertEqual(self.franchise.marketing_fee_statement_count, 0)
