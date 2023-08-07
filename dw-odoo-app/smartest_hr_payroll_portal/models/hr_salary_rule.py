# -*- coding: utf-8 -*-
from odoo import fields, models


class SmartestHrSalaryRUle(models.Model):
    _inherit = 'hr.salary.rule'

    portal_hide = fields.Boolean(
        'Hide on portal ?'
    )
