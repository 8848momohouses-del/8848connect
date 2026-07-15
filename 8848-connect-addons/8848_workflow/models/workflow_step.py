from odoo import api, fields, models

class WorkflowStep(models.Model):
    _name = '8848.workflow.step'
    _description = 'Workflow Step'
    _rec_name = 'name'
    _order = 'sequence, id'

    workflow_id = fields.Many2one('8848.workflow.definition', string='Workflow', required=True, ondelete='cascade')
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    sequence = fields.Integer(default=10)
    
    step_type = fields.Selection([
        ('start', 'Start'),
        ('normal', 'Normal'),
        ('approval', 'Approval'),
        ('end', 'End')
    ], string='Step Type', required=True, default='normal')
    
    responsible_group_id = fields.Many2one('res.groups', string='Responsible Group', help="Group responsible for this step")
    sla_hours = fields.Float(string='SLA (Hours)', help="Expected duration to complete this step")
    
    entry_action_id = fields.Many2one('ir.actions.server', string='Entry Action', help="Server action executed when entering this step")
    exit_action_id = fields.Many2one('ir.actions.server', string='Exit Action', help="Server action executed when leaving this step")

    _sql_constraints = [
        ('code_workflow_unique', 'unique(code, workflow_id)', 'Step code must be unique per workflow!')
    ]
