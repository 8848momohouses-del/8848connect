from odoo import api, fields, models


class CommunicationMessage(models.Model):
    _name = '8848.communication.message'
    _description = 'Communication Message Queue'
    _order = 'scheduled_date desc, id desc'

    # Targeting
    res_model = fields.Char(string='Related Document Model', required=True, index=True)
    res_id = fields.Many2oneReference(string='Related Document ID', model_field='res_model', required=True, index=True)
    partner_id = fields.Many2one('res.partner', string='Recipient', index=True)

    # Content & Routing
    channel_id = fields.Many2one('8848.communication.channel', string='Channel', required=True)
    template_id = fields.Many2one('8848.communication.template', string='Source Template')
    
    subject = fields.Char(string='Subject / Title')
    body = fields.Html(string='Message Body')

    # Status & Queue
    status = fields.Selection([
        ('draft', 'Draft'),
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, index=True)
    
    scheduled_date = fields.Datetime(string='Scheduled For', default=fields.Datetime.now, index=True)
    retry_count = fields.Integer(string='Retry Count', default=0)
    error_log = fields.Text(string='Error Log', readonly=True)

    # Reference to native mail message if generated
    mail_message_id = fields.Many2one('mail.message', string='Native Message', readonly=True)
