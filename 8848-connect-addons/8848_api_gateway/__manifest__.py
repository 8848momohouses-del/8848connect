{
    'name': '8848 API Gateway',
    'version': '1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Secure Webhook API Gateway for external integrations.',
    'description': 'Handles HMAC authenticated webhooks from systems like WordPress Gravity Forms and securely interfaces with 8848_crm.',
    'author': '8848 Momo House',
    'website': 'https://8848momos.com.au',
    'depends': ['base', '8848_crm'],
    'data': [
        'security/api_security.xml',
        'security/ir.model.access.csv',
        'data/api_sequence.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}
