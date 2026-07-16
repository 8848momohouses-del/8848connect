from odoo.tests.common import TransactionCase

class TestDeliveryRouting(TransactionCase):

    def setUp(self):
        super(TestDeliveryRouting, self).setUp()
        
        self.driver = self.env['hr.employee'].create({
            'name': 'Test Driver'
        })
        
        self.partner = self.env['res.partner'].create({'name': 'Delivery Customer'})
        self.product = self.env['product.product'].create({'name': 'Momo', 'type': 'consu', 'is_storable': False})
        
        self.picking_type_out = self.env.ref('stock.picking_type_out')
        
        self.picking = self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.picking_type_out.id,
            'location_id': self.picking_type_out.default_location_src_id.id,
            'location_dest_id': self.partner.property_stock_customer.id,
        })
        
        move = self.env['stock.move'].create({
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'product_uom': self.product.uom_id.id,
            'picking_id': self.picking.id,
            'location_id': self.picking.location_id.id,
            'location_dest_id': self.picking.location_dest_id.id,
        })
        self.picking.action_confirm()

    def test_route_completion(self):
        # Assign picking to route
        route = self.env['8848.delivery.route'].create({
            'driver_id': self.driver.id,
            'picking_ids': [(4, self.picking.id)]
        })
        
        route.action_start_route()
        self.assertEqual(route.state, 'in_transit')
        
        # We need stock to validate, so we bypass strict validation for unit test or mock it.
        self.picking.action_assign()
        for move in self.picking.move_ids:
            move.quantity = 1
            move.picked = True
            
        route.action_done()
        self.assertEqual(route.state, 'done')
