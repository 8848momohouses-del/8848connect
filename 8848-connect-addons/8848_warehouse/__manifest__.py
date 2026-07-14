{
    'name': '8848 Connect Warehouse',
    'version': '1.0',
    'category': 'Inventory/Inventory',
    'summary': 'Advanced warehouse operations for 8848 Connect.',
    'description': """
        This module extends standard warehouse operations with custom features
        for batch tracking, expiry tracking, and storage management tailored
        for the food manufacturing and franchise industry.
    """,
    'author': '8848 Momo House',
    'depends': ['8848_inventory', 'stock', 'product_expiry'],
    'data': [
        'views/stock_lot_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
