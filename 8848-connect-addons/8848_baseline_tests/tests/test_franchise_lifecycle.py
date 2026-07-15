from datetime import date

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install', 'baseline_8848')
class TestFranchiseLifecycle(TransactionCase):

    def test_new_franchise_defaults_to_inquiry_stage(self):
        partner = self.env['res.partner'].create({
            'name': 'Baseline Test Franchise',
            'is_franchise': True,
        })
        self.assertTrue(partner.franchise_stage_id, 'stage must auto-assign')
        self.assertEqual(partner.franchise_stage_id,
                         self.env.ref('8848_franchise.stage_franchise_inquiry'))

    def test_flag_flip_assigns_stage(self):
        partner = self.env['res.partner'].create({'name': 'Baseline Plain Contact'})
        self.assertFalse(partner.franchise_stage_id)
        partner.write({'is_franchise': True})
        self.assertTrue(partner.franchise_stage_id,
                        'flipping is_franchise must assign the default stage')

    def test_is_operational_gate(self):
        partner = self.env['res.partner'].create({
            'name': 'Baseline Gate Test',
            'is_franchise': True,
        })
        self.assertFalse(partner.is_operational)
        partner.write({
            'franchise_approved': True,
            'agreement_signed_date': date.today(),
            'deposit_received_date': date.today(),
        })
        self.assertFalse(partner.is_operational,
                         'three of four milestones must NOT open the gate')
        partner.write({'grand_opening_date': date.today()})
        self.assertTrue(partner.is_operational,
                        'all four milestones must open the gate')

    def test_defaults_preserved(self):
        partner = self.env['res.partner'].create({
            'name': 'Baseline Defaults', 'is_franchise': True,
        })
        self.assertEqual(partner.royalty_percentage, 5.0)
        self.assertEqual(partner.marketing_fee_percentage, 2.0)
        self.assertEqual(partner.franchise_status, 'active')
