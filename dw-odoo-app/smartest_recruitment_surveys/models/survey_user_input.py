# -*- coding:utf-8 -*-

from odoo import fields, models,api


class SmartestSurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    applicant_id = fields.Many2one(
        'hr.applicant',
        string='Applicant'
    )



