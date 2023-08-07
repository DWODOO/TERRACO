# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA
{
    'name': 'LEAVE  - By SMARTEST ALGERIA',
    'version': '1.0.0',
    'category': 'hidden',
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'description': "TIME OFF By SMARTEST ALGERIA",
    'depends': [
        'hr_holidays',
        'hr_contract',
    ],
    'data': [
        # Security

        'security/hr_leave_security.xml',
        'security/ir.model.access.csv',
        'report/hr_leave_title_report.xml',

        # Data
        'data/leave_categories_data.xml',
        'data/hr_leave_type.xml',
        'data/mail_template.xml',


        # Views
        'views/categories_leave.xml',
        'views/hr_leave_type_views.xml',
        'views/res_config_settings_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_leave_accrual_views.xml',
        'views/range_days_views.xml',
        'views/hr_leave_views.xml',

        'data/cron.xml',
    ],
    'license': 'LGPL-3',
}
