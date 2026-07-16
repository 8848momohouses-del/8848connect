from odoo import models, fields, api, exceptions, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    portal_access_ids = fields.One2many('8848.franchise.access', 'franchise_id', string='Portal Access')

    def action_invite_portal(self):
        self.ensure_one()
        if not self.is_franchise:
            raise exceptions.UserError(_("Can only invite to a franchise."))
            
        return {
            'name': _('Invite Portal User'),
            'type': 'ir.actions.act_window',
            'res_model': '8848.portal.invite.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_franchise_id': self.id,
            }
        }
