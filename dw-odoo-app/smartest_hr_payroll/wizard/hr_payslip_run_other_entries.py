import pdb

from odoo import models, fields, api, _


class HrPayslipRunOtherEntriesWizard(models.TransientModel):
    _name = "hr.payslip.run.other.entries"

    types = fields.Selection([
        ('department', 'By Department'),
        ('employee', 'Employee'),
        ('employees', 'Employees'),
        ('all', 'All')
    ], default='all')
    compute_condition = fields.Selection([
        ('amount', 'Amount'),
        ('condition', 'Based on Condition'),
    ])
    quantity = fields.Float(
        default=1
    )
    slip_run_id = fields.Many2one(
        'hr.payslip.run'
    )
    slip_ids = fields.One2many(
        'hr.payslip',
        related='slip_run_id.slip_ids'
    )
    input_line_ids = fields.One2many(
        'hr.payslip.input.inherit',
        'payslip_run_other_entries_id'
    )
    contributory_base = fields.Float()
    tax_base = fields.Float()
    department_id = fields.Many2one(
        'hr.department'
    )
    employee_id = fields.Many2one(
        'hr.employee'
    )
    employee_ids = fields.Many2many(
        'hr.employee',
        'hr_employee_payslip_rule_batch_rel',
        'employee_id',
        'other_id'
    )

    def get_work100(self, slip_id):
        return slip_id.contract_id.days_per_month if not slip_id.contract_id.paid_hourly_attendance \
            else slip_id.contract_id.hours_per_month

    def compute_amount(self, line_input, slip_id, quantity):
        """ This methode will return either the given amount or the computed one """
        if self.compute_condition == 'amount':
            amount = line_input.amount
        else:
            amounts = slip_id.line_ids.filtered(lambda o: o if o.salary_rule_id == line_input.salary_rule_id else None)\
                .mapped('amount')
            amount = ((amounts[0] / self.get_work100(slip_id)) if len(amounts) > 0 else 0) * quantity
        return amount

    def get_input_values(self, slip_id, quantity):
        vals = []
        for line_input in self.input_line_ids:

            amount = self.compute_amount(line_input, slip_id, quantity)

            vals.append({
                'input_type_id': line_input.input_type_id.id,
                'name': line_input.name,
                'amount': amount,
                'payslip_id': slip_id.id,
                'contract_id': slip_id.contract_id.id,
            })
        return vals

    def get_payslips(self):
        if self.types == 'employee':
            slip_ids = self.slip_ids.filtered(
                lambda o: o if o.department_id == self.department_id or o.employee_id == self.employee_id else None)
        elif self.types == 'employees':
            slip_ids = self.slip_ids.filtered(
                lambda o: o if o.department_id == self.department_id or o.employee_id in self.employee_ids else None)
        elif self.types == 'department':
            slip_ids = self.slip_ids.filtered(lambda o: o if o.department_id == self.department_id else None)
        else:
            slip_ids = self.slip_ids
        return slip_ids

    def action_validate_entries(self):
        slip_ids = self.get_payslips()
        for slip in slip_ids:
            vals = self.get_input_values(slip, self.quantity)
            self.env['hr.payslip.input'].create(vals)
            slip.compute_sheet()
        self.slip_run_id.compute_payroll_run()

    @api.onchange('department_id')
    def onchange_department_id(self):
        res = {}
        if self.department_id:
            res['domain'] = {'employee_id': [('department_id', '=', self.department_id.id)], 'employee_ids': [('department_id', '=', self.department_id.id)]}
        else:
            res['domain'] = {'employee_id': [], 'employee_ids': []}
        return res


class HrPayslipInput(models.TransientModel):
    _name = 'hr.payslip.input.inherit'

    name = fields.Char(
        'Name'
    )
    input_type_id = fields.Many2one(
        'hr.payslip.input.type',
    )
    amount = fields.Float(
        'Amount'
    )
    code = fields.Char(
        'Code'
    )
    sequence = fields.Integer(
        'Sequence'
    )
    payslip_run_other_entries_id = fields.Many2one(
        'hr.payslip.run.other.entries'
    )
    salary_rule_id = fields.Many2one(
        'hr.salary.rule'
    )
    compute_condition = fields.Selection([
        ('amount', 'Amount'),
        ('condition', 'Based on Condition'),
    ], related="payslip_run_other_entries_id.compute_condition")
