# -*- coding: utf-8 -*-
{
    'name': "smartest_dashboard_report",

    'summary': """
        subtitle on modules listing or smartest.dz""",

    'description': """
    """,

    'author': "SMARTEST",
    'website': "http://www.smartest.dz",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','board','account','stock','sale_enterprise'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_invoice_report.xml',
        'views/stock_move.xml',
        'views/sale_report.xml',
        'views/board_board.xml',
    ],
}
