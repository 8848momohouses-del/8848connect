from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class WorkflowActionWizard(models.TransientModel):
    _name = '8848.workflow.action.wizard'
    _description = 'Workflow Action Wizard'

    instance_id = fields.Many2one('8848.workflow.instance', string='Workflow Instance', required=True)
    transition_id = fields.Many2one('8848.workflow.transition', string='Transition', required=True)
    
    requires_comment = fields.Boolean(related='transition_id.requires_comment')
    requires_attachment = fields.Boolean(related='transition_id.requires_attachment')
    
    comment = fields.Text(string='Comment')
    attachment = fields.Binary(string='Attachment')
    attachment_name = fields.Char(string='Attachment Name')

    def action_confirm(self):
        self.ensure_one()
        if self.requires_comment and not self.comment:
            raise ValidationError(_("A comment is required for this action."))
        if self.requires_attachment and not self.attachment:
            raise ValidationError(_("An attachment is required for this action."))

        # Append comment to transition log context or create a log entry if we had a comment
        if self.comment:
            # Typically you'd pass it via context or create a log message
            pass
            
        # Optional: Save attachment to the underlying record
        if self.attachment:
            self.env['ir.attachment'].create({
                'name': self.attachment_name or 'Workflow Attachment',
                'type': 'binary',
                'datas': self.attachment,
                'res_model': self.instance_id.res_model,
                'res_id': self.instance_id.res_id,
            })

        # Execute transition
        self.instance_id.execute_transition(self.transition_id)
        
        # If we have a comment, update the most recent log created by execute_transition
        if self.comment:
            log = self.env['8848.workflow.log'].search([
                ('instance_id', '=', self.instance_id.id),
                ('action', '=', 'transition')
            ], order='id desc', limit=1)
            if log:
                log.comment = f"{log.comment}\nComment: {self.comment}"
                
        return {'type': 'ir.actions.act_window_close'}
