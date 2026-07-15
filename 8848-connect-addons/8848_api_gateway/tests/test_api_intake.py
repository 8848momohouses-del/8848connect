import json
import os
import time
from odoo.tests.common import HttpCase, tagged
import uuid
import hashlib
import hmac

@tagged('post_install', '-at_install', '/8848_api_gateway')
class TestApiIntake(HttpCase):

    def setUp(self):
        super().setUp()
        self.secret = 'test-secret-12345'
        os.environ['TEST_SECRET_REF'] = self.secret
        
        self.client = self.env['8848.api.client'].create({
            'name': 'Test Client',
            'environment': 'test',
            'allowed_route_codes': 'franchise_inquiry',
            'secret_reference': 'TEST_SECRET_REF'
        })
        self.url = '/api/v1/franchise/inquiries'

    def _generate_headers(self, method, path, body, timestamp=None, idempotency_key=None, secret=None, key_id=None):
        if timestamp is None:
            timestamp = int(time.time())
        if idempotency_key is None:
            idempotency_key = str(uuid.uuid4())
        if secret is None:
            secret = self.secret
        if key_id is None:
            key_id = self.client.key_id
            
        body_bytes = json.dumps(body).encode('utf-8')
        body_hash = hashlib.sha256(body_bytes).hexdigest()
        
        canonical_str = f"{method}\n{path}\n{timestamp}\n{idempotency_key}\n{body_hash}"
        canonical_bytes = canonical_str.encode('utf-8')
        
        signature = hmac.new(secret.encode('utf-8'), canonical_bytes, hashlib.sha256).hexdigest()
        
        return {
            'X-8848-Key-Id': key_id,
            'X-8848-Timestamp': str(timestamp),
            'X-8848-Signature': signature,
            'X-8848-Idempotency-Key': idempotency_key,
            'Content-Type': 'application/json'
        }

    def test_idempotent_retry(self):
        body = {'contact_name': 'Idempotent Test', 'email_from': 'idempotent@8848.com'}
        idem_key = 'idem-123'
        
        headers1 = self._generate_headers('POST', self.url, body, idempotency_key=idem_key)
        resp1 = self.url_open(self.url, data=json.dumps(body), headers=headers1)
        self.assertEqual(resp1.status_code, 201)
        
        # Exact same retry
        headers2 = self._generate_headers('POST', self.url, body, idempotency_key=idem_key)
        resp2 = self.url_open(self.url, data=json.dumps(body), headers=headers2)
        
        # Expect 200 for cached successful response
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp1.json().get('reference'), resp2.json().get('reference'))
        
    def test_conflict_different_body(self):
        idem_key = 'idem-conflict'
        
        body1 = {'contact_name': 'Conflict1', 'email_from': 'c1@8848.com'}
        headers1 = self._generate_headers('POST', self.url, body1, idempotency_key=idem_key)
        resp1 = self.url_open(self.url, data=json.dumps(body1), headers=headers1)
        self.assertEqual(resp1.status_code, 201)
        
        body2 = {'contact_name': 'Conflict2', 'email_from': 'c2@8848.com'}
        headers2 = self._generate_headers('POST', self.url, body2, idempotency_key=idem_key)
        resp2 = self.url_open(self.url, data=json.dumps(body2), headers=headers2)
        
        # Conflict response due to body hash mismatch
        self.assertEqual(resp2.status_code, 409)

    def test_strict_validation(self):
        # Missing email_from
        body = {'contact_name': 'Missing Email'}
        headers = self._generate_headers('POST', self.url, body)
        response = self.url_open(self.url, data=json.dumps(body), headers=headers)
        
        self.assertEqual(response.status_code, 422)
        self.assertTrue('required' in response.json().get('error'))
