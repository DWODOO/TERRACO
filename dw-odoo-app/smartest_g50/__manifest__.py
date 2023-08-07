# -*- coding: utf-8 -*-
{
    'name': "smartest_g50",

    'summary': """
    """,

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
    'depends': ['base','account','l10n_dz_payroll','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/g50_sequence.xml',
        'views/g_fifty.xml',
    ],
}
