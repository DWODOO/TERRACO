# -*- coding: utf-8 -*-
{
    'name': 'Portal access to Payslips',
    'category': 'Website/Website',
    'sequence': 30,
    'summary': 'Allow employees to consult their payslips on the portal',
    'description': """
    """,
    'author': 'SMARTEST - ALGERIA',
    'website': 'www.smartest.dz',
    'depends': [
        'portal',
        'hr_payroll',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/payslip_templates.xml',
        'views/hr_salary_rule_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
