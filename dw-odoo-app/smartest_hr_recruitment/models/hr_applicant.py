# -*- coding:utf-8 -*-
from odoo import _, api, fields, models

AVAILABLE_PRIORITIES = [
    ('0', 'None'),
    ('1', 'Bad'),
    ('2', 'Medium'),
    ('3', 'Quite good'),
    ('4', 'Good'),
    ('5', 'Excellent'),
]


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    priority = fields.Selection(
        AVAILABLE_PRIORITIES
    )
