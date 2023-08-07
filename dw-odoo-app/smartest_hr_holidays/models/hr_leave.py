# -*- coding:utf-8 -*-
import base64
from collections import defaultdict
from datetime import datetime
from datetime import date, timedelta
from odoo.tools.float_utils import float_compare

from dateutil.relativedelta import relativedelta
from pytz import timezone, UTC

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


WEEK_NUM = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6,
}
NUM_WEEK = {
    str(0): "Monday",
    str(1): "Tuesday",
    str(2): "Wednesday",
    str(3): "Thursday",
    str(4): "Friday",
    str(5): "Saturday",
    str(6): "Sunday",
}


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    state = fields.Selection(selection_add=[
        ('suspend', 'Suspended'),
        ('stop', 'Stopped'),
        ('prolonged', 'Prolonged'),
        ('done', 'Confirmé par reponsable'),
    ])
    smartest_hide_child_leave = fields.Boolean(default=False)
    smartest_test_stop = fields.Boolean(
        compute='_compute_smartest_test_stop',
    )
    smartest_request_check_stop = fields.Boolean(
        compute='_compute_smartest_request_check_stop',
    )
    smartest_check_edit = fields.Boolean(
        compute='_compute_smartest_check_edit',
    )
    smartest_test_suspend = fields.Boolean(
        compute='_compute_smartest_test_suspend',
    )
    smartest_request_check_suspend = fields.Boolean(
        compute='_compute_smartest_request_check_suspend',
    )
    smartest_cancellation_reason = fields.Char(
        string="Cancellation reason",
        index=True,
        tracking=True,
        store=True
    )
    smartest_motif = fields.Char(
        string="Reason",
        index=True,
        tracking=True,
        store=True
    )
    smartest_request_motif = fields.Char(
        string="Reason",
        index=True,
        tracking=True,
        store=True
    )
    smartest_alert_duration_holiday = fields.Boolean(
        string="field to respect the duration of leave selected"
    )
    smartest_duration_of_request_leave = fields.Integer(
        related="holiday_status_id.smartest_duration_of_leave"
    )
    smartest_is_mariage = fields.Boolean(
        related="holiday_status_id.smartest_is_mariage"
    )

    smartest_is_death = fields.Boolean(
        related="holiday_status_id.smartest_is_death"
    )
    smartest_is_exceptional_death = fields.Boolean(
        related="holiday_status_id.smartest_is_exceptional_death"
    )
    date_prolonged_suspended = fields.Date(
        string="New date-to"
    )
    request_date_prolonged_suspended = fields.Date(
        string="New date-to"
    )
    smartest_type_of_operation = fields.Selection([
        ('prolong', 'Prolong'),
        ('suspend', 'Suspend'),
    ],
        default='suspend',
        string="Suspend/Prolong"
    )
    smartest_request_type_of_operation = fields.Selection([
        ('prolong', 'Prolong'),
        ('suspend', 'Suspend'),
    ],
        default='suspend',
        string="Suspend/Prolong"
    )
    smartest_parent_id = fields.Many2one(
        comodel_name='hr.leave',
        string="Parent"
    )
    smartest_date_start = fields.Date(
        string='Date start'
    )
    smartest_mariage_of = fields.Selection(
        [('employee', 'Employee'),
         ('descendant', 'Direct descendants (Son or Daughter)')
         ],
        string="wedding of")

    smartest_death_of = fields.Selection([
        ('ascendants', 'Ascendants (father and mother)'),
        ('descendants', 'Descendants (sons and daughters)'),
        ('collateral',
         'Direct collateral (brothers and sisters) and their spouses (spouses of brothers, spouses of sisters)'),
    ], string="The Death of")

    smartest_death_exceptional_of = fields.Selection([
        ('collatéraux', 'Death of first degree direct collaterals (uncles and aunts).'),
    ], string="The Death of")

    smartest_next_leave = fields.Many2one(
        'hr.leave',
        string="Next (suite) ",
    )
    smartest_precedent_leave = fields.Many2one(
        'hr.leave',
        string="Precedent ",
    )
    smartest_parent_id_allocation = fields.Many2one(
        comodel_name='hr.leave'
    )
    smartest_child_ids_allocation = fields.One2many(
        comodel_name='hr.leave',
        inverse_name='smartest_parent_id_allocation'
    )
    smartest_check_corrspondant_sociale = fields.Boolean(
        compute="_compute_smartest_check_corrspondant_sociale"
    )
    smartest_interim_id = fields.Many2one('hr.employee',string="interim worker")

    @api.constrains('date_prolonged_suspended', 'date_to', 'request_date_to')
    def _check_type_of_operation(self):
        if self.date_prolonged_suspended and self.date_to and self.request_date_to and self.date_prolonged_suspended > self.request_date_to and self.smartest_type_of_operation == "suspend":
            raise ValidationError(
                _('A contradiction has been deduced !! the date chosen does not match to the type of operation selected,\n'
                  'When the new date-to is greater than the date-to of leave the type of operation becomes Prolong.')
            )
        elif self.date_prolonged_suspended and self.date_to and self.request_date_to and self.date_prolonged_suspended < self.request_date_to and self.smartest_type_of_operation == "prolong":
            raise ValidationError(
                _('A contradiction has been deduced !! the date chosen does not match to the type of operation selected,\n'
                  'When the new date-to is less than the date-to of leave the type of operation becomes Suspend.')
            )

    @api.constrains('date_from', 'date_to', 'employee_id')
    def _check_date(self):
        context = self.env.context
        if context.get('smartest_bypass_check_date') or context.get('leave_skip_date_check', False):
            return True
        for holiday in self.filtered('employee_id'):
            domain = [
                ('date_from', '<', holiday.date_to),
                ('date_to', '>', holiday.date_from),
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
                ('state', 'not in', ['cancel', 'refuse', 'done', 'suspend', 'prolong', 'stop']),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(
                    _('You can not set 2 time off that overlaps on the same day for the same employee.') + '\n- %s' % (holiday.display_name))

    @api.constrains('state', 'number_of_days', 'holiday_status_id')
    def _check_holidays(self):
        for holiday in self:
            if holiday.holiday_type != 'employee' or not holiday.employee_id or not holiday.holiday_status_id or holiday.holiday_status_id.requires_allocation == 'no':
                continue
            # FIXME: Here we commented Odoo constrains to allow leaves from different allocations periods
            # mapped_days = holiday.holiday_status_id.get_employees_days([holiday.employee_id.id], holiday.date_from)
            # leave_days = mapped_days[holiday.employee_id.id][holiday.holiday_status_id.id]
            # if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1 and not holiday.holiday_status_id.smartest_cumulative_leave:
            #     raise ValidationError(_('The number of remaining time off is not sufficient for this time off type.\n'
            #                             'Please also check the time off waiting for validation.') + '\n- %s' % holiday.display_name)

    @api.constrains('number_of_days')
    def _check_number_of_days(self):
        for leave in self:
            if leave.holiday_status_id.requires_allocation == 'no' \
                    and leave.smartest_duration_of_request_leave > 0 \
                    and leave.number_of_days != leave.smartest_duration_of_request_leave:
                raise ValidationError(
                    _('You can not ask for more or less than %s days for "%s" leave type.') % (
                        leave.smartest_duration_of_request_leave,
                        leave.holiday_status_id.name
                    )
                )

    @api.constrains('request_date_from', 'date_from', 'employee_id')
    def _check_date_from_days_permission(self):
        today = fields.Date.today()
        for leave in self:
            delay = leave.holiday_status_id.smartest_holidays_request_delay
            if delay > 0 and leave.holiday_type == 'employee' and leave.employee_id.anticipated_request \
                    and (leave.request_date_from - today).days < delay:
                raise ValidationError(
                    _('Holidays must be requested before %s days of the holiday start date.') % delay
                )

    @api.constrains('holiday_allocation_id')
    def _check_allocation_id(self):
        to_check = self.filtered(lambda l: not l.holiday_status_id.smartest_cumulative_leave)
        res = super(HrLeave, to_check)._check_allocation_id()
        for leave in self:
            if not leave.smartest_hide_child_leave and leave.holiday_type == 'employee' and not leave.multi_employee and \
                    leave.holiday_status_id.requires_allocation == 'yes' and leave.holiday_status_id.smartest_cumulative_leave and leave.state != 'done':
                days_available = 0
                for allocation in leave.get_allocation_ids(leave.employee_id.id, leave.holiday_status_id.id):
                    days_available += (allocation.max_leaves - allocation.leaves_taken)

                if days_available < leave.number_of_days:
                    raise ValidationError(
                        _(
                            'Could not find an allocation of type %(leave_type)s for the requested time period.',
                            leave_type=leave.holiday_status_id.display_name,
                    ) + '\n- %s' % (leave.employee_id.name))
        return res

    @api.constrains('holiday_status_id', 'number_of_days')
    def _check_allocation_duration(self):
        to_check = self.filtered(lambda l: not l.holiday_status_id.smartest_cumulative_leave)
        return super(HrLeave, to_check)._check_allocation_duration()

    @api.depends('date_from', 'request_date_from')
    def _compute_smartest_test_stop(self):
        current_time = fields.Datetime.now()
        current_date = fields.Date.context_today(self)
        is_holidays_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
        is_holidays_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        for leave in self:
            if leave.state in (['validate','done']) and self.env.user == leave.employee_id.leave_manager_id or is_holidays_manager or is_holidays_officer:
                if leave.request_date_from:
                    leave.smartest_test_stop = current_date < leave.request_date_from and leave.holiday_status_id.smartest_allow_cancellation
                elif leave.date_from:
                    leave.smartest_test_stop = current_time < leave.date_from and leave.holiday_status_id.smartest_allow_cancellation
                else:
                    leave.smartest_test_stop = False
            else:
                leave.smartest_test_stop = False
    @api.depends('date_from', 'request_date_from')
    def _compute_smartest_request_check_stop(self):
        current_time = fields.Datetime.now()
        current_date = fields.Date.context_today(self)
        for leave in self:
            if leave.state in (['validate','done']) and self.env.user == leave.employee_id.user_id:
                date_from = leave.date_from - timedelta(days=2)
                request_date_from = leave.request_date_from - timedelta(days=2)
                if leave.request_date_from:
                    leave.smartest_request_check_stop = current_date <= request_date_from and leave.holiday_status_id.smartest_allow_cancellation
                elif leave.date_from:
                    leave.smartest_request_check_stop = current_time <= date_from and leave.holiday_status_id.smartest_allow_cancellation
                else:
                    leave.smartest_request_check_stop = False
            else:
                leave.smartest_request_check_stop = False

    @api.depends('date_from', 'request_date_from')
    def _compute_smartest_check_edit(self):
        current_time = fields.Datetime.now()
        current_date = fields.Date.context_today(self)
        is_holidays_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
        is_holidays_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        for leave in self:
            if leave.state in (['validate','done']) and self.env.user == leave.employee_id.leave_manager_id or is_holidays_manager or is_holidays_officer:
                if leave.date_from:
                    leave.smartest_check_edit = current_time < leave.date_from and leave.holiday_status_id.smartest_allow_editing
                elif leave.request_date_from:
                    leave.smartest_check_edit = current_date < leave.request_date_from and leave.holiday_status_id.smartest_allow_editing
                else:
                    leave.smartest_check_edit = False
            else:
                leave.smartest_check_edit = False

    @api.depends('date_from', 'request_date_from', 'state')
    def _compute_smartest_test_suspend(self):
        current_time = fields.Datetime.now()
        current_date = fields.Date.context_today(self)
        is_holidays_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        for leave in self:
            if leave.state in ('validate', 'done') and leave.holiday_status_id.smartest_allow_prolong_suspend and (self.env.user == leave.employee_id.leave_manager_id  or is_holidays_officer):
                if leave.date_from and leave.date_to:
                    leave.smartest_test_suspend = leave.date_from <= current_time <= leave.date_to
                elif leave.request_date_from and leave.request_date_to:
                    leave.smartest_test_suspend = leave.request_date_from <= current_date <= leave.request_date_to
                else:
                    leave.smartest_test_suspend = False
            else:
                leave.smartest_test_suspend = False
    @api.depends('date_from', 'request_date_from', 'state')
    def _compute_smartest_request_check_suspend(self):
        current_time = fields.Datetime.now()
        current_date = fields.Date.context_today(self)
        for leave in self:
            if leave.state in ('validate', 'done') and self.env.user == leave.employee_id.user_id:
                if leave.date_from and leave.date_to:
                    leave.smartest_request_check_suspend = leave.date_from <= current_time <= leave.date_to
                elif leave.request_date_from and leave.request_date_to:
                    leave.smartest_request_check_suspend = leave.request_date_from <= current_date <= leave.request_date_to
                else:
                    leave.smartest_request_check_suspend = False
            else:
                leave.smartest_request_check_suspend = False
    @api.depends('date_from', 'request_date_from', 'state','holiday_status_id')
    def _compute_smartest_check_corrspondant_sociale(self):
        is_holidays_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        is_group_correspondant_social = self.env.user.has_group('smartest_hr_holidays.hr_leave_rule_responsible_unpaid_leave_update')
        for leave in self:
            if leave.holiday_status_id.smartest_type_leave_access_to_crud ==True and is_group_correspondant_social :
                leave.smartest_check_corrspondant_sociale = True
            else:
                leave.smartest_check_corrspondant_sociale = False

    @api.onchange('holiday_status_id')
    def _onchange_holiday_status_id(self):
        self.smartest_alert_duration_holiday = self.holiday_status_id.requires_allocation == "no" \
                                               and self.smartest_duration_of_request_leave > 0 \
                                               and self.number_of_days != self.smartest_duration_of_request_leave

    def action_stop(self):
        current_employee = self.env.user.employee_id
        if any(holiday.state not in ['draft', 'confirm', 'validate', 'validate1'] for holiday in self):
            raise UserError(_('Time off request must be confirmed or validated in order to cancel it.'))

        validated_holidays = self.filtered(lambda hol: hol.state == 'validate1')
        validated_holidays.write({'state': 'stop', 'first_approver_id': current_employee.id})
        (self - validated_holidays).write({'state': 'stop', 'second_approver_id': current_employee.id})
        # Delete the meeting
        self.mapped('meeting_id').write({'active': False})
        # If a category that created several holidays, cancel all related
        linked_requests = self.mapped('linked_request_ids')
        if linked_requests:
            linked_requests.action_stop()

        # Post a second message, more verbose than the tracking message
        for holiday in self:
            if holiday.employee_id.user_id:
                holiday.message_post(
                    body=_('Your %(leave_type)s planned on %(date)s has been canceled',
                           leave_type=holiday.holiday_status_id.display_name, date=holiday.date_from),
                    partner_ids=holiday.employee_id.user_id.partner_id.ids)
        self._remove_resource_leave()
        self.activity_update()
        # work_entries = self.env['hr.work.entry'].sudo().search([('leave_id', 'in', self.ids)])
        # work_entries.write({'active': False})
        # # Re-create attendance work entries
        # vals_list = []
        # for work_entry in work_entries:
        #     vals_list += work_entry.contract_id._get_work_entries_values(work_entry.date_start, work_entry.date_stop)
        # self.env['hr.work.entry'].create(vals_list)
        return True

    def button_stop(self):
        compose_form = self.env.ref('smartest_hr_holidays.hr_leave_form_view', False)
        if compose_form:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Motifs d"annulation',
                'res_model': 'hr.leave',
                'res_id': self.id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'view_id': compose_form.id,
            }

    def button_request_stop(self):
        self.ensure_one()
        mail_template_leave = self.env.ref('smartest_hr_holidays.request_cancellation_email_template',
                                           raise_if_not_found=False)
        if mail_template_leave:
            mail_template_leave.sudo().send_mail(self.id)


    def _process_suspend_prolong(self):
        if self.smartest_type_of_operation == "suspend":
            current_employee = self.env.user.employee_id
            if any(holiday.state not in ['draft', 'confirm', 'validate', 'validate1','done'] for holiday in self):
                raise UserError(_('Time off request must be confirmed or validated in order to suspend it.'))

            validated_holidays = self.filtered(lambda hol: hol.state == 'validate1')
            validated_holidays.write({'state': 'suspend', 'first_approver_id': current_employee.id})
            (self - validated_holidays).write({'state': 'suspend', 'second_approver_id': current_employee.id})
            # Delete the meeting
            self.mapped('meeting_id').write({'active': False})
            # If a category that created several holidays, cancel all related
            linked_requests = self.mapped('linked_request_ids')
            if linked_requests:
                linked_requests.action_stop()

            # Post a second message, more verbose than the tracking message
            for holiday in self:
                if holiday.employee_id.user_id:
                    holiday.message_post(
                        body=_('Your %(leave_type)s planned on %(date)s has been suspended',
                               leave_type=holiday.holiday_status_id.display_name, date=holiday.date_from),
                        partner_ids=holiday.employee_id.user_id.partner_id.ids)
        elif self.smartest_type_of_operation == "prolong":
            current_employee = self.env.user.employee_id
            if any(holiday.state not in ['draft', 'confirm', 'validate', 'validate1','done'] for holiday in self):
                raise UserError(_('Time off request must be confirmed or validated in order to prolong it.'))

            validated_holidays = self.filtered(lambda hol: hol.state == 'validate1')
            validated_holidays.write({'state': 'prolonged', 'first_approver_id': current_employee.id})
            (self - validated_holidays).write({'state': 'prolonged', 'second_approver_id': current_employee.id})
            # Delete the meeting
            self.mapped('meeting_id').write({'active': False})
            # If a category that created several holidays, cancel all related
            linked_requests = self.mapped('linked_request_ids')
            if linked_requests:
                linked_requests.action_stop()

            # Post a second message, more verbose than the tracking message
            for holiday in self:
                if holiday.employee_id.user_id:
                    holiday.message_post(
                        body=_('Your %(leave_type)s planned on %(date)s has been prolonged',
                               leave_type=holiday.holiday_status_id.display_name, date=holiday.date_from),
                        partner_ids=holiday.employee_id.user_id.partner_id.ids)
        self._remove_resource_leave()
        self.activity_update()
        # work_entries = self.env['hr.work.entry'].sudo().search([('leave_id', 'in', self.ids)])
        # work_entries.write({'active': False})
        # # Re-create attendance work entries
        # vals_list = []
        # for work_entry in work_entries:
        #     vals_list += work_entry.contract_id._get_work_entries_values(work_entry.date_start, work_entry.date_stop)
        # self.env['hr.work.entry'].create(vals_list)
        return True

    @api.ondelete(at_uninstall=False)
    def _unlink_if_correct_states(self):
        error_message = _('You cannot delete a time off which is in %s state')
        state_description_values = {elem[0]: elem[1] for elem in self._fields['state']._description_selection(self.env)}
        now = fields.Datetime.now()

        if not self.user_has_groups('hr_holidays.group_hr_holidays_user'):
            if any(hol.state not in ['draft', 'confirm', 'suspend', 'prolonged', 'stop'] for hol in self):
                raise UserError(error_message % state_description_values.get(self[:1].state))
            if any(hol.date_from < now for hol in self):
                raise UserError(_('You cannot delete a time off which is in the past'))
        else:
            for holiday in self.filtered(
                    lambda holiday: holiday.state not in ['draft', 'cancel', 'confirm', 'suspend', 'prolonged','done',
                                                          'stop']):
                raise UserError(error_message % (state_description_values.get(holiday.state),))

    def create_susp_prolong_leave(self):
        HrLeave = self.env['hr.leave']
        if self.smartest_hide_child_leave:
            self.date_prolonged_suspended = self.smartest_parent_id_allocation.date_prolonged_suspended
        if self.request_date_from < self.date_prolonged_suspended:
            create_vals = {
                'holiday_status_id': self.holiday_status_id.id,
                'request_date_from': self.request_date_from,
                'date_from': self.date_from,
                'request_date_to': self.date_prolonged_suspended,
                'number_of_days': abs((self.date_from.date() - self.date_prolonged_suspended).days) + 1,
                'date_to': datetime.strptime(str(self.date_prolonged_suspended) + " 16:00:00", "%Y-%m-%d %H:%M:%S"),
                'holiday_type': 'employee',
                'employee_id': self.employee_id.id,
                'department_id': self.department_id.id,
                'state': 'draft',
                'smartest_parent_id': self.id,
                'smartest_motif': self.smartest_motif,
            }
            leave = HrLeave.with_context(pass_holiday_status_constraint=True, smartest_bypass_check_date=True).create(
                create_vals)
            leave.sudo().with_context(smartest_bypass_check_date=True).action_draft()
            leave.sudo().action_confirm()
            leave.sudo().filtered(lambda alloc: alloc.state == 'confirm').action_approve()
            leave.sudo().filtered(lambda alloc: alloc.state == 'validate1').action_validate()
            leave.sudo().filtered(lambda alloc: alloc.state == 'confirm').action_approve()
            return leave
        return self.env['hr.leave']

    def action_draft(self):
        if any(holiday.state not in ['confirm', 'refuse','done'] for holiday in self) and not self.env.context.get(
                'smartest_bypass_check_date'):
            raise UserError(
                _('Time off request state must be "Refused" or "To Approve" in order to be reset to draft.'))
        self.write({
            'state': 'draft',
            'first_approver_id': False,
            'second_approver_id': False,
        })
        linked_requests = self.mapped('linked_request_ids')
        if linked_requests:
            linked_requests.action_draft()
            linked_requests.unlink()
        self.activity_update()
        return True

    def action_suspend_prolong(self):
        self.ensure_one()
        compose_form = self.env.ref('smartest_hr_holidays.hr_leave_form_view_suspension', False)
        if compose_form:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Holidays suspend/prolong reason'),
                'res_model': 'hr.leave',
                'res_id': self.id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'view_id': compose_form.id,
                # 'flags': {'form': {'button_method': True}}
            }
    def action_request_suspend_prolong(self):
        self.ensure_one()
        compose_form = self.env.ref('smartest_hr_holidays.hr_leave_form_view_request_suspension', False)
        if compose_form:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Holidays request suspend/prolong'),
                'res_model': 'hr.leave',
                'res_id': self.id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'view_id': compose_form.id,
                # 'flags': {'form': {'button_method': True}}
            }

    def button_request_suspend_prolong(self):
        self.ensure_one()
        mail_template_leave = self.env.ref('smartest_hr_holidays.request_suspend_prolong_email_template',
                                           raise_if_not_found=False)
        if mail_template_leave:
            mail_template_leave.sudo().send_mail(self.id)
    def button_suspend_prolong_approve(self):
        self.ensure_one()
        if not self.smartest_test_suspend:
            raise ValidationError(
                _('You can not suspend / prolong this holidays.')
            )
        if not self.smartest_hide_child_leave and not self.smartest_child_ids_allocation:
            self._process_suspend_prolong()
            if self.date_prolonged_suspended:
                leave = self.create_susp_prolong_leave()
                if leave:
                    return {
                        'type': 'ir.actions.act_window',
                        'name': leave.name,
                        'res_model': 'hr.leave',
                        'view_mode': 'form',
                        'res_id': leave.id,
                        'view_id': self.env.ref('hr_holidays.hr_leave_view_form_manager').id,
                    }
        elif not self.smartest_hide_child_leave and self.smartest_child_ids_allocation:
            if self.smartest_type_of_operation == "suspend":
                child_sus = self.smartest_child_ids_allocation
                for child in child_sus:
                    child.action_refuse()
                    child.action_draft()
                    child.unlink()

                self._process_suspend_prolong()
                leave = self.create_susp_prolong_leave()
                if leave:
                    return {
                        'type': 'ir.actions.act_window',
                        'name': leave.name,
                        'res_model': 'hr.leave',
                        'view_mode': 'form',
                        'res_id': leave.id,
                        'view_id': self.env.ref('hr_holidays.hr_leave_view_form_manager').id,
                    }
            else:
                if self.smartest_type_of_operation == "prolong":

                    child_sus = self.smartest_child_ids_allocation
                    for child in child_sus:
                        child.action_refuse()
                        child.action_draft()
                        child.unlink()

                    self._process_suspend_prolong()
                    leave = self.create_susp_prolong_leave()
                    if leave:
                        return {
                            'type': 'ir.actions.act_window',
                            'name': leave.name,
                            'res_model': 'hr.leave',
                            'view_mode': 'form',
                            'res_id': leave.id,
                            'view_id': self.env.ref('hr_holidays.hr_leave_view_form_manager').id,
                        }

    def action_refuse(self):
        current_employee = self.env.user.employee_id
        if any(holiday.state not in ['draft', 'confirm', 'validate', 'validate1','done'] for holiday in self):
            raise UserError(_('Time off request must be confirmed or validated in order to refuse it.'))

        validated_holidays = self.filtered(lambda hol: hol.state == 'validate1')
        validated_holidays.write({'state': 'refuse', 'first_approver_id': current_employee.id})
        (self - validated_holidays).write({'state': 'refuse', 'second_approver_id': current_employee.id})
        # Delete the meeting
        self.mapped('meeting_id').write({'active': False})
        # If a category that created several holidays, cancel all related
        linked_requests = self.mapped('linked_request_ids')
        if linked_requests:
            linked_requests.action_refuse()

        # Post a second message, more verbose than the tracking message
        for holiday in self:
            if holiday.employee_id.user_id:
                holiday.message_post(
                    body=_('Your %(leave_type)s planned on %(date)s has been refused', leave_type=holiday.holiday_status_id.display_name, date=holiday.date_from),
                    partner_ids=holiday.employee_id.user_id.partner_id.ids)
        self.activity_update()
        if self.smartest_child_ids_allocation:
            for child in self.smartest_child_ids_allocation:
                child.action_refuse()
                child.action_draft()
                child.unlink()
        return True
    def button_stop_approve(self):
        self.ensure_one()
        if not self.smartest_test_stop:
            raise ValidationError(
                _('You can not stop this holidays.')
            )
        if not self.smartest_hide_child_leave and not self.smartest_child_ids_allocation:
            self.action_stop()
        elif not self.smartest_hide_child_leave and self.smartest_child_ids_allocation:
            for child in self.smartest_child_ids_allocation:
                child.action_stop()
                self.state = 'stop'

    def button_editer(self):
        self.ensure_one()
        if not self.smartest_hide_child_leave and not self.smartest_child_ids_allocation:
            self.action_refuse()
            self.action_draft()
        elif not self.smartest_hide_child_leave and self.smartest_child_ids_allocation:
            for child in self.smartest_child_ids_allocation:
                child.action_refuse()
                child.action_draft()
                child.unlink()
            self.action_draft()

    def alldays(self, year, whichDayYouWant):
        d = date(year, 1, 1)
        d += timedelta(days=(WEEK_NUM[whichDayYouWant] - d.weekday()) % 7)
        while d.year == year:
            yield d
            d += timedelta(days=7)

    def extract_weekend_between_date_from_to(self, day_one):
        date = []
        if self.request_date_from:
            for d in self.alldays(datetime.strptime(str(self.request_date_from), "%Y-%m-%d").year, day_one):
                if not self.smartest_hide_child_leave:
                    if d >= self.request_date_from and d <= self.request_date_to:
                        date.append(d)
                    # elif d == self.request_date_from and not self.holiday_status_id.smartest_cumulative_leave:
                    #     raise ValidationError(
                    #         _('A LEAVE CANNOT START ON A WEEKEND.')
                    #     )
                    # elif d == self.request_date_to and not self.holiday_status_id.smartest_cumulative_leave:
                    #     raise ValidationError(
                    #         _('A LEAVE CANNOT BE FINISHED ON A WEEKEND.')

                else:
                    if d >= self.request_date_from and d <= self.request_date_to:
                        date.append(d)
            return date
        return False

    def date_range(self,start, end):
        delta = end - start
        days = [start + timedelta(days=i) for i in range(delta.days + 1)]
        return days

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_number_of_days(self):
        date_weekend = []
        public_holiday = self.env['resource.calendar.leaves']
        public_holiday_sum = 0
        all_day_weekend_public = []
        list_all_weekend = []
        for holiday in self:
            if holiday.date_from and holiday.date_to:
                if holiday.holiday_status_id.smartest_holidays_mode == "open":
                    holiday.number_of_days = \
                        holiday._get_number_of_days(holiday.date_from, holiday.date_to, holiday.employee_id.id)['days']
                elif holiday.holiday_status_id.smartest_holidays_mode == "calendar":
                    if len(holiday.employee_id.resource_calendar_id.extract_day_of()) == 1:
                        date_weekend = date_weekend.append(holiday.extract_weekend_between_date_from_to(
                            NUM_WEEK[str(holiday.employee_id.resource_calendar_id.extract_day_of()[0])]))
                        all_day_weekend_public = date_weekend
                    elif len(holiday.employee_id.resource_calendar_id.extract_day_of()) == 2:
                        date_weekend = holiday.extract_weekend_between_date_from_to(
                            NUM_WEEK[str(holiday.employee_id.resource_calendar_id.extract_day_of()[0])])
                        list_weekend = holiday.extract_weekend_between_date_from_to(
                            NUM_WEEK[str(holiday.employee_id.resource_calendar_id.extract_day_of()[1])])
                        list_all_weekend = list_weekend + date_weekend
                        all_day_weekend_public = list_all_weekend
                    public = public_holiday.search(
                            [('calendar_id', '=', holiday.employee_id.resource_calendar_id.id),('resource_id', '=', False)]).filtered(
                            lambda public: public if public.date_from > holiday.date_from or public.date_to > holiday.date_from else None)
                    if not public is None:
                        for public in public_holiday.search(
                                [('calendar_id', '=', holiday.employee_id.resource_calendar_id.id),('resource_id', '=', False)]).filtered(
                                lambda public: public if public.date_from > holiday.date_from or public.date_to > holiday.date_from else None):
                            if public.date_from >= holiday.date_from and public.date_from < holiday.date_to and public.date_to < holiday.date_to:
                                print(holiday.date_range(public.date_from.date(), public.date_to.date()))
                                all_day_weekend_public = all_day_weekend_public + holiday.date_range(public.date_from.date(), public.date_to.date())
                                all_day_weekend_public = list(set(all_day_weekend_public))
                            elif public.date_from > holiday.date_from and public.date_from < holiday.date_to and public.date_to > holiday.date_to:
                                all_day_weekend_public = all_day_weekend_public + holiday.date_range(public.date_from.date(),
                                                                                               holiday.date_to.date())
                                all_day_weekend_public = list(set(all_day_weekend_public))
                            elif public.date_from < holiday.date_from and public.date_to < holiday.date_to and public.date_to > holiday.date_from:
                                all_day_weekend_public = all_day_weekend_public + holiday.date_range(holiday.date_from.date(),
                                                                                               public.date_to.date())
                                all_day_weekend_public = list(set(all_day_weekend_public))
                    if type(all_day_weekend_public) is not list:
                        weekend = 0
                    else:
                        weekend = int(len(all_day_weekend_public))
                    holiday.number_of_days = \
                        holiday._get_number_of_days(holiday.date_from, holiday.date_to, holiday.employee_id.id)[
                            'days'] + weekend
            else:
                holiday.number_of_days = 0

    def _get_holidays_notification_emails(self):
        """ Get comma-separated notification email addresses. """
        self.ensure_one()
        emails = self.holiday_status_id.smartest_notify_group_ids.users.mapped('email_formatted') or []
        emails.append(self.employee_id.work_email)
        emails.append(self.employee_id.leave_manager_id.email_formatted)
        return ",".join([e for e in emails if e])

    def action_send_email(self):
        self.ensure_one()
        mail_template_leave = self.env.ref('smartest_hr_holidays.approval_email_template_validated_leave',
                                     raise_if_not_found=False)
        mail_template_absence = self.env.ref('smartest_hr_holidays.approval_email_template_validated_absence',
                                     raise_if_not_found=False)
        if self.holiday_status_id == self.env.ref('smartest_hr_holidays.holiday_status_anticip') or self.holiday_status_id == self.env.ref('hr_holidays.holiday_status_cl'):
            if mail_template_leave:
                mail_template_leave.send_mail(self.id)
        else:
            if mail_template_absence:
                if self.supported_attachment_ids:
                    for rec in self.supported_attachment_ids:
                        mail_template_absence.attachment_ids = [(4,rec.id)]
                mail_template_absence.send_mail(self.id)



    def get_allocation_ids(self, employee_id, holiday_status_id):

        employee_allocations = self.env['hr.leave.allocation'].search(
            [('employee_id', '=', employee_id), ('holiday_status_id', '=', holiday_status_id),
             ('state', '=', 'validate')], order='date_from asc')
        allocation_list = []
        for allocation in employee_allocations:
            if allocation.number_of_days > allocation.leaves_taken:
                allocation_list.append(allocation)
        return allocation_list

    def creation_leave_child(self, number_of_days_allocated):
        results = []
        all_days = []
        allocation_ids = self.get_allocation_ids(self.employee_id.id, self.holiday_status_id.id)
        request_date_from = self.request_date_from
        date_from = self.date_from
        index = 0
        number_of_days = abs(number_of_days_allocated)
        new_request_date_to = self.request_date_from + relativedelta(days=abs(number_of_days_allocated)-1)
        new_date_to = self.date_from.replace(hour=16) + relativedelta(days=abs(number_of_days_allocated)-1)
        while number_of_days > 0 and index <= len(allocation_ids)-1:
            allocation_id = allocation_ids[index]
            results.append({
                'employee_id': self.employee_id.id,
                'holiday_status_id': self.holiday_status_id.id,
                'request_date_from': request_date_from,
                'date_from': date_from,
                'request_date_to': new_request_date_to,
                'date_to': new_date_to,
                'number_of_days': number_of_days,
                'holiday_type': 'employee',
                'department_id': self.department_id.id,
                'state': 'draft',
                'smartest_hide_child_leave': True,
                'smartest_parent_id_allocation': self.id,
                'holiday_allocation_id': allocation_id.id,
            })
            number_of_days_allocated = allocation_id.number_of_days_display - allocation_id.leaves_taken
            all_days.append(number_of_days_allocated)
            request_date_from = self.request_date_from + relativedelta(days=abs(sum(all_days)))
            date_from = self.date_from + relativedelta(days=abs(sum(all_days)))

            number_of_days = self.number_of_days - abs(sum(all_days))
            index += 1
            h = index
            if index <= len(allocation_ids)-1:
                number_of_days_allocated = allocation_ids[h].number_of_days_display - allocation_ids[h].leaves_taken
                if number_of_days_allocated < number_of_days:
                    number_of_days = number_of_days_allocated
                new_request_date_to = request_date_from + relativedelta(days=abs(number_of_days) - 1)
                new_date_to = date_from.replace(hour=16) + relativedelta(days=abs(number_of_days) - 1)
        print(results)
        for resul in results:
            allocation_ids = self.with_context(pass_holiday_status_constraint=True).create(resul)
            allocation_ids.sudo().action_confirm()
            allocation_ids.sudo().filtered(lambda alloc: alloc.state == 'confirm').action_approve()
            allocation_ids.sudo().filtered(lambda alloc: alloc.state == 'validate1').action_validate()

    def action_validate(self):
        res = None
        for leave in self:
            if leave.holiday_status_id.smartest_cumulative_leave:
                number_of_days_allocated = leave.holiday_allocation_id.number_of_days_display - leave.holiday_allocation_id.leaves_taken
                if abs(number_of_days_allocated) >= self.number_of_days:
                    if not leave.smartest_hide_child_leave:
                        res = super(HrLeave, self).action_validate()
                        leave.action_send_email()
                    else:
                        res = super(HrLeave, self).action_validate()
                else:
                    if not leave.smartest_hide_child_leave:
                        all_days_allocation = 0
                        all_days_taken = 0
                        for allocation in self.get_allocation_ids(leave.employee_id.id, leave.holiday_status_id.id):
                            all_days_allocation += allocation.max_leaves
                            all_days_taken += allocation.leaves_taken
                        days_available = all_days_allocation - abs(all_days_taken)
                        if days_available >= self.number_of_days:
                            self.action_stop()
                            self.creation_leave_child(number_of_days_allocated)
                            self.write({'state': 'done','holiday_allocation_id':False})
                            leave.action_send_email()
                        else:
                            raise ValidationError(
                                _('vous ne disposez pas d"allocation.')
                            )
            else:
                res = super(HrLeave, self).action_validate()
                leave.action_send_email()
        return res

    @api.depends('holiday_status_id.requires_allocation', 'validation_type', 'employee_id', 'date_from', 'date_to')
    def _compute_from_holiday_status_id(self):
        invalid_self = self.filtered(lambda leave: not leave.date_to or not leave.date_from)
        if invalid_self:
            invalid_self.update({'holiday_allocation_id': False})
            self = self - invalid_self
        if not self:
            return
        allocations = self.env['hr.leave.allocation'].search_read(
            [
                ('holiday_status_id', 'in', self.holiday_status_id.ids),
                ('employee_id', 'in', self.employee_id.ids),
                ('state', '=', 'validate'),
                '|',
                ('date_to', '>=', min(self.mapped('date_to'))),
                '&',
                ('date_to', '=', False),
                ('date_from', '<=', max(self.mapped('date_from'))),
            ], ['id', 'date_from', 'date_to', 'holiday_status_id', 'employee_id', 'max_leaves', 'taken_leave_ids'],
            order="date_to, id"
        )
        allocations_dict = defaultdict(lambda: [])
        for allocation in allocations:
            allocation['taken_leaves'] = self.env['hr.leave'].browse(allocation.pop('taken_leave_ids')) \
                .filtered(lambda leave: leave.state in ['confirm', 'validate', 'validate1'])
            allocations_dict[(allocation['holiday_status_id'][0], allocation['employee_id'][0])].append(allocation)

        for leave in self:
            if leave.holiday_status_id.requires_allocation == 'yes' and leave.date_from and leave.date_to:
                found_allocation = False
                date_to = leave.date_to.replace(tzinfo=UTC).astimezone(timezone(leave.tz)).date()
                date_from = leave.date_from.replace(tzinfo=UTC).astimezone(timezone(leave.tz)).date()
                leave_unit = 'number_of_%s_display' % ('hours' if leave.leave_type_request_unit == 'hour' else 'days')
                for allocation in allocations_dict[(leave.holiday_status_id.id, leave.employee_id.id)]:
                    date_to_check = allocation['date_to'] >= date_to if allocation['date_to'] else True
                    date_from_check = allocation['date_from'] <= date_from
                    if (date_to_check and date_from_check):
                        allocation_taken_leaves = allocation['taken_leaves'] - leave
                        allocation_taken_number_of_units = sum(allocation_taken_leaves.mapped(leave_unit))
                        leave_number_of_units = leave[leave_unit]
                        if allocation['max_leaves'] >= allocation_taken_number_of_units + leave_number_of_units:
                            found_allocation = allocation['id']
                            break
                if leave.get_allocation_ids(leave.employee_id.id, leave.holiday_status_id.id):
                    leave.holiday_allocation_id = \
                        leave.get_allocation_ids(leave.employee_id.id, leave.holiday_status_id.id)[0] or False
                if not leave.holiday_allocation_id is False and leave.holiday_allocation_id:
                    leave.holiday_allocation_id = leave.holiday_allocation_id.id or False
                else:
                    leave.holiday_allocation_id = False
            else:
                leave.holiday_allocation_id = False
