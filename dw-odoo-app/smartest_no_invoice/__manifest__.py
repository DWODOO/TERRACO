# -*- coding: utf-8 -*-
{
    'name': "smartest_no_invoice",

    'summary': """
        Not Declared Invoice""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Smartest",
    'website': "http://www.smartest.dz",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'smartest_sale',
        'smartest_l10n_dz',
    ],
    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'data/account.account.csv',
        'data/fiscal_position.xml',
        'views/fiscal_position.xml',
        'views/account_move_view.xml',
        'views/account_payment_view.xml',
        'views/sale_order_view.xml',
        'data/sequence.xml',
        # 'report/reports.xml',
        # 'report/livraison_valorise.xml',
    ],

}
