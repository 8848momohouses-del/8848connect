# 8848 API Gateway Integration Guide

## Overview
The `8848_api_gateway` module securely ingests webhooks from external systems (such as WordPress Gravity Forms) and integrates them into the Odoo CRM.

## Endpoint
- **URL:** `https://api.8848momos.com.au/api/v1/franchise/inquiries`
- **Method:** `POST`
- **Content-Type:** `application/json`

## Authentication (HMAC-SHA256)
Every request must include the following headers:
- `X-8848-Key-Id`: Your assigned Key ID.
- `X-8848-Timestamp`: Unix epoch timestamp.
- `X-8848-Idempotency-Key`: A unique UUID for this request.
- `X-8848-Signature`: HMAC-SHA256 signature.

### Signature Generation (cURL / Python Example)
```python
import hmac
import hashlib
import json
import time
import uuid

secret = b'YOUR_RAW_SECRET_HERE'
key_id = 'YOUR_KEY_ID'
body = {
    "contact_name": "John Doe",
    "email_from": "john.doe@example.com",
    "mobile": "0400000000",
    "message": "Interested in opening a franchise in Sydney."
}

body_bytes = json.dumps(body).encode('utf-8')
body_hash = hashlib.sha256(body_bytes).hexdigest()

timestamp = str(int(time.time()))
idempotency_key = str(uuid.uuid4())

canonical_str = f"POST\n/api/v1/franchise/inquiries\n{timestamp}\n{idempotency_key}\n{body_hash}"
signature = hmac.new(secret, canonical_str.encode('utf-8'), hashlib.sha256).hexdigest()

print(f"X-8848-Key-Id: {key_id}")
print(f"X-8848-Timestamp: {timestamp}")
print(f"X-8848-Idempotency-Key: {idempotency_key}")
print(f"X-8848-Signature: {signature}")
```

## Payload Limit
The API strictly enforces a **1MB maximum payload size** at both the Nginx proxy layer and the Odoo controller layer. Requests exceeding 1MB will be rejected with an HTTP 413 Payload Too Large error before any JSON processing occurs. Do not send large documents through this endpoint.

## Idempotency and Duplicates
If you send the same `X-8848-Idempotency-Key` and body within the same hour, the server returns the cached response (HTTP 200). 
If you send the same key with a different body, the server returns HTTP 409 Conflict.

## Rollback Policy
If integration fails, an Odoo administrator can deactivate your API Client via `API Gateway > API Clients`, which will instantly reject all requests with HTTP 403.
