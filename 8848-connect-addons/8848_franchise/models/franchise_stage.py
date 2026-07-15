from odoo import fields, models


class FranchiseStage(models.Model):
    _name = '8848.franchise.stage'
    _table = 'connect_franchise_stage'
    _description = 'Franchise Lifecycle Stage'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(
        string='Folded in Kanban',
        help='Collapse this stage column in the Franchisees kanban view.')
    is_operational_stage = fields.Boolean(
        string='Operational Stage',
        help='Stages at or beyond Grand Opening: the franchise is trading. '
             'Used by reporting and portal activation.')
    description = fields.Text(translate=True)
