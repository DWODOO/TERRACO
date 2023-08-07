# -*- coding:utf-8 -*-
{
    'name': 'Stock Disallow Negative',
    'version': '1.0.0',
    'category': 'Inventory',
    'summary': 'Disallow negative stock levels by default',
    'author': 'SMARTEST ALGERIA',
    'website': 'https://smartest.dz',
    'depends': ['stock'],
    'data': [
        'views/product_product_views.xml',
        'views/stock_location_views.xml',
        'views/res_users_views.xml',
        'security/security.xml',
    ],
    'installable': True,
    'license': 'LGPL-3',
}
