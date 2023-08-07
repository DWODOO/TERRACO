# -*- coding: utf-8 -*-
{
    'name': 'Algeria - HR Leave & Payroll Management System',
    'version': '0.1',
    'category': 'Localization',
    'description': """
        This module adapts the algerian Payroll/Leave standards.
        """,
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'depends': [
        'hr_holidays',
        'hr_work_entry_contract_enterprise',
        'smartest_hr_payroll'
    ],
    'data': [
        # data
        'data/work_entry_type_data.xml',
        'data/salary_rule_data.xml',
        # Security
        'security/ir.model.access.csv',
        # views
        'views/payslip_views.xml',

        'views/smartest_hr_payroll_leave_allowance_attributions_views.xml',
        'views/smartest_hr_payroll_leave_allowance_views.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
