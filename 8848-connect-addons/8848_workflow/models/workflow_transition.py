from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class WorkflowTransition(models.Model):
    _name = '8848.workflow.transition'
    _description = 'Workflow Transition'
    _order = 'sequence, id'

    workflow_id = fields.Many2one('8848.workflow.definition', string='Workflow', required=True, ondelete='cascade')
    name = fields.Char(string='Name', required=True, help="Button or Action name")
    sequence = fields.Integer(default=10)
    
    source_step_id = fields.Many2one('8848.workflow.step', string='Source Step', required=True, ondelete='cascade', domain="[('workflow_id', '=', workflow_id)]")
    destination_step_id = fields.Many2one('8848.workflow.step', string='Destination Step', required=True, ondelete='cascade', domain="[('workflow_id', '=', workflow_id)]")
    
    required_group_id = fields.Many2one('res.groups', string='Required Group', help="Only users in this group can trigger this transition")
    
    requires_comment = fields.Boolean(string='Requires Comment', default=False)
    requires_attachment = fields.Boolean(string='Requires Attachment', default=False)
    
    is_automatic = fields.Boolean(string='Automatic Transition', default=False, help="Transition happens automatically if condition is met")
    condition_domain = fields.Char(string='Condition Domain', help="Domain evaluated on the target business record")
    
    action_id = fields.Many2one('ir.actions.server', string='Transition Action', help="Server action executed during transition")

    @api.constrains('source_step_id', 'destination_step_id')
    def _check_steps(self):
        for record in self:
            if record.source_step_id == record.destination_step_id:
                raise ValidationError(_("Source and destination steps cannot be the same."))
