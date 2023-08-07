# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA

# Import Odoo libs
from odoo import fields, models


class PayrollAccount(models.Model):
    _name = 'payroll.account'
    _description = 'Payroll Accounting'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        "Name"
    )
    line_ids = fields.One2many(
        'payroll.account.line',
        'payroll_account_id',
        'Payroll Account Lines',
    )


class PayrollRuleConfig(models.Model):
    _name = 'payroll.account.rule_config'
    _description = 'Payroll Accounting Rule Configuration'

    salary_rule_id = fields.Many2one(
        'hr.salary.rule',
        string='Salary Rules'
    )
    category_id = fields.Many2one(
        related='salary_rule_id.category_id'
    )
    code = fields.Char(
        related='salary_rule_id.code'
    )
    minus = fields.Boolean(
        default=False, string="Minus"
    )


class PayrollAccountLine(models.Model):
    _name = 'payroll.account.line'
    _description = 'Payroll Accounting Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        "Name"
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id
    )
    payroll_account_id = fields.Many2one(
        'payroll.account',
        string='Payroll Account',
        required=True,
        default=lambda self: self.env.ref('smartest_hr_payroll_account.payroll_account_record')
    )
    account_id = fields.Many2one(
        'account.account',
        string='Account',
        required=True
    )
    status = fields.Selection([
        ('debit', 'Debit'),
        ('credit', 'Credit')
    ],
        string="Status",
        default="debit",
        required=True
    )
    type = fields.Selection([
        ('employee', 'By Employee'),
        ('department', 'By Department'),
        ('all', 'All employee'),
    ],
        string="Type",
        required=True,
        default="employee",
    )
    department_id = fields.Many2one(
        'hr.department',
        'Department',
        required=False,
        index=True
    )
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Employees'
    )
    salary_rule_ids = fields.Many2many(
        'payroll.account.rule_config',
        string='Salary Rules'
    )
    active = fields.Boolean(
        default=True
    )

    def get_employees(self):
        # Initialize variables
        HrEmployee = self.env['hr.employee']
        employees = HrEmployee.browse()
        company = self.env.user.company_id

        for line in self:
            if line.type == 'employee':
                # Append employees selected manually
                employees += line.employee_ids

            elif line.type == 'department' and line.department_id:
                # Append Department employees
                employees += line.department_id.member_ids

            elif line.type == 'all':
                # Initialize company
                company = line.company_id or company

                # Get all the company employees
                company_employees = HrEmployee.search([('company_id', 'in', (company.id, False))])

                # In the case type == 'all', append all the company employees
                employees += company_employees

        # Return
        return employees

