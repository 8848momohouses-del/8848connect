{
    'name': '8848 Connect Factory',
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': 'Manufacturing and factory operations for 8848 Connect.',
    'description': """
        This module extends Odoo MRP with custom features for 8848 Connect,
        including advanced recipe management, BOM tracking, waste logging,
        and factory production processes.
    """,
    'author': '8848 Momo House',
    'depends': ['8848_inventory', 'mrp'],
    'data': [
        'views/mrp_production_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
