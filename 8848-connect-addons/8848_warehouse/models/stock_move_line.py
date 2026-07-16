from odoo import models, api
from odoo.exceptions import ValidationError

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.constrains('lot_id', 'state')
    def _check_qa_status(self):
        for line in self:
            if line.state == 'done' and line.picking_id.picking_type_code == 'outgoing':
                if line.lot_id and line.lot_id.qa_status != 'passed':
                    raise ValidationError(
                        "Cannot deliver Lot '%s' because its QA status is '%s'. "
                        "Only Lots with 'passed' QA status can be delivered." % (line.lot_id.name, line.lot_id.qa_status)
                    )
