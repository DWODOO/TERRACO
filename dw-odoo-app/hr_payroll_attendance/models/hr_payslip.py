# -*- coding:utf-8 -*-
from datetime import datetime, time

from odoo import api, models, fields, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        def create_empty_worked_lines(employee, contract, date_from, date_to):
            attendances = {
                'name': _('Attendance'),
                'sequence': 10,
                'code': 'PRES',
                'number_of_days': contract.days_per_month,
                'number_of_hours': contract.hours_per_month,
                'contract_id': contract.id,
            }

            day_from = datetime.combine(fields.Date.from_string(date_from), time.min)
            day_to = datetime.combine(fields.Date.from_string(date_to), time.max)

            valid_attendances = [
                ('employee_id', '=', employee.id),
                ('check_in', '>=', day_from),
                ('check_in', '<=', day_to),
            ]

            return attendances, valid_attendances

        work = []
        for contract in contracts:
            worked_attn, valid_attn = create_empty_worked_lines(
                contract.employee_id,
                contract,
                date_from,
                date_to
            )

            min_attendance_worked_hours = contract.company_id.min_attendance_worked_hours
            attendance_ids = self.env['hr.attendance'].search(valid_attn).filtered(lambda att: att.check_out)
            iso_days = set()
            for attn in attendance_ids:
                iso_day = attn.check_in.isocalendar()
                if iso_day not in iso_days:
                    iso_days.add(iso_day)

            for iso_day in iso_days:
                attendances = attendance_ids.filtered(lambda attn: attn.check_in.isocalendar() == iso_day)
                number_of_hours = round(
                    sum(attn.worked_hours for attn in attendances),
                    2
                )
                if number_of_hours >= min_attendance_worked_hours:
                    worked_attn['number_of_days'] += 1
                    worked_attn['number_of_hours'] += number_of_hours
            work.append(worked_attn)
        res = super(HrPayslip, self).get_worked_day_lines(contracts, date_from, date_to)
        for element in res:
            if element.get('code', False) == 'WORK100':
                contract = self.env['hr.contract'].browse(element['contract_id'])
                element['number_of_days'] = contract.days_per_month
                element['number_of_hours'] = contract.hours_per_month
                break
        res.extend(work)
        return res
