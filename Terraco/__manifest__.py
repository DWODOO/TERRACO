# -*- coding: utf-8 -*-
{
    'name': "Terraco DW",

    'summary': """
        """,
    'version': '1.1.0',
    'description': """
        specific dev for Terraco

    """,
    'author': "My Company",
    'website': "",
    'category': '',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_restourne_view.xml',
        'views/account_move_views.xml',
        'views/res_users_views.xml',
        'views/sale_order.xml',
        'wizard/restourne_wizard.xml',
        'data/product_template.xml',
        'data/ir_action_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
