from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class WorkflowDefinition(models.Model):
    _name = '8848.workflow.definition'
    _description = 'Workflow Definition'
    _rec_name = 'name'
    _order = 'sequence, id'
    _inherit = ['mail.thread']

    name = fields.Char(string='Name', required=True, tracking=True, help="Display name for this workflow")
    code = fields.Char(string='Code', required=True, tracking=True, help="Unique technical code for the workflow")
    active = fields.Boolean(default=True, tracking=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    description = fields.Text(string='Description')
    target_model_id = fields.Many2one('ir.model', string='Target Model', required=True, ondelete='cascade', help="The business model this workflow orchestrates")
    
    step_ids = fields.One2many('8848.workflow.step', 'workflow_id', string='Steps')
    initial_step_id = fields.Many2one('8848.workflow.step', string='Initial Step', domain="[('workflow_id', '=', id)]", help="The starting step for new instances")
    
    allow_multiple_active_instances = fields.Boolean(
        string='Allow Multiple Active Instances',
        default=False,
        help="If false, a business record can only have one active instance of this workflow at a time."
    )
    automatic_start = fields.Boolean(string='Automatic Start', default=False, help="Automatically start when a matching record is created")

    _sql_constraints = [
        ('code_unique', 'unique(code, company_id)', 'Workflow code must be unique per company!')
    ]
