# -*- coding:utf-8 -*-
from odoo import models, fields


class HrContract(models.Model):
    _inherit = 'hr.contract'

    paid_hourly_attendance = fields.Boolean(
        "Paid Hourly Attendance",
        copy=True
    )
