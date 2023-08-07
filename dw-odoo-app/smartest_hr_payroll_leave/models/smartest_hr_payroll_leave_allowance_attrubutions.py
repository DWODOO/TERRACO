# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA
# Import Odoo libs
from odoo import _, api, fields, models


class SmartestHrPayrollLeaveAllowanceAttrbutions(models.Model):
    _name = 'smartest.hr.payroll.leave.allowance.attributions'

    name = fields.Char(string='Name',
                       translate=True,
                       compute="compute_name")
    smartest_leave_id = fields.Many2one('hr.leave',
                                        string='Time Off',
                                        readonly=True)

    smartest_holiday_allocation_id = fields.Many2one(related='smartest_leave_id.holiday_allocation_id',
                                                 store=True)

    smartest_leave_id_state = fields.Selection(related='smartest_leave_id.state',
                                               store=True)

    smartest_date_start_exercice = fields.Date('Start Date',
                                               tracking=True,
                                               store=True,
                                               related='smartest_holiday_allocation_id.date_from',
                                               )
    smartest_date_end_exercice = fields.Date('End Date',
                                             tracking=True,
                                             store=True,
                                             compute="compute_date_start",
                                             )
    smartest_request_date_from = fields.Date('Start Date',
                                             tracking=True,
                                             store=True,
                                             related='smartest_leave_id.request_date_from',
                                             )
    smartest_request_date_to = fields.Date('End Date',
                                           tracking=True,
                                           store=True,
                                           related='smartest_leave_id.request_date_to',
                                           )
    smartest_employee_id = fields.Many2one('hr.employee',
                                           string='Employee',
                                           readonly=True,
                                           )
    smartest_payslip_id = fields.Many2one('hr.payslip',
                                          string='Payslip',
                                          readonly=True,
                                          )
    smartest_leave_allowance_attributed = fields.Float('Leave Allowance Attributed',
                                                       compute="compute_leave_allowance_days_per_exercice",
                                                       store=True

                                                       )
    smartest_days_attributed = fields.Float(string='Days Attributed',
                                            compute="compute_leave_allowance_days_per_exercice",
                                            store=True
                                            )
    payroll_leave_id = fields.Many2one('smartest.hr.payroll.leave.allowance',
                                       string='allowance Leave Exercice')

    @api.depends('smartest_employee_id', 'smartest_date_start_exercice')
    def compute_name(self):
        for record in self:
            name = ""
            if record.smartest_employee_id and record.smartest_date_start_exercice:
                name = record.smartest_employee_id.name + " - Attribution Exercice " + str(
                    record.smartest_date_start_exercice.year )
            record.name = name

    def get_exercice(self, date_start, start=False):
        actual_year = date_start.year
        start_date_exercice_for_actual_year = str(actual_year) + '-07-01'
        date_start_exercice = fields.Date.from_string(start_date_exercice_for_actual_year)
        if date_start < date_start_exercice and start:
            actual_year -= 1
        elif date_start >= date_start_exercice and not start:
            actual_year += 1

        return actual_year

    @api.depends('smartest_date_start_exercice')
    def compute_date_start(self):
        for record in self:
            if record.smartest_date_start_exercice:
                today = record.smartest_date_start_exercice
                actual_year = record.get_exercice(today, start=False)
                exercice_end_date = str(actual_year) + '-06-30'
                record.smartest_date_end_exercice = fields.Date.from_string(exercice_end_date)

    @api.model
    def action_leave_allowance_attributions_analysis(self):
        domain = []

        if self.env.context.get('active_ids'):
            domain = [('payroll_leave_id', 'in', self.env.context.get('active_ids', []))]

        return {
            'name': _('Leave Allowance Attrbutions Analysis'),
            'type': 'ir.actions.act_window',
            'res_model': 'smartest.hr.payroll.leave.allowance.attributions',
            'view_mode': 'tree',
            'search_view_id': self.env.ref(
                'smartest_hr_payroll_leave.smartest_hr_payroll_leave_allowance_attributions_search').id,
            'domain': domain,
            'context': {
                'search_default_holiday_status_id': True,
            }
        }
