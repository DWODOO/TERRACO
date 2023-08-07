# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA

# Import Odoo libs
from odoo import fields, models


class SmartestResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    smartest_calendar_forced = fields.Boolean(string="Calendar Forced")
    smartest_number_days_forced = fields.Integer(string="Number of Days")
