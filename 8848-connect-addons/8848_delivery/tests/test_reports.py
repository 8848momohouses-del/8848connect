from odoo.tests import common

class TestReports(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env['res.partner'].create({'name': 'Test Franchise'})
        self.product = self.env['product.product'].create({'name': 'Test Product', 'type': 'consu', 'is_storable': True})
        self.picking = self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
            'move_ids': [(0, 0, {
                'name': 'Test Move',
                'product_id': self.product.id,
                'product_uom': self.product.uom_id.id,
                'product_uom_qty': 1.0,
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'location_dest_id': self.env.ref('stock.stock_location_customers').id,
            })]
        })

    def test_render_packing_slip(self):
        report = self.env.ref('8848_delivery.action_report_packing_slip')
        pdf, _ = report._render_qweb_pdf(self.picking.ids)
        self.assertTrue(pdf, "PDF rendering failed for packing slip")

    def test_render_delivery_slip(self):
        report = self.env.ref('8848_delivery.action_report_delivery_slip')
        pdf, _ = report._render_qweb_pdf(self.picking.ids)
        self.assertTrue(pdf, "PDF rendering failed for delivery slip")
