from odoo.tests import common
from odoo.exceptions import UserError

class TestE2ELifecycle(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.supplier = self.env['res.partner'].create({'name': 'Test Supplier', 'supplier_rank': 1})
        self.franchise = self.env['res.partner'].create({
            'name': 'Test Franchise',
            'is_franchise': True,
            'customer_rank': 1
        })
        self.driver = self.env['res.users'].create({
            'name': 'Test Driver',
            'login': 'driver_e2e@test.com',
        })
        self.raw_material = self.env['product.product'].create({
            'name': 'Raw Material',
            'type': 'product'
        })
        self.finished_good = self.env['product.product'].create({
            'name': 'Finished Good',
            'type': 'product'
        })
        
    def test_end_to_end_supply_chain(self):
        # 1-4. PO and Confirm
        po = self.env['purchase.order'].create({
            'partner_id': self.supplier.id,
            'order_line': [(0, 0, {
                'product_id': self.raw_material.id,
                'product_qty': 100,
                'price_unit': 10.0,
            })]
        })
        po.button_confirm()
        
        # 5. Receive stock
        receipt = po.picking_ids[0]
        for move in receipt.move_ids:
            move.quantity = 100
        receipt.button_validate()
        
        self.assertEqual(self.raw_material.qty_available, 100)
        
        # 7-10. Manufacturing
        mo = self.env['mrp.production'].create({
            'product_id': self.finished_good.id,
            'product_qty': 10,
            'move_raw_ids': [(0, 0, {
                'product_id': self.raw_material.id,
                'product_uom_qty': 50,
            })]
        })
        mo.action_confirm()
        for move in mo.move_raw_ids:
            move.quantity = 50
        mo.qty_producing = 10
        mo.button_mark_done()
        
        self.assertEqual(self.raw_material.qty_available, 50)
        self.assertEqual(self.finished_good.qty_available, 10)
        
        # 12-14. Franchise Sale Order
        so = self.env['sale.order'].create({
            'partner_id': self.franchise.id,
            'order_line': [(0, 0, {
                'product_id': self.finished_good.id,
                'product_uom_qty': 5,
                'price_unit': 100.0,
            })]
        })
        
        so.action_approve_order()
        so.action_confirm()
        
        # 15-17. Picking and Packing
        delivery = so.picking_ids[0]
        delivery.action_assign() # reserve stock
        
        # Explicitly pack
        delivery.action_start_packing()
        delivery.action_mark_packed()
        
        # Record explicit picked quantities
        for move in delivery.move_ids:
            move.quantity = 5
            
        # 19-21. Delivery Route
        route = self.env['8848.delivery.route'].create({
            'driver_id': self.driver.id,
            'picking_ids': [(4, delivery.id)]
        })
        route.action_start_route()
        
        # 22-25. Delivery Completion
        # If we try to complete without quantities, it fails
        delivery.move_ids.quantity = 0
        with self.assertRaises(UserError):
            route.action_done()
            
        # Set exact quantities
        delivery.move_ids.quantity = 5
        route.action_done()
        
        self.assertEqual(delivery.state, 'done')
        self.assertEqual(route.state, 'done')
        self.assertEqual(route.invoice_status, 'created')
        
        # 28-29. Invoices
        self.assertTrue(so.invoice_ids)
        self.assertEqual(so.invoice_ids[0].state, 'draft')
        
        # 30. Communications
        messages = self.env['8848.communication.message'].search([('partner_id', '=', self.franchise.id)])
        self.assertTrue(len(messages) > 0)
