# -*- coding: utf-8 -*-
{
    'name': "smartest_liasse_fiscale",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter moduledate_scopes in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','stock', 'account_reports'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/accounting_algerian_reports.xml',
        'data/algerian_balance_sheet.xml',
        'data/algerian_passive_balance.xml',
        'data/demo.xml',
        'data/sequence.xml',
        'views/import_export.xml',
        'views/result_fiscal_list.xml',
        'report/external_layout_extnd.xml',
        'report/res_partner_report.xml',
        'wizards/create_date.xml',
        'wizards/detail_client.xml',
        'views/smartest_account_move_line.xml',
        'views/res_company_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
