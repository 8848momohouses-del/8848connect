# -*- coding: utf-8 -*-
{
    'name': '8848 Connect Dashboard',
    'version': '19.0.1.0.0',
    'category': 'Hidden',
    'summary': 'Branded landing dashboard with live KPIs for 8848 Connect.',
    'description': """
        Custom landing page for 8848 Connect showing live KPI cards for
        CRM, Sales, Projects and Inventory, each linking into its app.
    """,
    'author': '8848 Momo House',
    'depends': [
        'web',
        'crm',
        'sale_management',
        'project',
        'stock',
        '8848_core_branding',
    ],
    'data': [
        'views/dashboard_action.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '8848_dashboard/static/src/dashboard/dashboard.js',
            '8848_dashboard/static/src/dashboard/dashboard.xml',
            '8848_dashboard/static/src/dashboard/dashboard.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
