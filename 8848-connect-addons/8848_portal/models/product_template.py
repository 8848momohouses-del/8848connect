from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_portal_orderable = fields.Boolean(string='Portal Orderable', default=False, tracking=True, help="If checked, this product will appear in the Franchise Portal catalogue.")
