# -*- coding:utf-8 -*-
{
    'name': 'Attendance on Payslips',
    'description': 'Get Attendance numbers onto Employee Payslips.',
    'version': '12.0.1',
    'website': 'www.smartest.dz',
    'author': 'SMARTEST - ALGERIA',
    'category': 'Human Resources',
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/hr_contract_views.xml',
        'views/hr_attendance_payroll_view.xml',
    ],
    'depends': [
        'hr_payroll',
        'hr_attendance',
    ],
    'license': 'LGPL-3',
}
