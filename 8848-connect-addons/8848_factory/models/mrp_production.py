from odoo import models, fields, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    batch_temperature = fields.Float(string='Batch Temperature (°C)', tracking=True)
    qa_supervisor_id = fields.Many2one('hr.employee', string='QA Supervisor', tracking=True)
    
    waste_quantity = fields.Float(
        string='Total Waste Logged',
        compute='_compute_waste_quantity',
        help="Total quantity scrapped for this manufacturing order."
    )

    @api.depends('scrap_ids.scrap_qty')
    def _compute_waste_quantity(self):
        for production in self:
            production.waste_quantity = sum(production.scrap_ids.mapped('scrap_qty'))
