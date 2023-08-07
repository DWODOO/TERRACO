# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA
from datetime import date
import calendar
# Import Odoo libs
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round


class SmartestHrPayrollLeaveAllowanceLine(models.Model):
    _name = 'smartest.hr.payroll.leave.allowance.line'

    smartest_payroll_leave_id = fields.Many2one('smartest.hr.payroll.leave.allowance',
                                                string='payroll leave')

    smartest_company_id = fields.Many2one(string='Company',
                                          related='smartest_payroll_leave_id.smartest_company_id',
                                          )

    smartest_company_currency = fields.Many2one('res.currency',
                                                string='Currency',
                                                related='smartest_company_id.currency_id')

    smartest_date_start = fields.Date('Start Date',
                                      tracking=True,
                                      required=True
                                      )
    smartest_date_end = fields.Date('End Date',
                                    tracking=True,
                                    required=True
                                    )
    smartest_payslip_id = fields.Many2one('hr.payslip',
                                          string='Payslip',
                                          readonly=True,
                                          )
    smartest_days_leave_attribution = fields.Float(string='Days Attribution',
                                                   default=2.5
                                                   )

    smartest_leave_allowance = fields.Monetary('Leave Allowance Per Month',
                                               currency_field="smartest_company_currency",
                                               required=True
                                               )
    smartest_active = fields.Boolean(string='Active',
                                     default=True
                                     )

    @api.onchange('smartest_date_start')
    def onchange_date_start(self):
        if self.smartest_date_start:
            month_date = date(self.smartest_date_start.year, int(self.smartest_date_start.month), 1)
            self.smartest_date_end = month_date.replace(day=calendar.monthrange(month_date.year, month_date.month)[1])

    @api.constrains('smartest_date_start', 'smartest_date_end')
    def _check_date_validity(self):
        if any(
                record.smartest_date_start and record.smartest_date_end and record.smartest_date_end < record.smartest_date_start
                for record in self):
            raise ValidationError(
                _('Date start must be lower !!!')
            )


