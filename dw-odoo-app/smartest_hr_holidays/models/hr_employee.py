# -*- coding:utf-8 -*-
from odoo import models, fields, api, _


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'


    anticipated_request = fields.Boolean(
        string="Anticipated Request",
        default=True
    )
    working_in_south_area = fields.Boolean(
        string="Working in south area"
    )
    attribution_auto_leave = fields.Boolean(
        string="Inclus in allocation",
        default = True
    )
    current_leave_state = fields.Selection(selection_add=[
        ('suspend', 'Suspend'),
        ('stop', 'Stop'),
        ('prolonged','Prolonged'),
        ('done', 'Confirmed by manager'),
    ])

    def _get_remaining_leaves(self):
        """ Helper to compute the remaining leaves for the current employees
            :returns dict where the key is the employee id, and the value is the remain leaves
        """
        self._cr.execute("""
            SELECT
                sum(h.number_of_days) AS days,
                h.employee_id
            FROM
                (
                    SELECT holiday_status_id, number_of_days,
                        state, employee_id
                    FROM hr_leave_allocation
                    UNION ALL
                    SELECT holiday_status_id, (number_of_days * -1) as number_of_days,
                        state, employee_id
                    FROM hr_leave
                ) h
                join hr_leave_type s ON (s.id=h.holiday_status_id)
            WHERE
                s.active = true AND h.state='validate' AND
                s.requires_allocation='yes' AND s.smartest_include_carry_over = true AND
                h.employee_id in %s
            GROUP BY h.employee_id""", (tuple(self.ids),))
        return dict((row['employee_id'], row['days']) for row in self._cr.dictfetchall())



class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def action_send_email(self, allocation):
        mail_template = self.env.ref('smartest_hr_holidays.approval_email_template_carry_over', False)
        if mail_template:
            mail_template.send_mail(self.id, force_send=False)

    def cron_carry_over_method(self):
        allocations = self.env['hr.leave.allocation'].search([
            ('employee_id.attribution_auto_leave', '=', True),
            ('employee_id.contract_id.state', '=', 'open'),
            ('holiday_status_id.smartest_include_carry_over', '=', True),
            ('holiday_status_id.smartest_carry_over_threshold', '>', 0),
        ])
        for allocation in allocations:
            if (allocation.max_leaves - allocation.leaves_taken) > allocation.holiday_status_id.smartest_carry_over_threshold:
                allocation.employee_id.action_send_email(allocation)

