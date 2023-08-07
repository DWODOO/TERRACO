# -*- coding:utf-8 -*-
import datetime
from collections import defaultdict
from datetime import datetime, time
import pandas as pd
from dateutil.relativedelta import relativedelta
from odoo import api, models, fields, _
from odoo.addons.resource.models.resource import HOURS_PER_DAY
from odoo.osv import expression
from odoo.tools.date_utils import get_timedelta

class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    @api.model
    def _update_accrual(self):
        """
            Method called by the cron task in order to increment the number_of_days when
            necessary.
        """
        # Get the current date to determine the start and end of the accrual period
        today = datetime.combine(fields.Date.today(), time(0, 0, 0))
        this_year_first_day = today + relativedelta(day=1, month=1)
        end_of_year_allocations = self.search(
            [('allocation_type', '=', 'accrual'), ('state', '=', 'validate'), ('accrual_plan_id', '!=', False),
             ('employee_id', '!=', False),
             '|', ('date_to', '=', False), ('date_to', '>', fields.Datetime.now()),
             ('lastcall', '<', this_year_first_day)])
        end_of_year_allocations._end_of_year_accrual()
        end_of_year_allocations.flush()
        allocations = self.search(
            [('allocation_type', '=', 'accrual'), ('state', '=', 'validate'), ('accrual_plan_id', '!=', False),
             ('employee_id', '!=', False),
             '|', ('date_to', '=', False), ('date_to', '>', fields.Datetime.now()),
             '|', ('nextcall', '=', False), ('nextcall', '<=', today)])
        allocations._process_accrual_plans()


    def get_worked_days(self, employee_id, end_date):
        date_planified_action = self.env.ref('hr_holidays.hr_leave_allocation_cron_accrual').nextcall
        # days = date_planified_action.days
        datetime_test_jan = datetime.strptime(str(end_date), '%Y-%m-%d')
        h = pd.Timestamp(str(datetime_test_jan)) + pd.offsets.MonthEnd(n=1)
        last_day_of_month = h.date().strftime("%d")
        nextcall_str = datetime_test_jan.strftime('%Y-%m')
        day = date_planified_action.strftime("%d")
        contract_id = employee_id.contract_id
        if nextcall_str == contract_id.date_start.strftime(
                '%Y-%m') or contract_id.date_end and nextcall_str == contract_id.date_end.strftime('%Y-%m'):
            if nextcall_str == contract_id.date_start.strftime('%Y-%m'):
                worked_days = int(last_day_of_month)-int(contract_id.date_start.strftime("%d"))
                if worked_days:
                    if worked_days >= int(day):
                        return False
                    elif int(day) > worked_days:
                        return worked_days
                else:
                    return 0
            else:
                if contract_id.date_end and nextcall_str == contract_id.date_end.strftime('%Y-%m'):
                    if int(contract_id.date_end.strftime("%d")) >=int(day):
                        return False
                    elif int(contract_id.date_end.strftime("%d")) <int(day):
                        return int(contract_id.date_end.strftime("%d"))
        else:
            return False

    @api.model
    def get_number_of_days_to_be_allocated(self, employee_id, end_date):
        contract_id = employee_id.contract_id
        range_days = self.env['range.days']
        nextcall = self.env.ref('hr_holidays.hr_leave_allocation_cron_accrual').nextcall.date()
        datetime_test_jan = datetime.strptime(str(end_date), '%Y-%m-%d')
        date_jan = datetime_test_jan.strftime('%Y-%m')

        worked_days = 0
        if date_jan == contract_id.date_start.strftime(
                '%Y-%m') or contract_id.date_end and date_jan == contract_id.date_end.strftime('%Y-%m'):
            worked_days = self.get_worked_days(employee_id, end_date)
        print(employee_id.name,worked_days,type(worked_days),end_date)
        if self.get_worked_days(employee_id, end_date) is False:
            return False
        else:
            if worked_days:
                if not employee_id.working_in_south_area:
                    for range in range_days.search([], order='smartest_days_worked asc').filtered(
                            lambda p: p.smartest_area == "north"):
                        if worked_days <= range.smartest_days_worked:
                            return range.smartest_number_of_days_allocated
                else:
                    for range in range_days.search([], order='smartest_days_worked asc').filtered(
                            lambda p: p.smartest_area == "south"):
                        if worked_days <= range.smartest_days_worked:
                            return range.smartest_number_of_days_allocated

    def worked_days_in_july(self, employee_id, days_added_per_level):
        contract_date_start_month = employee_id.contract_id.date_start.strftime('%Y-%m')
        july = datetime.now().replace(month=7).strftime('%Y-%m')
        date_july = datetime.now().replace(month=7).strftime('%Y-%m-%d')
        h = pd.Timestamp(str(date_july)) + pd.offsets.MonthEnd(n=1)
        last_day_of_month = h.date().strftime("%d")
        if contract_date_start_month == july:
            number_of_days_to_be_allocated = self.get_number_of_days_to_be_allocated(
                employee_id, date_july)
            number_of_days_added_in_july = number_of_days_to_be_allocated - days_added_per_level
            return number_of_days_added_in_july
        elif employee_id.contract_id.date_end and employee_id.contract_id.date_end.strftime(
                '%Y-%m') == july:
            number_of_days_to_be_allocated = self.get_number_of_days_to_be_allocated(
                employee_id, date_july)
            number_of_days_added_in_july = number_of_days_to_be_allocated - days_added_per_level
            return number_of_days_added_in_july

    def _process_accrual_plan_level(self, level, start_period, start_date, end_period, end_date):
        """
        Returns the added days for that level
        """
        self.ensure_one()
        if level.is_based_on_worked_time:
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = datetime.combine(end_date, datetime.max.time())
            worked = \
                self.employee_id._get_work_days_data_batch(start_dt, end_dt,
                                                           calendar=self.employee_id.resource_calendar_id) \
                    [self.employee_id.id]['hours']
            left = self.employee_id.sudo()._get_leave_days_data_batch(start_dt, end_dt,
                                                                      domain=[('time_type', '=', 'leave')])[
                self.employee_id.id]['hours']
            work_entry_prorata = worked / (left + worked) if worked else 0
            added_value = work_entry_prorata * level.added_value
        else:
            added_value = level.added_value
        # Convert time in hours to time in days in case the level is encoded in hours
        if level.added_value_type == 'hours':
            added_value = added_value / (self.employee_id.sudo().resource_id.calendar_id.hours_per_day or HOURS_PER_DAY)
        period_prorata = 1
        contract_date_start_month = self.employee_id.contract_id.date_start.strftime('%Y-%m')
        # contract_date_end_month = self.employee_id.contract_id.date_end.strftime('%Y-%m')
        while contract_date_start_month <= end_period.strftime('%Y-%m'):
            if self.employee_id.contract_id.date_end and self.employee_id.contract_id.date_end.strftime(
                    '%Y-%m') < end_period.strftime('%Y-%m'):
                return 0
            if self.get_number_of_days_to_be_allocated(self.employee_id, end_period) is False:
                if not self.employee_id.working_in_south_area:
                    print(self.employee_id, added_value * period_prorata)
                    # raise(_(added_value))
                    return added_value * period_prorata
                else:
                    return level.smartest_added_value_south * period_prorata
            else:
                print(self.employee_id, self.get_number_of_days_to_be_allocated(self.employee_id, end_period))
                return self.get_number_of_days_to_be_allocated(self.employee_id, end_date)
        return 0

    def _process_accrual_plans(self):
        """
        This method is part of the cron's process.
        The goal of this method is to retroactively apply accrual plan levels and progress from nextcall to today
        """
        today = fields.Date.today()
        first_allocation = _(
            """This allocation have already ran once, any modification won't be effective to the days allocated to the employee. If you need to change the configuration of the allocation, cancel and create a new one.""")
        for allocation in self:
            level_ids = allocation.accrual_plan_id.level_ids.sorted('sequence')
            if not level_ids:
                continue
            if not allocation.nextcall:
                first_level = level_ids[0]
                first_level_start_date = allocation.date_from + get_timedelta(first_level.start_count,
                                                                              first_level.start_type)
                if today < first_level_start_date:
                    # Accrual plan is not configured properly or has not started
                    continue
                allocation.lastcall = max(allocation.lastcall, first_level_start_date)
                allocation.nextcall = first_level._get_next_date(allocation.lastcall) - relativedelta(days=1)

                if len(level_ids) > 1:
                    second_level_start_date = allocation.date_from + get_timedelta(level_ids[1].start_count,
                                                                                   level_ids[1].start_type)
                    allocation.nextcall = min(second_level_start_date - relativedelta(days=1), allocation.nextcall)
                allocation._message_log(body=first_allocation)
            days_added_per_level = defaultdict(lambda: 0)
            while allocation.nextcall <= today:
                (current_level, current_level_idx) = allocation._get_current_accrual_plan_level_id(allocation.nextcall)
                nextcall = current_level._get_next_date(allocation.nextcall)
                # Since _get_previous_date returns the given date if it corresponds to a call date
                # this will always return lastcall except possibly on the first call
                # this is used to prorate the first number of days given to the employee
                period_start = current_level._get_previous_date(allocation.lastcall)
                period_end = current_level._get_next_date(allocation.lastcall)
                # If accruals are lost at the beginning of year, skip accrual until beginning of this year
                if current_level.action_with_unused_accruals == 'lost':
                    this_year_first_day = today + relativedelta(day=1, month=1)
                    if period_end < this_year_first_day:
                        allocation.lastcall = allocation.nextcall
                        allocation.nextcall = nextcall
                        continue
                    else:
                        period_start = max(period_start, this_year_first_day)
                # Also prorate this accrual in the event that we are passing from one level to another
                if current_level_idx < (
                        len(level_ids) - 1) and allocation.accrual_plan_id.transition_mode == 'immediately':
                    next_level = level_ids[current_level_idx + 1]
                    current_level_last_date = allocation.date_from + get_timedelta(next_level.start_count,
                                                                                   next_level.start_type) - relativedelta(
                        days=1)
                    if allocation.nextcall != current_level_last_date:
                        nextcall = min(nextcall, current_level_last_date)
                days_added_in_july = allocation._process_accrual_plan_level(
                    current_level, period_start, allocation.lastcall, period_end, allocation.nextcall)
                days_added_per_level[current_level] += allocation._process_accrual_plan_level(
                    current_level, period_start, allocation.lastcall, period_end, allocation.nextcall)
                print(period_start, period_end, allocation.lastcall, allocation.nextcall, allocation.employee_id)
                allocation.lastcall = allocation.nextcall
                allocation.nextcall = nextcall

            number_of_days_added_in_july = 0

            if days_added_per_level:
                if allocation.worked_days_in_july(allocation.employee_id, days_added_in_july):
                    number_of_days_added_in_july = allocation.worked_days_in_july(allocation.employee_id,
                                                                                  days_added_in_july)
                if not allocation.employee_id.working_in_south_area:
                    number_of_days_to_add = allocation.number_of_days + sum(
                        days_added_per_level.values()) + number_of_days_added_in_july
                    # Let's assume the limit of the last level is the correct one
                    allocation.number_of_days = min(number_of_days_to_add,
                                                    current_level.maximum_leave + allocation.leaves_taken) if current_level.maximum_leave > 0 else number_of_days_to_add
                else:
                    number_of_days_to_add = allocation.number_of_days + sum(
                        days_added_per_level.values()) + number_of_days_added_in_july
                    print(number_of_days_to_add)
                    # Let's assume the limit of the last level is the correct one
                    allocation.number_of_days = min(number_of_days_to_add,
                                                    current_level.smartest_maximum_leave_south + allocation.leaves_taken) if current_level.smartest_maximum_leave_south > 0 else number_of_days_to_add

    def _action_validate_create_childs(self):
        # TODO: Do not erase this function. Find a way to do a good override
        childs = self.env['hr.leave.allocation']
        # In the case we are in holiday_type `employee` and there is only one employee we can keep the same allocation
        # Otherwise we do need to create an allocation for all employees to have a behaviour that is in line
        # with the other holiday_type
        if self.state == 'validate' and (self.holiday_type in ['category', 'department', 'company'] or
                                         (self.holiday_type == 'employee' and len(self.employee_ids) > 1)):
            if self.holiday_type == 'employee':
                employees = self.employee_ids
            elif self.holiday_type == 'category':
                employees = self.category_id.employee_ids
            elif self.holiday_type == 'department':
                employees = self.department_id.member_ids
            else:
                employees = self.env['hr.employee'].search([('company_id', '=', self.mode_company_id.id)])

            # Added by SMARTEST
            employees = employees.filtered(lambda p: p.contract_id.state == 'open' and p.attribution_auto_leave == True)

            allocation_create_vals = self._prepare_holiday_values(employees)
            childs += self.with_context(
                mail_notify_force_send=False,
                mail_activity_automation_skip=True
            ).create(allocation_create_vals)
            if childs:
                childs.action_validate()
        return childs

    # ----------------------------------------------------------------
    # Helpers methods
    # ----------------------------------------------------------------
    @api.model
    def _get_employee_allocation_domain(self, employee, start_date):
        employee_domain = [('holiday_type', '=', 'employee'), ('employee_ids', 'in', employee.id)]
        company_domain = [('holiday_type', '=', 'company'), ('mode_company_id', '=', employee.company_id.id)]
        department_domain = [('holiday_type', '=', 'department'), ('department_id', '=', employee.department_id.id)]
        category_domain = [('holiday_type', '=', 'category'), ('category_id', 'in', employee.category_ids.ids)]
        or_domain = expression.OR([
            employee_domain,
            company_domain,
            department_domain,
            category_domain,
        ])
        date_domain = expression.OR([
            [('date_from', '<=', start_date), ('date_to', '>=', start_date)],
            [('date_from', '<=', start_date), ('date_to', '=', False)]
        ])
        return expression.AND([
            date_domain,
            or_domain
        ])

    @api.model
    def _get_employee_allocation(self, employee, start_date):
        if not employee:
            return self.env['hr.leave.allocation']
        domain = self._get_employee_allocation_domain(employee, start_date)

        return self.search(domain, order='date_from asc', limit=1)



    # ------------------------------------------------------------------------------------------
    # ------------------METHODE CLOTURE DE CONGÉ -----------------------------------------------
    # -----------------------------------------------------------------------------------------

    # ________________________pour chaque employee___________________________________________________
    # #-- creation allocation congé payé similaire a congé anticipé dans le cas accrual
    # #------ modifier tout les congés anticipé de cet comployee en congé payé
    # ---- refuser annuler supprimer allocation anticipé de chaque employee
    # ---- -------------- create une allocation anticipé de lannée courante de type company pour tout les employee----------------

    def cron_cloture_method(self):
        anticip = self.env.ref('smartest_hr_holidays.holiday_status_anticip').id
        paid = self.env.ref('hr_holidays.holiday_status_cl').id
        allocation_obj = self.env['hr.leave.allocation']
        employee_ids = self.env['hr.employee'].search(
            [('attribution_auto_leave', '=', True), ('contract_id.state', '=', 'open')])
        allocation_anticip_ids = allocation_obj.search(
            [('holiday_status_id', '=', anticip), ('holiday_type', '=', 'company'),
             ('allocation_type', '=', 'accrual'),
             ('state', '=', 'validate')])

