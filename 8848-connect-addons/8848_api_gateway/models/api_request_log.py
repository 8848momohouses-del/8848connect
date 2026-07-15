from odoo import api, fields, models

class ApiRequestLog(models.Model):
    _name = '8848.api.request.log'
    _table = 'connect_api_request_log'
    _description = 'API Request Audit Log'
    _order = 'started_at desc'

    name = fields.Char(string='Reference', required=True, readonly=True, copy=False, default='New')
    api_client_id = fields.Many2one('8848.api.client', string='API Client', readonly=True)
    
    route_code = fields.Char(string='Route Code', required=True, readonly=True, index=True)
    http_method = fields.Char(string='HTTP Method', readonly=True)
    
    idempotency_key = fields.Char(string='Idempotency Key', required=True, readonly=True, index=True)
    request_body_hash = fields.Char(string='Request Body Hash', readonly=True)
    
    state = fields.Selection([
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('error', 'Error')
    ], string='Status', required=True, default='processing', index=True)
    
    response_status = fields.Integer(string='HTTP Response Status', readonly=True)
    safe_response_payload = fields.Text(string='Safe Response Payload', readonly=True)
    target_reference = fields.Char(string='Target Public Reference', readonly=True)
    
    started_at = fields.Datetime(string='Started At', default=fields.Datetime.now, readonly=True, required=True)
    completed_at = fields.Datetime(string='Completed At', readonly=True)
    
    source_ip = fields.Char(string='Source IP', readonly=True)
    safe_error_message = fields.Text(string='Safe Error Message', readonly=True)

    _sql_constraints = [
        ('idempotency_uniq', 'unique(api_client_id, route_code, idempotency_key)', 'Idempotency key must be unique per client and route!')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('8848.api.request.log') or 'REQ-NEW'
        return super().create(vals_list)
