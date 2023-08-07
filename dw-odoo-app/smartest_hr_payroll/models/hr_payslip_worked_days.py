# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA

# Import Odoo libs
from odoo import api, fields, models


class SmartestHrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    @api.onchange('number_of_days')
    def _onchange_number_of_days(self):
        hours_per_day = self.payslip_id.struct_id.type_id.default_resource_calendar_id.hours_per_day
        if hours_per_day:
            self.number_of_hours = self.number_of_days * hours_per_day

    @api.onchange('number_of_hours')
    def _onchange_number_of_hours(self):
        hours_per_day = self.payslip_id.struct_id.type_id.default_resource_calendar_id.hours_per_day
        if hours_per_day:
            self.number_of_days = self.number_of_hours / hours_per_day

    @api.depends('work_entry_type_id.smartest_hourly_paid',
                 'work_entry_type_id.smartest_paid_in_calendar',
                 'contract_id.paid_hourly_attendance',
                 'contract_id.smartest_paid_in_calendar',
                 'contract_id.smartest_work_entry_type_ids')
    def _compute_amount(self):
        for line in self:
            for worked_days in line.filtered(lambda wd: not wd.payslip_id.edited):
                if not worked_days.contract_id or worked_days.code == 'OUT':
                    worked_days.amount = 0
                    continue
                work_entry_type_id = worked_days.work_entry_type_id
                payslip_id = worked_days.payslip_id
                contract_id = payslip_id.contract_id
                smartest_work_entry_type_ids = contract_id.smartest_work_entry_type_ids
                smartest_paid_in_calendar = contract_id.smartest_paid_in_calendar
                theoretic_worked_days = 30 if (work_entry_type_id.smartest_paid_in_calendar or (
                            smartest_paid_in_calendar and work_entry_type_id in smartest_work_entry_type_ids)) else payslip_id.smartest_theoretic_worked_days

                if payslip_id.wage_type == "hourly":
                    if contract_id.paid_hourly_attendance or work_entry_type_id.smartest_hourly_paid:
                        amount = contract_id.hourly_wage * worked_days.number_of_hours if worked_days.is_paid else 0
                    else:
                        amount = contract_id.hourly_wage * worked_days.number_of_days if worked_days.is_paid else 0
                else:
                    if contract_id.paid_hourly_attendance or work_entry_type_id.smartest_hourly_paid:
                        amount = contract_id.contract_wage * worked_days.number_of_hours / (
                                payslip_id.smartest_theoretic_worked_hours or 1) if worked_days.is_paid else 0
                    else:
                        amount = contract_id.contract_wage * worked_days.number_of_days / (
                                theoretic_worked_days or 1) if worked_days.is_paid else 0
                worked_days.amount = amount
