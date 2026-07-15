from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class CrmIntakeService(models.AbstractModel):
    _name = '8848.crm.intake.service'
    _table = 'connect_crm_intake_service'
    _description = 'CRM Intake Service Boundary'

    @api.model
    def process_enquiry(self, payload, integration_context):
        """
        Validates payload and processes the enquiry securely.
        Returns a structured dictionary to the caller.
        """
        # Strict validation
        if not isinstance(payload, dict):
            return {'success': False, 'error': 'Payload must be a dictionary', 'status': 422}
            
        contact_name = payload.get('contact_name', '').strip()
        email_from = payload.get('email_from', '').strip()
        
        if not contact_name:
            return {'success': False, 'error': 'contact_name is required', 'status': 422}
        if not email_from:
            return {'success': False, 'error': 'email_from is required', 'status': 422}
            
        if '@' not in email_from:
            return {'success': False, 'error': 'email_from is invalid', 'status': 422}
            
        # Clean payload for business logic
        clean_payload = {
            'contact_name': contact_name,
            'email_from': email_from,
            'phone': payload.get('phone', payload.get('mobile', '')).strip(),
            'franchise_territory_interest': payload.get('franchise_territory_interest', '').strip(),
            'external_entry_id': integration_context.get('idempotency_key'),
            'message': payload.get('message', '').strip(),
            'marketing_consent': bool(payload.get('marketing_consent', False)),
            'privacy_consent': bool(payload.get('privacy_consent', False)),
        }
        
        # Delegate to crm.lead model method for business logic
        result = self.env['crm.lead'].create_or_update_franchise_enquiry(clean_payload)
        
        if result.get('success'):
            return {
                'success': True,
                'reference': result.get('reference'),
                'status': result.get('status'), # 'created', 'updated', or 'idempotent'
                'http_status': 200 if result.get('status') in ('updated', 'idempotent') else 201
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Unknown Error'),
                'status': 422
            }
