{
    'name': '8848 Connect - Admin Dashboard',
    'version': '1.0',
    'category': 'Hidden',
    'summary': 'High-level KPI dashboards for Factory Admins.',
    'depends': [
        'board',
        '8848_franchise',
        '8848_royalty',
        '8848_factory',
        # Referenced by dashboard_views.xml board widgets / menu override:
        '8848_store_performance',
        '8848_core_branding',
    ],
    'data': [
        'views/dashboard_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
