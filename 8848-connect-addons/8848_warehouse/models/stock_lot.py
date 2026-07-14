# -*- coding: utf-8 -*-
from odoo import models, fields, api

class StockLot(models.Model):
    _inherit = 'stock.lot'

    # Food manufacturing specific fields
    qa_status = fields.Selection([
        ('pending', 'Pending QA'),
        ('passed', 'Passed QA'),
        ('failed', 'Failed QA'),
    ], string='QA Status', default='pending', tracking=True)
    
    temperature_logged = fields.Float(string='Storage Temp (°C)', tracking=True)
    batch_notes = fields.Text(string='Batch Notes')

    def action_pass_qa(self):
        for record in self:
            record.qa_status = 'passed'

    def action_fail_qa(self):
        for record in self:
            record.qa_status = 'failed'
