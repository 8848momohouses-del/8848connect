from odoo.tests.common import TransactionCase

class TestCrmIntake(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Lead = self.env['crm.lead']
        self.Partner = self.env['res.partner']

    def test_new_enquiry_creation(self):
        """Test a clean new enquiry."""
        payload = {
            'contact_name': 'Test User',
            'email_from': 'test@8848.com ',
            'franchise_territory_interest': 'Sydney CBD',
            'external_entry_id': 'GF_123',
        }
        res = self.Lead.create_or_update_franchise_enquiry(payload)
        
        self.assertTrue(res['success'])
        self.assertEqual(res['status'], 'created')
        self.assertTrue(res['reference'].startswith('FRQ-'))
        
        lead = self.Lead.browse(res['lead_id'])
        self.assertEqual(lead.email_from, 'test@8848.com')
        self.assertEqual(lead.contact_name, 'Test User')
        
    def test_idempotency(self):
        """Test exactly same external ID is idempotent."""
        payload = {
            'contact_name': 'Test User',
            'email_from': 'test@8848.com',
            'external_entry_id': 'GF_456',
        }
        res1 = self.Lead.create_or_update_franchise_enquiry(payload)
        res2 = self.Lead.create_or_update_franchise_enquiry(payload)
        
        self.assertEqual(res2['status'], 'idempotent')
        self.assertEqual(res1['lead_id'], res2['lead_id'])

    def test_duplicate_email_territory(self):
        """Test same email + territory updates existing open lead."""
        payload1 = {
            'contact_name': 'Duplicate User',
            'email_from': 'dup@8848.com',
            'franchise_territory_interest': 'Melbourne',
            'external_entry_id': 'GF_1',
        }
        payload2 = {
            'contact_name': 'Duplicate User',
            'email_from': 'dup@8848.com',
            'franchise_territory_interest': 'Melbourne',
            'external_entry_id': 'GF_2',
            'message': 'Following up!'
        }
        res1 = self.Lead.create_or_update_franchise_enquiry(payload1)
        res2 = self.Lead.create_or_update_franchise_enquiry(payload2)
        
        self.assertEqual(res2['status'], 'updated')
        self.assertEqual(res1['lead_id'], res2['lead_id'])
        
        lead = self.Lead.browse(res1['lead_id'])
        self.assertEqual(lead.description, 'Following up!')

    def test_expansion_enquiry(self):
        """Test existing partner receives an expansion enquiry."""
        partner = self.Partner.create({
            'name': 'Existing Franchisee',
            'email': 'existing@8848.com',
            'is_franchise': True
        })
        
        payload = {
            'contact_name': 'Existing Franchisee',
            'email_from': 'existing@8848.com',
            'franchise_territory_interest': 'Brisbane',
        }
        res = self.Lead.create_or_update_franchise_enquiry(payload)
        
        self.assertEqual(res['status'], 'created')
        lead = self.Lead.browse(res['lead_id'])
        self.assertEqual(lead.partner_id.id, partner.id)
        self.assertTrue('Expansion Enquiry' in lead.name)

    def test_submit_application(self):
        """Test that submitting an application links and scores correctly."""
        payload = {
            'contact_name': 'Applicant',
            'email_from': 'applicant@8848.com',
        }
        res = self.Lead.create_or_update_franchise_enquiry(payload)
        lead = self.Lead.browse(res['lead_id'])
        
        app = lead.submit_franchise_application({
            'business_experience': 'Ran a cafe',
            'hospitality_experience': True,
            'total_assets': 600000,
            'investment_available': 550000,
            'finance_required': False,
        })
        
        self.assertEqual(app.version, 1)
        self.assertEqual(app.status, 'submitted')
        # Score calculation check: 
        # Business(20) + Hosp(20) + Inv>500k(40) + NoFinance(10) = 90
        # Mobile(0) + Territory(0) = 90 total
        self.assertEqual(lead.franchise_score, 90)
        self.assertEqual(lead.franchise_score_category, 'hot')

    def test_convert_to_franchise(self):
        """Test converting a lead creates a franchise partner."""
        payload = {
            'contact_name': 'To Convert',
            'email_from': 'convert@8848.com',
            'franchise_territory_interest': 'Perth CBD'
        }
        res = self.Lead.create_or_update_franchise_enquiry(payload)
        lead = self.Lead.browse(res['lead_id'])
        
        # Add an application
        app = lead.submit_franchise_application({})
        
        lead.action_convert_to_franchise()
        
        partner = lead.partner_id
        self.assertTrue(partner)
        self.assertTrue(partner.is_franchise)
        self.assertEqual(partner.territory, 'Perth CBD')
        
        # Check application is linked
        self.assertEqual(app.partner_id.id, partner.id)
        
        # Check it is NOT operational yet
        self.assertFalse(partner.is_operational)
