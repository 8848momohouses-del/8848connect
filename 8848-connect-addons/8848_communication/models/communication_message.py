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
        """Sends an email using Odoo's native mail.mail."""
        if not self.partner_id or not self.partner_id.email:
            raise ValueError("Recipient Partner must have an email address.")
            
        mail_values = {
            'subject': self.subject,
            'body_html': self.body or '',
            'email_to': self.partner_id.email,
            'recipient_ids': [(4, self.partner_id.id)],
            'model': self.res_model,
            'res_id': self.res_id,
            'auto_delete': True,
        }
        mail = self.env['mail.mail'].sudo().create(mail_values)
        mail.send()
        self.mail_message_id = mail.mail_message_id.id

    def _dispatch_sms(self):
        """Sends an SMS using Odoo's native sms.sms shell."""
        if not self.partner_id or not self.partner_id.mobile:
            raise ValueError("Recipient Partner must have a mobile number.")
            
        # We need the plain text body from the template, as self.body is HTML.
        body_text = self.template_id.body_text if self.template_id else self.body
        
        sms_values = {
            'partner_id': self.partner_id.id,
            'number': self.partner_id.mobile,
            'body': body_text or '',
        }
        sms = self.env['sms.sms'].sudo().create(sms_values)
        sms.send()

    def _dispatch_portal(self):
        """Posts a message to the record's chatter, visible to portal users."""
        target_record = self.env[self.res_model].browse(self.res_id)
        if hasattr(target_record, 'message_post'):
            msg = target_record.message_post(
                subject=self.subject,
                body=self.body,
                message_type='comment',
                subtype_xmlid='mail.mt_comment',
                partner_ids=[self.partner_id.id] if self.partner_id else []
            )
            self.mail_message_id = msg.id
        else:
            raise ValueError(f"Model {self.res_model} does not inherit mail.thread. Cannot dispatch portal message.")
        
    def _dispatch_internal(self):
        """Posts an internal note to the record's chatter, invisible to portal."""
        target_record = self.env[self.res_model].browse(self.res_id)
        if hasattr(target_record, 'message_post'):
            msg = target_record.message_post(
                subject=self.subject,
                body=self.body,
                message_type='comment',
                subtype_xmlid='mail.mt_note'
            )
            self.mail_message_id = msg.id
        else:
            raise ValueError(f"Model {self.res_model} does not inherit mail.thread. Cannot dispatch internal note.")
