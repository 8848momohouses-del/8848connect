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

    @api.model
    def _cron_dispatch_messages(self):
        """Finds all queued messages due for dispatch and processes them."""
        messages = self.search([
            ('status', '=', 'queued'),
            ('scheduled_date', '<=', fields.Datetime.now())
        ], limit=200) # Process in batches of 200

        for message in messages:
            message._dispatch()

    def _dispatch(self):
        """Internal dispatch router based on channel code."""
        self.ensure_one()
        
        try:
            channel_code = self.channel_id.code
            
            # Delegate to channel-specific dispatch methods
            if channel_code == 'email':
                self._dispatch_email()
            elif channel_code == 'sms':
                self._dispatch_sms()
            elif channel_code == 'portal':
                self._dispatch_portal()
            elif channel_code == 'internal':
                self._dispatch_internal()
            else:
                raise ValueError(f"Unsupported channel code: {channel_code}")
                
            self.write({'status': 'sent', 'error_log': False})
            
        except Exception as e:
            self._handle_dispatch_error(str(e))

    def _handle_dispatch_error(self, error_msg):
        """Handles retry logic on failure."""
        self.ensure_one()
        new_retry_count = self.retry_count + 1
        
        if new_retry_count >= 3:
            # Exhausted retries
            self.write({
                'status': 'failed',
                'retry_count': new_retry_count,
                'error_log': f"Failed after {new_retry_count} attempts.\nLast Error: {error_msg}"
            })
        else:
            # Will retry on next cron run
            self.write({
                'retry_count': new_retry_count,
                'error_log': f"Attempt {new_retry_count} failed.\nError: {error_msg}"
            })

    def _dispatch_email(self):
        """Stub for email dispatch. To be implemented in C3."""
        pass

    def _dispatch_sms(self):
        """Stub for sms dispatch. To be implemented in C3."""
        pass

    def _dispatch_portal(self):
        """Stub for portal dispatch. To be implemented in C3."""
        pass
        
    def _dispatch_internal(self):
        """Stub for internal dispatch. To be implemented in C3."""
        pass
