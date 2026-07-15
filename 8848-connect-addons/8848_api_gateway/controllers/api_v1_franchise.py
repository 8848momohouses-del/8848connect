from odoo import http
from odoo.http import request, Response
import json
import logging
from .api_auth import authenticate_request, ApiAuthException
import uuid
import datetime

_logger = logging.getLogger(__name__)

class ApiV1FranchiseController(http.Controller):

    @http.route('/api/v1/franchise/inquiries', type='http', auth='public', methods=['POST'], csrf=False, cors=False)
    def receive_franchise_inquiry(self, **kwargs):
        correlation_id = request.httprequest.headers.get('X-Correlation-ID', str(uuid.uuid4()))
        started_at = datetime.datetime.now()
        
        # 1. Authenticate
        try:
            client, idempotency_key, body_hash = authenticate_request('franchise_inquiry')
        except ApiAuthException as e:
            return self._json_response({'success': False, 'error': e.message, 'correlation_id': correlation_id}, status=e.code)
        except Exception as e:
            _logger.error(f"API Auth Error: {str(e)}")
            return self._json_response({'success': False, 'error': 'Internal Server Error', 'correlation_id': correlation_id}, status=500)
            
        # 2. Parse & Validate JSON payload
        raw_body = request.httprequest.get_data()
        # Max 10MB payload (should be blocked by nginx earlier, but safeguard here)
        if len(raw_body) > 10 * 1024 * 1024:
            return self._json_response({'success': False, 'error': 'Payload too large', 'correlation_id': correlation_id}, status=413)

        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            return self._json_response({'success': False, 'error': 'Invalid JSON', 'correlation_id': correlation_id}, status=422)
            
        # TODO: A4 Batch - Strict validation and A5 Batch - Delegation to CRM
        
        return self._json_response({'success': True, 'correlation_id': correlation_id}, status=201)

    def _json_response(self, data, status=200):
        body = json.dumps(data)
        headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(body)))
        ]
        return Response(body, status=status, headers=headers)
