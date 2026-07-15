from odoo import api, fields, models
from jinja2 import Environment

class CommunicationMixin(models.AbstractModel):
    _name = '8848.communication.mixin'
    _table = 'connect_communication_mixin'
    _description = 'Communication Hub Integration Mixin'

    def send_communication(self, template_code, channel_code=None, partner_id=None, scheduled_date=None):
        """
        Public API for business models to enqueue communications.
        
        :param template_code: Code of the 8848.communication.template
        :param channel_code: (Optional) Override the template's default channels. Sends to all matched if None.
        :param partner_id: (Optional) Specific res.partner recipient.
        :param scheduled_date: (Optional) When to dispatch this message.
        """
        self.ensure_one()
        
        # 1. Find the Template
        template = self.env['8848.communication.template'].search([('code', '=', template_code)], limit=1)
        if not template:
            raise ValueError(f"Communication template with code '{template_code}' not found.")
            
        # 2. Determine target channels
        channels = template.channel_ids
        if channel_code:
            channels = channels.filtered(lambda c: c.code == channel_code)
            
        if not channels:
            # If no specific channel was forced, fallback to attempting to find the channel globally if forced
            if channel_code:
                channels = self.env['8848.communication.channel'].search([('code', '=', channel_code)], limit=1)
            
        if not channels:
            raise ValueError(f"No valid communication channels found for template '{template_code}'.")
            
        # 3. Simple Jinja2 Rendering
        # In a full implementation, this uses Odoo's qweb/jinja engine safely.
        # For our design, we do basic string replacement using python format or a safe jinja env.
        env = Environment()
        render_ctx = {'object': self, 'env': self.env}
        
        subject = env.from_string(template.subject or '').render(render_ctx)
        body = env.from_string(template.body_html or '').render(render_ctx)
        
        # 4. Enqueue messages
        messages = self.env['8848.communication.message']
        for channel in channels:
            msg_vals = {
                'res_model': self._name,
                'res_id': self.id,
                'partner_id': partner_id.id if partner_id else False,
                'channel_id': channel.id,
                'template_id': template.id,
                'subject': subject,
                'body': body,
                'status': 'queued',
            }
            if scheduled_date:
                msg_vals['scheduled_date'] = scheduled_date
                
            messages |= self.env['8848.communication.message'].create(msg_vals)
            
        return messages
