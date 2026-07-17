from odoo import models, fields, api, exceptions, _

class FranchiseAccess(models.Model):
    _name = '8848.franchise.access'
    _table = 'connect_franchise_access'
    _description = 'Franchise Portal Access'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    user_id = fields.Many2one('res.users', string='Portal User', required=True, ondelete='cascade', tracking=True)
    franchise_id = fields.Many2one('res.partner', string='Franchise Master', required=True, domain=[('is_franchise', '=', True)], ondelete='cascade', tracking=True)
    
    portal_role = fields.Selection([
        ('owner', 'Franchise Owner'),
        ('manager', 'Store Manager'),
        ('accounts', 'Franchise Accounts'),
        ('read_only', 'Read-only Contact')
    ], string='Portal Role', required=True, default='owner', tracking=True)
    
    state = fields.Selection([
        ('invited', 'Invited'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('revoked', 'Revoked')
    ], string='Status', default='invited', tracking=True, required=True)

    invited_by = fields.Many2one('res.users', string='Invited By', readonly=True, copy=False)
    invited_at = fields.Datetime(string='Invited At', readonly=True, copy=False)
    activated_at = fields.Datetime(string='Activated At', readonly=True, copy=False)
    suspended_by = fields.Many2one('res.users', string='Suspended By', readonly=True, copy=False)
    suspended_at = fields.Datetime(string='Suspended At', readonly=True, copy=False)
    suspension_reason = fields.Char(string='Suspension Reason', copy=False, tracking=True)
    revoked_by = fields.Many2one('res.users', string='Revoked By', readonly=True, copy=False)
    revoked_at = fields.Datetime(string='Revoked At', readonly=True, copy=False)
    
    _sql_constraints = [
        ('user_franchise_uniq', 'unique(user_id, franchise_id)', 'A user can only have one access record per franchise.')
    ]

    def action_activate(self):
        for record in self:
            record.write({
                'state': 'active',
                'activated_at': fields.Datetime.now()
            })

    def action_suspend(self, reason=None):
        for record in self:
            record.write({
                'state': 'suspended',
                'suspended_by': self.env.user.id,
                'suspended_at': fields.Datetime.now(),
                'suspension_reason': reason or 'Suspended by admin'
            })

    def action_revoke(self):
        for record in self:
            record.write({
                'state': 'revoked',
                'revoked_by': self.env.user.id,
                'revoked_at': fields.Datetime.now()
            })

class ResUsers(models.Model):
    _inherit = 'res.users'

    def _get_permitted_franchise_ids(self, required_operations=None):
        """
        Returns a list of franchise res.partner IDs that this user has active access to.
        required_operations can be used to filter by role if needed (e.g., 'finance' requires owner/accounts).
        """
        self.ensure_one()
        domain = [
            ('user_id', '=', self.id),
            ('state', '=', 'active'),
            ('franchise_id.is_operational', '=', True)
        ]
        
        access_records = self.env['8848.franchise.access'].sudo().search(domain)
        
        if required_operations:
            filtered_records = self.env['8848.franchise.access'].sudo()
            for record in access_records:
                if required_operations == 'finance' and record.portal_role not in ['owner', 'accounts']:
                    continue
                if required_operations == 'order' and record.portal_role not in ['owner', 'manager']:
                    continue
                filtered_records |= record
            access_records = filtered_records
            
        return access_records.mapped('franchise_id').ids
