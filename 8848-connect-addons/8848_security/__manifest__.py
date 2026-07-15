# -*- coding: utf-8 -*-
{
    'name': '8848 Security',
    'version': '1.0.0',
    'category': '8848 Connect',
    'summary': 'Core role-based security hierarchy for 8848 Connect',
    'description': 'Provides business-level security groups without IT administration privileges.',
    'author': '8848 Momo House',
    'depends': ['base'],
    'data': [
        'security/security_categories.xml',
        'security/security_groups.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
