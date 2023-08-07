# -*- coding: utf-8 -*-
{
    'name': 'Algeria - HR Leaves Management System',
    'version': '12.0.1',
    'category': 'Localization',
    'description': """
        This module adapt the default odoo Leaves module to the algerian standards.
        """,
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'depends': [
        'hr_holidays',
        'l10n_dz_payroll'
    ],
    'data': [
        'data/leave_type_data.xml',
        'wizard/hr_leave_cumulation_wizard_views.xml',
        'views/payslip_views.xml',
        'security/ir.model.access.csv',
        'data/salary_structure_data.xml',
        'data/salary_rules_data.xml',
        'security/hr_security.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
