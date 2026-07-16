from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_on_time = fields.Boolean(
        string='Is On Time',
        compute='_compute_otif_metrics',
        store=True
    )
    is_in_full = fields.Boolean(
        string='Is In Full',
        compute='_compute_otif_metrics',
        store=True
    )

    @api.depends('state', 'date_done', 'scheduled_date', 'move_ids.quantity', 'move_ids.product_uom_qty')
    def _compute_otif_metrics(self):
        for picking in self:
            if picking.state != 'done':
                picking.is_on_time = False
                picking.is_in_full = False
                continue
                
            # On time: date_done is before or on scheduled_date
            if picking.date_done and picking.scheduled_date:
                picking.is_on_time = picking.date_done <= picking.scheduled_date
            else:
                picking.is_on_time = True
                
            # In full: all moves have quantity == product_uom_qty (no backorders needed)
            in_full = True
            for move in picking.move_ids:
                if move.quantity < move.product_uom_qty:
                    in_full = False
                    break
            picking.is_in_full = in_full

    def _action_done(self):
        res = super(StockPicking, self)._action_done()
        for picking in self.filtered(lambda p: p.picking_type_code == 'incoming' and p.partner_id and p.partner_id.is_supplier):
            picking.partner_id._update_supplier_otif()
        return res
