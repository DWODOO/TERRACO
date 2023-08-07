# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA

# Import Odoo libs
from odoo import fields, models


class PayslipHiddenLine(models.Model):
    _name = 'payslip.hidden.line'

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
    slip_id = fields.Many2one(
        'hr.payslip',
        string='Pay Slip',
        required=True,
        ondelete='cascade'
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True
    )
    rate = fields.Float(
        string='Rate (%)',
        default=100.0
    )
    amount = fields.Float(
        "Amount"
    )
    quantity = fields.Float(
        default=1.0
    )
    total = fields.Float(
        string='Total'
    )


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    hidden_line_ids = fields.One2many(
        'payslip.hidden.line',
        'slip_id',
        string='Hidden Payslip Lines'
    )

    def compute_sheet(self):
        res = super(HrPayslip, self).compute_sheet()
        self.mapped('hidden_line_ids').unlink()
        for line in self.mapped('line_ids').filtered(lambda line: not line.appears_on_payslip):
            self.env['payslip.hidden.line'].create({
                'salary_rule_id': line.salary_rule_id.id,
                'slip_id': line.slip_id.id,
                'employee_id': line.employee_id.id,
                'rate': line.rate,
                'amount': line.amount,
                'quantity': line.quantity,
                'total': line.total,
            })
        self.mapped('line_ids').filtered(lambda line: not line.appears_on_payslip).unlink()
        return res
