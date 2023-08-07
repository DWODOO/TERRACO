# -*- coding:utf-8 -*-
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    min_attendance_worked_hours = fields.Float(
        'Attendance min hours per day',
        default=6
    )
