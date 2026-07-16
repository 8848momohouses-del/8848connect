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

    def _update_supplier_otif(self):
        for partner in self:
            if not partner.is_supplier:
                continue
            
            # Fetch all done incoming pickings for this supplier linked to a PO
            pickings = self.env['stock.picking'].search([
                ('partner_id', '=', partner.id),
                ('picking_type_code', '=', 'incoming'),
                ('state', '=', 'done'),
                ('purchase_id', '!=', False)
            ])
            
            if not pickings:
                partner.on_time_delivery_rate = 100.0
                continue
            
            score = 0.0
            for picking in pickings:
                if picking.is_on_time and picking.is_in_full:
                    score += 100.0
                elif picking.is_on_time or picking.is_in_full:
                    score += 50.0
            
            partner.on_time_delivery_rate = score / len(pickings)
