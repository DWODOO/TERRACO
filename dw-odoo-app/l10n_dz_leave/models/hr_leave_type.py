# -*- coding:utf-8 -*-

from odoo import models, fields


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    allocation_ids = fields.One2many(
        'hr.leave.allocation',
        'holiday_status_id'
    )
    leave_situation = fields.Selection(
        [
            ('annual_leave', 'Annual Leave'),
            ('unpaid_leave', 'Unpaid Leave'),
            ('recovery_leave', 'Recovery Leave'),
        ],
        'Leave situation'
    )