#________________________pour chaque employee___________________________________________________
        for employee in employee_ids:
            allocation = allocation_obj.search(
                [('employee_id', '=', employee.id), ('holiday_status_id', '=', anticip),
                 ('holiday_type', '=', 'employee'), ('allocation_type', '=', 'accrual'),
                 ('state', '=', 'validate')])
            allocation_regular_accrual = allocation_obj.search(
                [('employee_id', '=', employee.id), ('holiday_status_id', '=', anticip),
                 ('holiday_type', '=', 'employee'),
                 ('state', '=', 'validate')])
            leave_ids = self.env['hr.leave'].search(
                [('employee_id', '=', employee.id), ('holiday_status_id', '=', anticip),
                 ('state', '=', 'validate')])
            allocations = []
            allocations.append({
                'name': _("Leaves cumulation of the period: %s - %s for %s") % (
                allocation.date_from, allocation.date_to, employee.name),
                'holiday_status_id': paid,
                'allocation_type': 'regular',
                'date_from': allocation.date_from,
                'date_to': False,
                'number_of_days': float(allocation.number_of_days),
                'number_of_days_display': float(allocation.number_of_days),
                'holiday_type': 'employee',
                'employee_id': employee.id,
                'department_id': employee.department_id.id,
                'state': 'draft',
            })
