# -*- coding:utf-8 -*-
from odoo import api, models, fields


class SmartestHrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    smartest_holidays_request_delay = fields.Integer(
        string="Holidays request delay"
    )
    smartest_duration_of_leave = fields.Integer(
        string="Holiday duration",
        help="If greater than 0 then the number of days of the holidays request must be exactly as this value. "
             "If 0 then any value will be allowed on holidays request."
    )
    smartest_holidays_mode = fields.Selection([
        ('calendar','Calendar'),
        ('open','Open'),
    ],
        required=True,
        default='open',
        string="Leave calculation",
        help='If "Open", the weekend days will be excluded in the holidays. '
             'If "Calendar", the weekend days will be included from the holidays.'
    )
    smartest_allow_prolong_suspend = fields.Boolean(
        string="Allow leave expanding or suspension",
    )
    smartest_allow_cancellation = fields.Boolean(
        string="Allow leave canceling",
    )
    smartest_allow_editing = fields.Boolean(
        string="Allow leave editing",
    )
    smartest_notify_group_ids = fields.Many2many(
        comodel_name='res.groups',
        string="Users who will be notified"
    )
    smartest_carry_over_threshold = fields.Integer(
        string="Carry over notification threshold"
    )
    smartest_include_carry_over = fields.Boolean(
        string="Include in carry over notification"
    )
    smartest_is_mariage = fields.Boolean(
        string="is wedding"
    )

    smartest_is_death = fields.Boolean(
        string="is death"
    )
    smartest_is_exceptional_death = fields.Boolean(
        string="is death"
    )
    smartest_leave_categories = fields.Many2one(
        'leave.categories',
        string="Categories"
    )
    smartest_cumulative_leave= fields.Boolean(
        string="Cumulative leave",
    )
    smartest_portal_type_leave = fields.Boolean(
        string="Show this type of leave in portal"
    )
    smartest_type_leave_access_to_crud = fields.Boolean(
        string="access correspondant"
    )

    @api.onchange('smartest_duration_of_leave')
    def _onchange_requires_allocation(self):
        if self.requires_allocation == 'yes':
            self.smartest_duration_of_leave = 0
