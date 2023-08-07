# -*- coding: utf-8 -*-

# Import Odoo libs
from odoo import _, api, fields, models


class SmartestHrAppraisalLevel(models.Model):
    _name = 'hr.appraisal.level'
    _description = 'Employee Performance Assessment Level'

    name = fields.Char(
        'Name',
        required=True,
        index=True,
        translate=True
    )
    description = fields.Text(
        'Description',
        translate=True
    )
    score_interval_min = fields.Float(
        'Min Score',
        default=0
    )
    score_interval_max = fields.Float(
        'Max Score',
        default=25
    )
    active = fields.Boolean(
        'Active',
        default=True
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _('The level name must be unique'))
    ]
