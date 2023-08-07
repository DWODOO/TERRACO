# -*- coding:utf-8 -*-
from odoo import models, fields


class HrLeaveAccrualLevel(models.Model):
    _inherit = 'hr.leave.accrual.level'

    smartest_added_value_south = fields.Float(
        string="South Rate",
    )

    smartest_maximum_leave_south = fields.Float(
        string="South limited to",
    )
