from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_franchise = fields.Boolean(string='Is a Franchise', default=False)
    store_id = fields.Char(string='Store ID', help='Unique identifier for the franchise store')
    royalty_percentage = fields.Float(string='Royalty (%)', default=5.0)
    marketing_fee_percentage = fields.Float(string='Marketing Fee (%)', default=2.0)
    territory = fields.Char(string='Territory', help='Geographical territory assigned to this franchise')
    franchise_status = fields.Selection([
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('terminated', 'Terminated'),
    ], string='Franchise Status', default='active', tracking=True)
