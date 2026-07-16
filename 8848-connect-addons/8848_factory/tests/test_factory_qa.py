from odoo.tests.common import TransactionCase

class TestFactoryQA(TransactionCase):

    def setUp(self):
        super(TestFactoryQA, self).setUp()
        self.product = self.env['product.product'].create({
            'name': 'Momo',
            'type': 'consu',
            'is_storable': True,
            'tracking': 'lot',
        })
        self.bom = self.env['mrp.bom'].create({
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'product_qty': 1.0,
        })

    def test_waste_computation(self):
        production = self.env['mrp.production'].create({
            'product_id': self.product.id,
            'product_qty': 10,
            'bom_id': self.bom.id,
        })
        production.action_confirm()
        
        # Add scrap
        scrap_loc = self.env['stock.location'].search([('scrap_location', '=', True)], limit=1)
        scrap = self.env['stock.scrap'].create({
            'production_id': production.id,
            'product_id': self.product.id,
            'scrap_qty': 2.0,
            'product_uom_id': self.product.uom_id.id,
            'location_id': production.location_src_id.id,
            'scrap_location_id': scrap_loc.id,
        })
        scrap.action_validate()
        
        self.assertEqual(production.waste_quantity, 2.0)
