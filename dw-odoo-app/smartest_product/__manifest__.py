# -*- coding: utf-8 -*-
{
    'name': "Products & Pricelists - BY SMARTEST",

    'summary': """
    Add improvements for Product Management
    """,

    'author': "SMARTEST",
    'website': "https://smartest.dz/",

    'category': 'Sales/Sales',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'smartest_base',
        'product'
    ],
    'data': [
        'views/product_views.xml',
        'report/product_product_templates.xml',
    ],
    'license': 'LGPL-3',
}
