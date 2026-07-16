from odoo.tests import common
from odoo.exceptions import UserError

class TestSaleApproval(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.stage_operational = self.env['8848.franchise.stage'].create({
            'name': 'Operational Test',
            'code': 'operational'
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Test Franchise',
            'is_franchise': True,
            'franchise_stage_id': self.stage_operational.id
        })
        self.product = self.env['product.product'].create({
            'name': 'Momo',
            'type': 'consu'
        })

    def test_sale_approval(self):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 10
            })]
        })
        self.assertEqual(order.approval_state, 'draft')
        
        order.action_approve_order()
        self.assertEqual(order.approval_state, 'approved')
        
        # Test confirmation works after approval
        order.action_confirm()
        self.assertEqual(order.state, 'sale')
