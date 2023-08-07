# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    min_attendance_worked_hours = fields.Float(
        related='company_id.min_attendance_worked_hours',
        readonly=False
    )

