{
    'name': '8848 Connect Core Branding',
    'version': '1.0',
    'category': 'Hidden',
    'summary': 'Core branding and theme modifications for 8848 Connect.',
    'description': """
        This module overrides the default Odoo branding with the custom 
        8848 Connect theme and aesthetic.
    """,
    'author': '8848 Momo House',
    'depends': ['base', 'web', 'board'],
    'data': [
        'views/web_layout.xml',
        'data/user_data.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            '8848_core_branding/static/src/scss/variables.scss',
        ],
        'web.assets_backend': [
            '8848_core_branding/static/src/scss/backend.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': True,
    'license': 'LGPL-3',
}
