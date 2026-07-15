from odoo import api, fields, models
import uuid

class ApiClient(models.Model):
    _name = '8848.api.client'
    _description = 'API Client Credentials'

    name = fields.Char(string='Client Name', required=True, help='e.g., WordPress Gravity Forms')
    key_id = fields.Char(string='Key ID', required=True, copy=False, default=lambda self: str(uuid.uuid4()), readonly=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    environment = fields.Selection([
        ('test', 'Testing'),
        ('staging', 'Staging'),
        ('production', 'Production')
    ], string='Environment', default='test', required=True)
    
    allowed_route_codes = fields.Char(string='Allowed Routes', help='Comma-separated list of allowed route codes, e.g., franchise_enquiry')
    
    secret_reference = fields.Char(string='Secret Reference', help='Reference to the environment variable or vault holding the secret.', required=True)
    previous_secret_reference = fields.Char(string='Previous Secret Reference', help='Used during rotation to allow overlap.')
    rotation_date = fields.Datetime(string='Last Rotated At', readonly=True)
    
    timestamp_tolerance = fields.Integer(string='Timestamp Tolerance (s)', default=300, help='Maximum allowed clock skew in seconds.')
    rate_limit = fields.Integer(string='Rate Limit (req/min)', default=100)
    last_used_at = fields.Datetime(string='Last Used At', readonly=True)
    
    allowed_ip_ranges = fields.Text(string='Allowed IP Ranges', help='Optional comma-separated CIDR blocks.')
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('key_id_uniq', 'unique(key_id)', 'Key ID must be unique!')
    ]
