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

    def _evaluate_condition(self, record):
        """
        Evaluates the transition's condition_domain against a business record.
        :param record: The business record to evaluate against.
        :return: True if the condition passes or is empty, False otherwise.
        """
        self.ensure_one()
        if not self.condition_domain:
            return True
            
        try:
            import ast
            domain = ast.literal_eval(self.condition_domain)
            # Find if the record matches the domain
            return bool(record.env[record._name].search([('id', '=', record.id)] + domain))
        except Exception as e:
            # If the domain is malformed, log it and return False
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Failed to evaluate workflow condition domain on %s: %s", self.name, e)
            return False
