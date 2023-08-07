# -*- coding: utf-8 -*-
{
    'name': "Vente Details",

    'summary': """
        This module simplify the sale, payment and return,
        make in it all in one interface""",

    'description': """
    """,

    'author': "SMARTEST Algerie",
    'website': "http://www.smartest.dz",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','product','account','location_security'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_details.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_details/static/src/js/sale_detail_scanner.js',
        ],
        'web.assets_qweb': [
        ],
    }
}
