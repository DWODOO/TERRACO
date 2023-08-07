# -*- coding:utf-8 -*-

from odoo import fields, models


class SmartestHrRecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'

    survey_ids = fields.Many2many(
        'survey.survey',
        string='Interview form',
    )

    check_interview = fields.Selection(
        [('first', 'First'),
         ('second', 'Second'),
         ('last', 'Last'),], string="Interview"
    )