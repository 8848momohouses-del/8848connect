from odoo import http
from odoo.http import request, Response
import json
import logging
from .api_auth import authenticate_request, ApiAuthException
import uuid
import datetime

import psycopg2

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
        # Max 1MB payload for franchise inquiries
        if len(raw_body) > 1 * 1024 * 1024:
            return self._json_response({'success': False, 'error': 'Payload too large', 'correlation_id': correlation_id}, status=413)

        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            return self._json_response({'success': False, 'error': 'Invalid JSON', 'correlation_id': correlation_id}, status=422)
            
        # 3. Transport Idempotency and Audit Log setup
        ReqLog = request.env['8848.api.request.log'].sudo()
        
        from odoo.tools import mute_logger
        
        try:
            with mute_logger('odoo.sql_db'), request.env.cr.savepoint():
                current_log = ReqLog.create({
                    'api_client_id': client.id,
                    'route_code': 'franchise_inquiry',
                    'http_method': request.httprequest.method,
                    'idempotency_key': idempotency_key,
                    'request_body_hash': body_hash,
                    'state': 'processing',
                    'started_at': started_at,
                    'source_ip': request.httprequest.remote_addr,
                })
        except psycopg2.IntegrityError:
            # DB UniqueViolation caught safely using a savepoint
            existing_log = ReqLog.search([
                ('api_client_id', '=', client.id),
                ('route_code', '=', 'franchise_inquiry'),
                ('idempotency_key', '=', idempotency_key)
            ], limit=1)
            
            if not existing_log:
                return self._json_response({'success': False, 'error': 'Concurrency recovery failed', 'correlation_id': correlation_id}, status=500)
                
            if existing_log.state == 'processing':
                # Check for stuck request (e.g., > 1 hour old)
                if (started_at - existing_log.started_at).total_seconds() > 3600:
                    current_log = existing_log
                    current_log.write({'state': 'processing', 'started_at': started_at})
                else:
                    return self._json_response({'success': False, 'error': 'Request already processing', 'correlation_id': correlation_id}, status=409)
            elif existing_log.request_body_hash != body_hash:
                return self._json_response({'success': False, 'error': 'Idempotency key reused with different payload', 'correlation_id': correlation_id}, status=409)
            elif existing_log.state == 'success':
                cached_resp = json.loads(existing_log.safe_response_payload or '{}')
                cached_resp['correlation_id'] = correlation_id
                return self._json_response(cached_resp, status=existing_log.response_status or 200)
            elif existing_log.state == 'error':
                current_log = existing_log
                current_log.write({'state': 'processing', 'started_at': started_at})
        except Exception as e:
            _logger.error(f"Unrelated Log Exception: {str(e)}")
            return self._json_response({'success': False, 'error': 'Internal Server Error', 'correlation_id': correlation_id}, status=500)

        # 4. Delegate to CRM Intake Service
        try:
            integration_context = {
                'idempotency_key': idempotency_key,
                'correlation_id': correlation_id,
                'client_name': client.name
            }
            
            # Narrow Sudo Boundary
            service = request.env['8848.crm.intake.service'].sudo()
            result = service.process_enquiry(payload, integration_context)
            
            if result.get('success'):
                response_data = {
                    'success': True,
                    'reference': result.get('reference'),
                    'status': result.get('status'),
                    'correlation_id': correlation_id,
                    'message': 'Franchise enquiry received.'
                }
                http_status = result.get('http_status', 201)
                
                # Update Log
                current_log.write({
                    'state': 'success',
                    'response_status': http_status,
                    'safe_response_payload': json.dumps(response_data),
                    'target_reference': result.get('reference'),
                    'completed_at': datetime.datetime.now()
                })
                
                return self._json_response(response_data, status=http_status)
            else:
                # Validation error from service
                error_msg = result.get('error', 'Validation failed')
                http_status = result.get('status', 422)
                
                current_log.write({
                    'state': 'error',
                    'response_status': http_status,
                    'safe_error_message': error_msg,
                    'completed_at': datetime.datetime.now()
                })
                return self._json_response({'success': False, 'error': error_msg, 'correlation_id': correlation_id}, status=http_status)
                
        except Exception as e:
            _logger.error(f"CRM Service Error: {str(e)}")
            current_log.write({
                'state': 'error',
                'response_status': 500,
                'safe_error_message': 'Internal Server Error',
                'completed_at': datetime.datetime.now()
            })
            return self._json_response({'success': False, 'error': 'Internal Server Error', 'correlation_id': correlation_id}, status=500)

    def _json_response(self, data, status=200):
        body = json.dumps(data)
        headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(body)))
        ]
        return Response(body, status=status, headers=headers)
