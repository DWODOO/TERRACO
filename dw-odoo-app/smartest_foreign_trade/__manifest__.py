# -*- coding: utf-8 -*-
{
    'name': "Foreign Trade",
    'summary': "Manage Foreign Trade file and forms",
    'version': '1.0.0',
    'depends': ['smartest_stock_landed_costs','smartest_sale',
    ],
    'author': 'SMARTEST',
    'website': 'https://www.smartest.dz',
    'category': 'Purchase',
    'sequence': 80,
    'data': [
        # security
        'security/security.xml',
        'security/ir.model.access.csv',
        # data
        'data/sequence.xml',
        # views
        'views/export_folder.xml',
        'views/account_move_views.xml',
        'views/purchase_order_views.xml',
        'views/res_bank_agency_views.xml',
        'views/smartest_import_plan_views.xml',
        'views/smartest_import_file_views.xml',
        'views/stock_landed_cost_views.xml',
        'views/smartest_import_folder.xml',
        'views/stock_valuation_adjustment_lines.xml',
        # report
        # 'report/import_file_report.xml',
        # menu
        'menus.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
