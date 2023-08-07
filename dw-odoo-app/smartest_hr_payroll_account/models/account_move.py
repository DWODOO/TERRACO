# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA

# Import Odoo libs
from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee"
    )
    salary_rule_id = fields.Many2one(
        'hr.salary.rule',
        string='Salary Rule'
    )
    debit_test = fields.Monetary(
        string='Debit',
        default=0.0,
        currency_field='company_currency_id'
    )
    credit_test = fields.Monetary(
        string='Credit',
        default=0.0,
        currency_field='company_currency_id'
    )


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_payroll = fields.Boolean(
        'is Payroll'
    )
    is_test = fields.Boolean(
        'is test'
    )
