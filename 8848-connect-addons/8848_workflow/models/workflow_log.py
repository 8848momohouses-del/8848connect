from odoo import api, fields, models

class WorkflowLog(models.Model):
    _name = '8848.workflow.log'
    _description = 'Workflow Audit Log'
    _order = 'timestamp desc, id desc'

    instance_id = fields.Many2one('8848.workflow.instance', string='Instance', required=True, ondelete='cascade', index=True)
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now, required=True, readonly=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True, readonly=True)
    
    action = fields.Char(string='Action', required=True, readonly=True)
    source_step_id = fields.Many2one('8848.workflow.step', string='Source Step', readonly=True)
    destination_step_id = fields.Many2one('8848.workflow.step', string='Destination Step', readonly=True)
    
    comment = fields.Text(string='Comment', readonly=True)
    result = fields.Selection([
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('rejected', 'Rejected'),
        ('escalated', 'Escalated')
    ], string='Result', required=True, default='success', readonly=True)
    
    event_code = fields.Char(string='Event Code', readonly=True)
    correlation_id = fields.Char(string='Correlation ID', readonly=True, help="Idempotency key for event-driven logs")
