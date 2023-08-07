# -*- coding: utf-8 -*-
{
    'name': "pricelist - BY SMARTEST",

    'summary': """
        Add improvements for Pricelist management""",

    'description': """
        Long description of module's purpose
    """,

    'author': "SMARTEST",
    'website': "https://smartest.dz/",

    'category': 'Sales/Sales',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale',
        'stock',
        'purchase'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/margin_sequence.xml',
        'views/smartest_price_margin_view.xml',
    ],
}
