from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_supplier = fields.Boolean(string='Is a Supplier', default=False)
    quality_rating = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('poor', 'Poor')
    ], string='Quality Rating')
    on_time_delivery_rate = fields.Float(string='On-Time Delivery (%)', default=100.0)
