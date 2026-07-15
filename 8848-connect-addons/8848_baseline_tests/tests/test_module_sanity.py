from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install', 'baseline_8848')
class TestModuleSanity(TransactionCase):
    """The 8848 suite's structural contract: every baseline module is
    installed and every load-bearing model/field exists."""

    EXPECTED_MODULES = [
        '8848_core_branding', '8848_glass_skin', '8848_dashboard',
        '8848_franchise', '8848_royalty', '8848_marketing_fee',
        '8848_store_performance', '8848_factory', '8848_inventory',
        '8848_warehouse', '8848_quality', '8848_delivery', '8848_driver',
        '8848_portal', '8848_supplier', 'sign_oca', 'theme_liquid_glass',
    ]

    EXPECTED_MODELS = [
        '8848.franchise.stage', '8848.royalty.statement',
        '8848.marketing.fee.statement', '8848.store.performance',
        '8848.delivery.route',
    ]

    FRANCHISE_CORE_FIELDS = [
        'is_franchise', 'store_id', 'territory', 'franchise_status',
        'royalty_percentage', 'marketing_fee_percentage',
        'franchise_stage_id', 'franchise_approved', 'is_operational',
        'agreement_signed_date', 'deposit_received_date', 'grand_opening_date',
    ]

    def test_modules_installed(self):
        mods = self.env['ir.module.module'].search(
            [('name', 'in', self.EXPECTED_MODULES)])
        states = {m.name: m.state for m in mods}
        for name in self.EXPECTED_MODULES:
            self.assertEqual(states.get(name), 'installed',
                             f'module {name} must be installed')

    def test_models_exist(self):
        for model in self.EXPECTED_MODELS:
            self.assertIn(model, self.env,
                          f'model {model} must exist in the registry')

    def test_franchise_core_field_contract(self):
        partner_fields = self.env['res.partner']._fields
        for fname in self.FRANCHISE_CORE_FIELDS:
            self.assertIn(fname, partner_fields,
                          f'res.partner.{fname} is part of the frozen core contract')

    def test_lifecycle_stages_seeded(self):
        stages = self.env['8848.franchise.stage'].search([])
        self.assertGreaterEqual(len(stages), 15,
                                'the 15 lifecycle stages must be seeded')
        operational = stages.filtered('is_operational_stage')
        self.assertGreaterEqual(len(operational), 4,
                                'operational stages (Grand Opening onward) must be flagged')
