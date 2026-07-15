from odoo.tests.common import HttpCase, tagged


@tagged('post_install', '-at_install', 'baseline_8848')
class TestHttpRoutes(HttpCase):

    def test_login_page_served(self):
        response = self.url_open('/web/login')
        self.assertEqual(response.status_code, 200)

    def test_franchise_portal_requires_authentication(self):
        # Anonymous access to the franchise portal must land on login,
        # never expose franchise data.
        response = self.url_open('/my/franchise')
        self.assertEqual(response.status_code, 200)
        self.assertIn('login', response.url,
                      'anonymous /my/franchise must redirect to login')
