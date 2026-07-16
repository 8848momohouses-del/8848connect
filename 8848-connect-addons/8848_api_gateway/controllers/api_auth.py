import hmac
import hashlib
import os
import time
from odoo.http import request

class ApiAuthException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

def authenticate_request(route_code):
    """
    Authenticates an incoming webhook request using HMAC-SHA256.
    Returns: (api_client, idempotency_key, body_hash)
    Raises ApiAuthException if authentication fails.
    """
    headers = request.httprequest.headers
    
    key_id = headers.get('X-8848-Key-Id')
    timestamp_str = headers.get('X-8848-Timestamp')
    signature = headers.get('X-8848-Signature')
    idempotency_key = headers.get('X-8848-Idempotency-Key')
    
    if not all([key_id, timestamp_str, signature, idempotency_key]):
        raise ApiAuthException(401, "Missing required authentication headers.")

    # 1. Parse and validate timestamp
    try:
        timestamp = int(timestamp_str)
    except ValueError:
        raise ApiAuthException(401, "Invalid timestamp format.")
        
    current_time = int(time.time())
    
    # 2. Lookup API Client
    client = request.env['8848.api.client'].sudo().with_context(active_test=False).search([('key_id', '=', key_id)], limit=1)
    if not client:
        raise ApiAuthException(401, "Unknown Key ID.")
        
    if not client.active:
        raise ApiAuthException(403, "API Client is inactive.")
        
    if client.allowed_route_codes and route_code not in [r.strip() for r in client.allowed_route_codes.split(',')]:
        raise ApiAuthException(403, f"Route code '{route_code}' not allowed for this client.")

    # 3. Check Clock Skew
    tolerance = client.timestamp_tolerance or 300
    if abs(current_time - timestamp) > tolerance:
        raise ApiAuthException(401, "Timestamp outside of allowed tolerance (replay protection).")
        
    # 4. Construct Canonical String
    raw_body = request.httprequest.get_data()
    body_hash = hashlib.sha256(raw_body).hexdigest()
    
    http_method = request.httprequest.method.upper()
    exact_path = request.httprequest.path
    
    canonical_string = f"{http_method}\n{exact_path}\n{timestamp_str}\n{idempotency_key}\n{body_hash}"
    canonical_bytes = canonical_string.encode('utf-8')
    
    # 5. Verify Signature
    def check_signature(secret_ref):
        if not secret_ref:
            return False
        # We assume secrets are loaded in env vars.
        # For testing, we might pass them directly if os.environ doesn't have it, but for prod it MUST be in env.
        # To make tests easier without mutating os.environ globally, we can also check the context, but
        # os.environ is standard. Let's try os.environ.get.
        secret = os.environ.get(secret_ref)
        if not secret:
            return False
            
        expected_mac = hmac.new(secret.encode('utf-8'), canonical_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_mac, signature)
        
    if not check_signature(client.secret_reference):
        # Fallback to previous secret if rotating
        if not (client.previous_secret_reference and check_signature(client.previous_secret_reference)):
            raise ApiAuthException(401, "Invalid signature.")

    # Log last used at (in a separate transaction or safe write)
    # Note: Doing write() here creates a lock on the client record, which might reduce concurrency.
    # We will ignore it for now or rely on an async job if needed, but for MVP it's fine.
    
    return client, idempotency_key, body_hash
