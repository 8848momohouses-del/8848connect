from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    otif_score = fields.Float(
        string='PO OTIF Score',
        compute='_compute_otif_score',
        store=True,
        help="On-Time In-Full score for this specific Purchase Order."
    )

    @api.depends('picking_ids.state', 'picking_ids.is_on_time', 'picking_ids.is_in_full')
    def _compute_otif_score(self):
        for po in self:
            done_pickings = po.picking_ids.filtered(lambda p: p.state == 'done')
            if not done_pickings:
                po.otif_score = 100.0
                continue
            
            score = 0.0
            for picking in done_pickings:
                if picking.is_on_time and picking.is_in_full:
                    score += 100.0
                elif picking.is_on_time or picking.is_in_full:
                    score += 50.0
            
            po.otif_score = score / len(done_pickings)
