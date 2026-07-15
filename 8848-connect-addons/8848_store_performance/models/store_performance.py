from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StorePerformance(models.Model):
    _name = '8848.store.performance'
    _table = 'connect_store_performance'
    _description = 'Store Performance Metrics'
    _order = 'total_score desc'

    franchise_id = fields.Many2one('res.partner', string='Franchise', domain=[('is_franchise', '=', True)], required=True)
    period = fields.Char(string='Period (e.g., 2026-07)', required=True)
    
    monthly_sales = fields.Monetary(string='Monthly Sales', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', related='franchise_id.currency_id')
    
    customer_rating = fields.Float(string='Customer Rating (1-5)', default=5.0)
    compliance_score = fields.Float(string='Compliance Score (1-100)', default=100.0)

    total_score = fields.Float(string='Total Score', compute='_compute_total_score', store=True)

    @api.depends('monthly_sales', 'customer_rating', 'compliance_score')
    def _compute_total_score(self):
        for record in self:
            # Simple weighted score: 
            # 40% sales (normalized by an arbitrary 100k target for ranking), 
            # 30% rating, 30% compliance
            sales_score = min((record.monthly_sales / 100000) * 100, 100) * 0.4
            rating_score = (record.customer_rating / 5) * 100 * 0.3
            compliance = record.compliance_score * 0.3
            record.total_score = sales_score + rating_score + compliance

    def unlink(self):
        raise UserError(_("Store performance records cannot be deleted. Please archive them instead or contact the system administrator."))
