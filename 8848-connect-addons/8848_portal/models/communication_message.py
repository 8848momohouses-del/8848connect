from odoo import models, fields

class CommunicationMessage(models.Model):
    _inherit = '8848.communication.message'

    portal_visibility = fields.Boolean(string='Visible in Portal', default=False, tracking=True)
