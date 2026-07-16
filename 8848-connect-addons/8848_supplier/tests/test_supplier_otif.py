from odoo.tests.common import TransactionCase
from datetime import datetime, timedelta

class TestSupplierOTIF(TransactionCase):

    def setUp(self):
        super(TestSupplierOTIF, self).setUp()
        
        self.supplier = self.env['res.partner'].create({
            'name': 'Test Supplier',
            'is_supplier': True
        })
        
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'type': 'product'
        })

    def test_otif_calculation(self):
        # Create a PO
        po = self.env['purchase.order'].create({
            'partner_id': self.supplier.id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product.id,
                    'product_qty': 10,
                    'price_unit': 100.0,
                })
            ]
        })
        
        po.button_confirm()
        
        picking = po.picking_ids[0]
        
        # Test 1: On-Time and In-Full
        for move in picking.move_ids:
            move.quantity = 10
            
        picking._action_done()
        
        self.assertTrue(picking.is_on_time)
        self.assertTrue(picking.is_in_full)
        self.assertEqual(po.otif_score, 100.0)
        self.assertEqual(self.supplier.on_time_delivery_rate, 100.0)
