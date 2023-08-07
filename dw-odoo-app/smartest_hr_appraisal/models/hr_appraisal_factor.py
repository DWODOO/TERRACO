# -*- coding: utf-8 -*-

# Import Odoo libs
from odoo import _, api, fields, models


class SmartestHrAppraisalFactor(models.Model):
    _name = "hr.appraisal.factor"
    _description = "Employee Performance Factor"
    _order = 'sequence'

    name = fields.Char(
        'Name',
        required=True,
        index=True,
        translate=True
    )
    sequence = fields.Integer(
        'Sequence',
        default=10
    )
    score = fields.Float(
        'Score',
        default=10.0
    )
    category_id = fields.Many2one(
        'hr.appraisal.factor.category',
        'Category',
        required=True,
        index=True,
    )
    description = fields.Text(
        'Description',
        translate=True
    )
    active = fields.Boolean(
        'Active',
        default=True
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _('The factor name must be unique'))
    ]
