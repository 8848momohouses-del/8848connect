from odoo.tests import common

class TestDelivery(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.driver = self.env['res.users'].create({
            'name': 'Test Driver',
            'login': 'driver@test.com'
        })
        self.route = self.env['8848.delivery.route'].create({
            'driver_id': self.driver.id
        })

    def test_delivery_workflow(self):
        self.assertEqual(self.route.state, 'draft')
        
        self.route.action_start_route()
        self.assertEqual(self.route.state, 'in_transit')
        
        self.route.action_done()
        self.assertEqual(self.route.state, 'done')
