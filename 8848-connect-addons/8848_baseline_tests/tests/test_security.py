from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError, UserError

class TestSecurityEffectivePermissions(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        
        # Create users
        cls.user_internal = cls.env['res.users'].create({
            'name': 'Internal User',
            'login': 'internal',
            'group_ids': [(6, 0, [cls.env.ref('base.group_user').id])]
        })
        
        cls.user_acc_manager = cls.env['res.users'].create({
            'name': 'Accounts Manager',
            'login': 'acc_mgr',
            'group_ids': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('8848_security.group_8848_acc_manager').id
            ])]
        })
        
        cls.user_ops_manager = cls.env['res.users'].create({
            'name': 'Ops Manager',
            'login': 'ops_mgr',
            'group_ids': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('8848_security.group_8848_ops_manager').id
            ])]
        })
        
        cls.user_gm = cls.env['res.users'].create({
            'name': 'General Manager',
            'login': 'gm_user',
            'group_ids': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('8848_security.group_8848_gm').id
            ])]
        })
        
        cls.user_ceo = cls.env['res.users'].create({
            'name': 'CEO',
            'login': 'ceo_user',
            'group_ids': [(6, 0, [
                cls.env.ref('base.group_user').id,
                cls.env.ref('8848_security.group_8848_ceo').id
            ])]
        })
        
        # Create test franchise
        cls.franchise = cls.env['res.partner'].create({
            'name': 'Test Franchise',
            'is_franchise': True,
        })
        
        # Create test royalty statement (draft)
        cls.royalty = cls.env['8848.royalty.statement'].create({
            'franchise_id': cls.franchise.id,
            'date_start': '2026-01-01',
            'date_end': '2026-01-31',
            'total_sales': 1000,
        })
        
        # Create test franchise stage
        cls.franchise_stage = cls.env['8848.franchise.stage'].create({
            'name': 'Test Stage',
            'sequence': 10,
        })

    def test_01_internal_user_readonly(self):
        """Internal user can read but not write or delete royalty statements."""
        # Read should succeed
        self.royalty.with_user(self.user_internal).read(['name'])
        
        # Write should fail
        with self.assertRaises(AccessError):
            self.royalty.with_user(self.user_internal).write({'total_sales': 2000})
            
        # Unlink should fail
        with self.assertRaises(AccessError):
            self.royalty.with_user(self.user_internal).unlink()

    def test_02_accounts_manager_access(self):
        """Accounts manager can write and delete draft royalties."""
        # Write should succeed
        self.royalty.with_user(self.user_acc_manager).write({'total_sales': 2000})
        
        # Unlink draft should succeed
        self.royalty.with_user(self.user_acc_manager).unlink()

    def test_03_unlink_guard(self):
        """No one can delete an invoiced statement."""
        statement = self.env['8848.royalty.statement'].create({
            'franchise_id': self.franchise.id,
            'date_start': '2026-02-01',
            'date_end': '2026-02-28',
            'total_sales': 1000,
            'state': 'invoiced',
        })
        
        with self.assertRaises(UserError):
            statement.with_user(self.user_acc_manager).unlink()
            
    def test_04_ops_manager_cannot_write_royalties(self):
        """Ops manager can read but not write royalties."""
        # Read should succeed
        self.royalty.with_user(self.user_ops_manager).read(['name'])
        
        # Write should fail
        with self.assertRaises(AccessError):
            self.royalty.with_user(self.user_ops_manager).write({'total_sales': 3000})
            
    def test_05_executive_permissions(self):
        """Verify GM and CEO broad access without relying on base system groups or inheriting all departments."""
        # Ensure neither has base.group_system
        self.assertFalse(self.user_gm.has_group('base.group_system'))
        self.assertFalse(self.user_ceo.has_group('base.group_system'))
        
        # Ensure they do not inherit ops_manager directly (they only get what we granted via ir.model.access.csv)
        self.assertFalse(self.user_gm.has_group('8848_security.group_8848_ops_manager'))
        self.assertFalse(self.user_ceo.has_group('8848_security.group_8848_ops_manager'))
        
        # GM Operational write access (Franchise Stage)
        self.franchise_stage.with_user(self.user_gm).write({'name': 'GM Stage Update'})
        
        # GM Financial read-only access (Royalty Statement)
        self.royalty.with_user(self.user_gm).read(['name'])
        with self.assertRaises(AccessError):
            self.royalty.with_user(self.user_gm).write({'total_sales': 9999})
            
        # CEO Broad write access (Franchise Stage AND Royalty Statement)
        self.franchise_stage.with_user(self.user_ceo).write({'name': 'CEO Stage Update'})
        self.royalty.with_user(self.user_ceo).write({'total_sales': 5000})
        
        # CEO Unlink safe financial (draft)
        self.royalty.with_user(self.user_ceo).unlink()