#-------------- create allocation de l'employee de type congé payé la copie de anticipé
            if allocations:
                allocation_ids = allocation_obj.sudo().create(allocations)
                # allocation_ids.sudo().action_draft()
                allocation_ids.sudo().action_confirm()
                allocation_ids.sudo().filtered(lambda alloc: alloc.state == 'confirm').action_validate()
#-------------- modify leave de employee de congé anticipé a payé
            for leave in leave_ids:
                leave.employee_id.name
                leave.sudo().action_refuse()
                leave.sudo().action_draft()
                leave.write({'holiday_status_id': paid})
                leave._compute_from_holiday_status_id()
                leave.sudo().filtered(lambda alloc: alloc.state == 'draft').action_confirm()
                leave.sudo().filtered(lambda alloc: alloc.state == 'confirm').action_approve()
                leave.sudo().filtered(lambda alloc: alloc.state == 'validate1').action_validate()
#-------------------suppression de l'ancienne allocation
            for alloc in allocation_regular_accrual:
                alloc.action_refuse()
                alloc.action_draft()
                alloc.unlink()
#------------- creer la grande allocation de l'année courante
        allocation_anticip_ids.action_refuse()
        allocation_anticip_ids.action_draft()
        new_date_from = allocation_anticip_ids.date_from + relativedelta(years=1)
        new_date_to = allocation_anticip_ids.date_to + relativedelta(years=1)
        allocation_anticip_ids.write({'date_from': new_date_from, 'date_to': new_date_to})
        allocation_anticip_ids.sudo().filtered(lambda alloc: alloc.state == 'draft').action_confirm()
        allocation_anticip_ids.sudo().filtered(lambda alloc: alloc.state == 'confirm').action_validate()

    @api.depends('employee_id', 'holiday_status_id', 'taken_leave_ids.number_of_days', 'taken_leave_ids.state')
    def _compute_leaves(self):
        for allocation in self:
            allocation.max_leaves = allocation.number_of_hours_display if allocation.type_request_unit == 'hour' else allocation.number_of_days
            allocation.leaves_taken = sum(taken_leave.number_of_hours_display if taken_leave.leave_type_request_unit == 'hour' else taken_leave.number_of_days\
                for taken_leave in allocation.taken_leave_ids\
                if taken_leave.state in ('validate'))
