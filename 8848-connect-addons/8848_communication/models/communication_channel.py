from odoo import api, fields, models


class CommunicationChannel(models.Model):
    _name = '8848.communication.channel'
    _description = 'Communication Channel'
    _order = 'sequence, id'

    name = fields.Char(string='Channel Name', required=True, translate=True)
    code = fields.Selection([
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('portal', 'Portal Notification'),
        ('internal', 'Internal Note'),
    ], string='Channel Code', required=True)
    is_active = fields.Boolean(string='Active', default=True)
    sequence = fields.Integer(string='Sequence', default=10)
    provider_config = fields.Text(string='Provider Configuration (JSON)', help='JSON configuration for the channel provider.')

    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The channel code must be unique!')
    ]