class SmartestHrPayrollLeaveAllowance(models.Model):
    _name = 'smartest.hr.payroll.leave.allowance'

    def get_exercice(self, date_start, start=False):
        actual_year = date_start.year
        start_date_exercice_for_actual_year = str(actual_year) + '-07-01'
        date_start_exercice = fields.Date.from_string(start_date_exercice_for_actual_year)
        if date_start < date_start_exercice and start:
            actual_year -= 1
        elif date_start >= date_start_exercice and not start:
            actual_year += 1

        return actual_year

    def _default_smartest_date_start_exercice(self):
        today = fields.Date.today()
        actual_year = self.get_exercice(today, start=True)
        return fields.Date.from_string(str(actual_year) + '-07-01')

    smartest_company_id = fields.Many2one('res.company',
                                          string='Company',
                                          required=True,
                                          default=lambda self: self.env.company
                                          )
    name = fields.Char(string='Name', translate=True, compute="compute_name")
    smartest_date_start_exercice = fields.Date('Start Date',
                                               tracking=True,
                                               store=True,
                                               default=_default_smartest_date_start_exercice,
                                               compute="compute_date_start",
                                               readonly=False
                                               )
    smartest_date_end_exercice = fields.Date('End Date',
                                             tracking=True,
                                             )
    smartest_employee_id = fields.Many2one('hr.employee',
                                           string='Employee',
                                           required=True,
                                           )
    smartest_leave_allowance_exercice = fields.Float('Leave Allowance Per Exercice',
                                                     compute="compute_leave_allowance_days_per_exercice",
                                                     store=True, readonly=False,

                                                     )
    smartest_days_leave_attribution_exercice = fields.Float(string='Days Attribution Per Exercice',
                                                            compute="compute_leave_allowance_days_per_exercice",
                                                            store=True, readonly=False,
                                                            )
    smartest_remaining_leave_allowance_exercice = fields.Float('Remaining Leave Allowance Per Exercice',
                                                               compute="compute_remaining_leave_allowance_days_per_exercice",
                                                               store=True, readonly=True,

                                                               )
    smartest_remaining_days_leave_attribution_exercice = fields.Float(string='Remaining Days Attribution Per Exercice',
                                                                      compute="compute_remaining_leave_allowance_days_per_exercice",
                                                                      store=True, readonly=True,

                                                                      )
    smartest_given_leave_allowance_exercice = fields.Float('Given Leave Allowance Per Exercice',
                                                           store="1", readonly=True,
                                                           )
    smartest_given_days_leave_attribution_exercice = fields.Float(string='Given Days Attribution Per Exercice',
                                                                  store="1", readonly=True,
                                                                  )
    smartest_active = fields.Boolean(string='Active',
                                     default=True
                                     )
    smartest_allowance_leave_ids = fields.One2many('smartest.hr.payroll.leave.allowance.line',
                                                   'smartest_payroll_leave_id',
                                                   'Allowance Leave Per Month',
                                                   copy=True,
                                                   readonly=True
                                                   )
    payslips_count = fields.Float('Number of Payslips',
                                  compute='_compute_payslips_count')
    allowance_count = fields.Float('Number of Payslips',
                                   compute='_compute_leave_days_allowance_attributed_count')
    days_count = fields.Float('Number of Payslips',
                              compute='_compute_leave_days_allowance_attributed_count')

    _sql_constraints = [
        ('employee_exercice_company_uniq',
         'unique (smartest_employee_id,smartest_date_start_exercice,smartest_company_id,smartest_active)',
         _('The Leave Exercice of the Employee must be unique per company !'))
    ]

    @api.constrains('smartest_date_start_exercice', 'smartest_date_end_exercice')
    def _check_date_validity(self):
        if any(
                record.smartest_date_start_exercice and record.smartest_date_end_exercice and record.smartest_date_end_exercice < record.smartest_date_start_exercice
                for record in self):
            raise ValidationError(
                _('Date start must be lower !!!')
            )

    def _get_payslips_count(self):
        """ Helper to compute the Number of Payslips for the current employees
            :returns dict where the key is the employee id, and the value is Number of Payslips.
        """
        payslips = self.env["hr.payslip"].search([
            ('employee_id', 'in', self.smartest_employee_id.ids),
            ('payroll_leave_ids', 'in', self.ids), ])
        employees = payslips.employee_id
        return dict(
            (employee['id'], len(payslips.filtered(lambda line: line.employee_id.id == employee.id))) for employee in employees)

    def _compute_payslips_count(self):
        payslips_count_ids = {}
        if self.ids:
            payslips_count_ids = self._get_payslips_count()
        for payroll_leave in self:
            value = float_round(payslips_count_ids.get(payroll_leave.smartest_employee_id.id, 0.0), precision_digits=2)
            payroll_leave.payslips_count = value

    def _get_leave_days_allowance_attributed_count(self):

        return self.env["smartest.hr.payroll.leave.allowance.attributions"].search([
            ('smartest_employee_id', '=', self.smartest_employee_id.id),
            ('payroll_leave_id', '=', self._origin.id), ])

    def _compute_leave_days_allowance_attributed_count(self):

        for payroll_leave in self:
            allowance = days = 0
            leave_allowance_attributions_count_ids = payroll_leave._get_leave_days_allowance_attributed_count()
            if leave_allowance_attributions_count_ids:
                allowance = sum(leave_allowance_attributions_count_ids.mapped("smartest_leave_allowance_attributed"))
                days = sum(leave_allowance_attributions_count_ids.mapped("smartest_days_attributed"))
            payroll_leave.allowance_count = payroll_leave.smartest_given_leave_allowance_exercice = allowance
            payroll_leave.days_count = payroll_leave.smartest_given_days_leave_attribution_exercice = days

    @api.depends('smartest_date_start_exercice')
    @api.onchange('smartest_date_start_exercice')
    def compute_date_start(self):
        for record in self:
            if record.smartest_date_start_exercice:
                actual_year = record.get_exercice(record.smartest_date_start_exercice, start=True)
                exercice_start_date = str(actual_year) + '-07-01'
                record.smartest_date_start_exercice = fields.Date.from_string(exercice_start_date)

    @api.onchange('smartest_date_start_exercice','smartest_date_end_exercice')
    def onchange_date_start(self):
        for record in self:
            if record.smartest_date_start_exercice:
                today = record.smartest_date_start_exercice
                actual_year = record.get_exercice(today, start=False)
                exercice_end_date = str(actual_year) + '-06-30'
                record.smartest_date_end_exercice = fields.Date.from_string(exercice_end_date)

    @api.depends('smartest_employee_id', 'smartest_date_start_exercice')
    def compute_name(self):
        for record in self:
            name = ""
            if record.smartest_employee_id and record.smartest_date_start_exercice:
                name = record.smartest_employee_id.name + " Exercice " + str(
                    record.smartest_date_start_exercice.year + 1)
            record.name = name

    @api.depends('smartest_allowance_leave_ids')
    def compute_leave_allowance_days_per_exercice(self):
        for record in self:
            allowance_leave = allowance_leave_days = 0

            if record.smartest_allowance_leave_ids:
                allowance_leave = sum(record.smartest_allowance_leave_ids.mapped("smartest_leave_allowance"))
                allowance_leave_days = sum(
                    record.smartest_allowance_leave_ids.mapped("smartest_days_leave_attribution"))

            record.smartest_leave_allowance_exercice = allowance_leave
            record.smartest_days_leave_attribution_exercice = allowance_leave_days

    @api.depends('smartest_leave_allowance_exercice', 'smartest_days_leave_attribution_exercice',
                 'smartest_given_leave_allowance_exercice', 'smartest_given_days_leave_attribution_exercice')
    def compute_remaining_leave_allowance_days_per_exercice(self):
        for record in self:
            record.smartest_remaining_leave_allowance_exercice = record.smartest_leave_allowance_exercice - record.smartest_given_leave_allowance_exercice
            record.smartest_remaining_days_leave_attribution_exercice = record.smartest_days_leave_attribution_exercice - record.smartest_given_days_leave_attribution_exercice
