from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class WorkflowInstance(models.Model):
    _name = '8848.workflow.instance'
    _description = 'Workflow Instance'
    _rec_name = 'reference'
    _order = 'id desc'
    _inherit = ['mail.thread']

    workflow_id = fields.Many2one('8848.workflow.definition', string='Workflow Definition', required=True, ondelete='restrict', tracking=True)
    reference = fields.Char(string='Reference', compute='_compute_reference', store=True)
    
    res_model = fields.Char(string='Target Model', required=True, index=True)
    res_id = fields.Integer(string='Target Record ID', required=True, index=True)
    
    company_id = fields.Many2one('res.company', string='Company', related='workflow_id.company_id', store=True)
    active = fields.Boolean(default=True)
    
    current_step_id = fields.Many2one('8848.workflow.step', string='Current Step', tracking=True)
    
    state = fields.Selection([
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='State', default='in_progress', tracking=True, required=True)
    
    started_at = fields.Datetime(string='Started At', default=fields.Datetime.now, readonly=True)
    completed_at = fields.Datetime(string='Completed At', readonly=True)
    deadline = fields.Datetime(string='Deadline', tracking=True)
    
    log_ids = fields.One2many('8848.workflow.log', 'instance_id', string='Logs')
    
    @api.depends('workflow_id', 'res_model', 'res_id')
    def _compute_reference(self):
        for record in self:
            if record.workflow_id and record.res_model and record.res_id:
                record.reference = f"{record.workflow_id.code}-{record.res_model}-{record.res_id}"
            else:
                record.reference = _("New Instance")

    _sql_constraints = [
        ('unique_active_instance', 
         'unique(workflow_id, res_model, res_id, active)', 
         'A business record can only have one active instance of a specific workflow!')
    ]
