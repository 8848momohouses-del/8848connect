from odoo import api, fields, models


class CommunicationTemplate(models.Model):
    _name = '8848.communication.template'
    _description = 'Communication Template'
    _inherit = ['mail.thread']

    name = fields.Char(string='Template Name', required=True, tracking=True)
    code = fields.Char(string='Template Code', required=True, tracking=True, copy=False)
    
    # We reference Odoo's ir.model directly to know what we are templating
    model_id = fields.Many2one('ir.model', string='Applies To', required=True, tracking=True)
    model = fields.Char(related='model_id.model', string='Related Document Model', store=True, readonly=True)

    subject = fields.Char(string='Subject / Title', translate=True, help='Subject for Emails, Title for Portal notifications. Supports Jinja2 syntax.')
    body_html = fields.Html(string='HTML Body', translate=True, sanitize=False, help='Used for Emails and Portal notes. Supports Jinja2 syntax.')
    body_text = fields.Text(string='Text Body', translate=True, help='Used for SMS and plain text fallbacks. Supports Jinja2 syntax.')

    channel_ids = fields.Many2many(
        '8848.communication.channel',
        string='Supported Channels',
        help='Channels this template is designed to be sent through.'
    )

    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The template code must be unique!')
    ]
