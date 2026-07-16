from odoo.tests import common
from odoo.exceptions import UserError

class TestPacking(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({'name': 'Test Partner'})
        self.product = self.env['product.product'].create({'name': 'Test Product', 'type': 'product'})
        picking_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)
        location = self.env['stock.location'].search([('usage', '=', 'internal')], limit=1)
        dest_location = self.env['stock.location'].search([('usage', '=', 'customer')], limit=1)
        
        self.picking = self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': picking_type.id,
            'location_id': location.id,
            'location_dest_id': dest_location.id,
        })
        self.move = self.env['stock.move'].create({
            'name': 'Test Move',
            'product_id': self.product.id,
            'product_uom_qty': 10,
            'product_uom': self.product.uom_id.id,
            'picking_id': self.picking.id,
            'location_id': location.id,
            'location_dest_id': dest_location.id,
        })

    def test_packing_workflow(self):
        # Update picking to assigned state (mocking availability)
        self.picking.state = 'assigned'
        self.assertEqual(self.picking.packing_status, 'pending')
        
        self.picking.action_start_packing()
        self.assertEqual(self.picking.packing_status, 'packing')
        
        self.picking.action_finish_packing()
        self.assertEqual(self.picking.packing_status, 'packed')
