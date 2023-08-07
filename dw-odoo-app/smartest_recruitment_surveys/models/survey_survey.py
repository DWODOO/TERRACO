# -*- coding:utf-8 -*-

from odoo import fields, models


class SmartestSurveySurvey(models.Model):
    _inherit = 'survey.survey'

    job_id = fields.Many2one(
        'hr.job'
    )

    check_stage = fields.Many2one(
        'hr.recruitment.stage',
        string="Stage"
    )



