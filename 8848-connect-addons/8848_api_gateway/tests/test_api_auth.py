import hmac
import hashlib
import json
import os
import time
from odoo.tests.common import HttpCase, tagged
import uuid

@tagged('post_install', '-at_install', '/8848_api_gateway')
class TestApiAuth(HttpCase):

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

    def test_valid_signature(self):
        body = {'contact_name': 'Test', 'email_from': 'test@8848.com'}
        headers = self._generate_headers('POST', self.url, body)
        response = self.url_open(self.url, data=json.dumps(body), headers=headers)
        self.assertEqual(response.status_code, 201)

    def test_invalid_signature(self):
        body = {'contact_name': 'Test', 'email_from': 'test@8848.com'}
        headers = self._generate_headers('POST', self.url, body, secret='wrong-secret')
        response = self.url_open(self.url, data=json.dumps(body), headers=headers)
        self.assertEqual(response.status_code, 401)
        resp_json = response.json()
        self.assertEqual(resp_json.get('error'), 'Invalid signature.')

    def test_expired_timestamp(self):
        body = {'contact_name': 'Test', 'email_from': 'test@8848.com'}
        # 600 seconds in past
        headers = self._generate_headers('POST', self.url, body, timestamp=int(time.time()) - 600)
        response = self.url_open(self.url, data=json.dumps(body), headers=headers)
        self.assertEqual(response.status_code, 401)
        resp_json = response.json()
        self.assertTrue('tolerance' in resp_json.get('error'))

    def test_unknown_client(self):
        body = {'contact_name': 'Test', 'email_from': 'test@8848.com'}
        headers = self._generate_headers('POST', self.url, body, key_id='does-not-exist')
        response = self.url_open(self.url, data=json.dumps(body), headers=headers)
        self.assertEqual(response.status_code, 401)
        
    def test_inactive_client(self):
        self.client.active = False
        body = {'contact_name': 'Test', 'email_from': 'test@8848.com'}
        headers = self._generate_headers('POST', self.url, body)
        response = self.url_open(self.url, data=json.dumps(body), headers=headers)
        self.assertEqual(response.status_code, 403)
