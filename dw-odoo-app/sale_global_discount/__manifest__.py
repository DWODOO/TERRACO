# -*- coding: utf-8 -*-
{
    'name': "sale_global_discount",

    'summary': """
        GLOBAL DISCOUNT""",

    'description': """
        Long description of module's purpose
    """,

    'author': "SMARTEST",
    'website': "http://www.smartest.dz",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale','account'],

    # always loaded
    'data': [
        'data/data.xml',
        'views/sale.xml',
        'views/account_move.xml',
    ],
}
