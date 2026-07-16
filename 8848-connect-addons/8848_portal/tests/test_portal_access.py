from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError

class TestFranchisePortalAccess(TransactionCase):
    
    def setUp(self):
        super(TestFranchisePortalAccess, self).setUp()
        self.portal_group = self.env.ref('base.group_portal')
        
        # Create test franchises
        self.franchise_a = self.env['res.partner'].create({'name': 'Store A', 'is_franchise': True, 'is_operational': True})
        self.franchise_b = self.env['res.partner'].create({'name': 'Store B', 'is_franchise': True, 'is_operational': True})
        
        # Create test users
        self.user_a = self.env['res.users'].create({
            'name': 'User A',
            'login': 'user_a@test.com',
            'groups_id': [(6, 0, [self.portal_group.id])]
        })
        self.user_b = self.env['res.users'].create({
            'name': 'User B',
            'login': 'user_b@test.com',
            'groups_id': [(6, 0, [self.portal_group.id])]
        })
        
        # Create Access records
        self.env['8848.franchise.access'].create({
            'user_id': self.user_a.id,
            'franchise_id': self.franchise_a.id,
            'portal_role': 'owner',
            'state': 'active'
        })
        
        self.env['8848.franchise.access'].create({
            'user_id': self.user_b.id,
            'franchise_id': self.franchise_b.id,
            'portal_role': 'owner',
            'state': 'active'
        })

    def test_permitted_franchises(self):
        # User A should only see Store A
        permitted_a = self.user_a._get_permitted_franchise_ids()
        self.assertEqual(permitted_a, [self.franchise_a.id])
        
        # User B should only see Store B
        permitted_b = self.user_b._get_permitted_franchise_ids()
        self.assertEqual(permitted_b, [self.franchise_b.id])

    def test_ticket_cross_franchise_isolation(self):
        # Create tickets for both stores
        ticket_a = self.env['8848.support.ticket'].create({
            'name': 'Issue A',
            'description': 'Desc',
            'category': 'other',
            'franchise_id': self.franchise_a.id
        })
        ticket_b = self.env['8848.support.ticket'].create({
            'name': 'Issue B',
            'description': 'Desc',
            'category': 'other',
            'franchise_id': self.franchise_b.id
        })
        
        # User A checks tickets
        ticket_env_a = self.env['8848.support.ticket'].with_user(self.user_a)
        tickets_visible_a = ticket_env_a.search([])
        
        self.assertIn(ticket_a, tickets_visible_a)
        self.assertNotIn(ticket_b, tickets_visible_a)
