from odoo import models, fields, api, exceptions, _

class PortalInviteWizard(models.TransientModel):
    _name = '8848.portal.invite.wizard'
    _description = 'Portal Invite Wizard'

    franchise_id = fields.Many2one('res.partner', string='Franchise', required=True, readonly=True)
    partner_id = fields.Many2one('res.partner', string='Contact to Invite', required=True, domain="[('parent_id', '=', franchise_id)]")
    portal_role = fields.Selection([
        ('owner', 'Franchise Owner'),
        ('manager', 'Store Manager'),
        ('accounts', 'Franchise Accounts'),
        ('read_only', 'Read-only Contact')
    ], string='Portal Role', required=True, default='owner')

    def action_invite(self):
        self.ensure_one()
        # Find or create user
        user = self.env['res.users'].search([('partner_id', '=', self.partner_id.id)], limit=1)
        if not user:
            user = self.env['res.users'].create({
                'name': self.partner_id.name,
                'login': self.partner_id.email or f"portal_{self.partner_id.id}",
                'partner_id': self.partner_id.id,
                'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
            })
            
        # Create access record
        existing = self.env['8848.franchise.access'].search([
            ('user_id', '=', user.id),
            ('franchise_id', '=', self.franchise_id.id)
        ])
        if not existing:
            self.env['8848.franchise.access'].create({
                'user_id': user.id,
                'franchise_id': self.franchise_id.id,
                'portal_role': self.portal_role,
                'state': 'invited',
                'invited_by': self.env.user.id,
                'invited_at': fields.Datetime.now()
            })
            
        # Standard Odoo password reset / portal invite email can be triggered here
        user.action_reset_password()
        
        return {'type': 'ir.actions.act_window_close'}
