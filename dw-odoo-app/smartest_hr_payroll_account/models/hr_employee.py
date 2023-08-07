# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA

# Import Odoo libs
from odoo import fields, models


class SmartestHrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    payroll_account_line_id = fields.Many2one(
        'payroll.account.line',
        'Payroll Accounting'
    )


class SmartestHrEmployee(models.Model):
    _inherit = 'hr.employee'

    payroll_account_line_id = fields.Many2one(
        'payroll.account.line',
        'Payroll Accounting'
    )
