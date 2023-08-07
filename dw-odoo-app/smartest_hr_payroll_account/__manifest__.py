# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA
{
    'name': 'Payroll Accounting - By SMARTEST ALGERIA',
    'version': '16.0.0',
    'category': 'Localization',
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'description': "Improvements of Payroll Accounting By SMARTEST ALGERIA",
    'depends': [
        'smartest_hr_payroll',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/payroll_account_data.xml',
        'views/hr_payroll_account_views.xml',
        'views/hr_payslip_run_views.xml',
        'views/payroll_transfer.xml',
        'wizard/hr_payroll_account_verif.xml',
    ],
    # "post_init_hook": "post_init_hook",
    'license': 'LGPL-3',
}
