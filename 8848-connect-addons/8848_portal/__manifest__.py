{
    'author': '8848 Momo House',
    'name': '8848 Connect - Franchise Portal',
    'version': '1.0',
    'category': 'Website/Portal',
    'summary': 'Dedicated web portal for Franchisees to view deliveries and royalties.',
    'depends': ['portal', 'website', '8848_franchise', '8848_royalty'],
    'data': [
        'security/security_rules.xml',
        'security/ir.model.access.csv',
        'views/portal_templates.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
