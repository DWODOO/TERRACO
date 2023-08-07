# -*- coding:utf-8 -*-

from odoo import fields, models,api



class SmartestHrApplicant(models.Model):
    _inherit = 'hr.applicant'

    survey_ids = fields.Many2one(
        'survey.survey',
        compute='_compute_survey_ids'
    )

    last_check = fields.Boolean(
    )

    total_score = fields.Float(
        compute="_compute_total_score"
    )


    @api.onchange('stage_id','job_id')
    def _compute_survey_ids(self):
        survey = self.env["survey.survey"].search([('job_id','=',self.job_id.id),('check_stage','=',self.stage_id.id)])
        if survey:
            self.survey_ids = survey
        else:
            self.survey_ids = None


    def action_test_survey_one(self):
        for rec in self:
            if rec.survey_ids:
                rec.ensure_one()
                print('/survey/'+str(rec.id)+'/start/%s' % rec.survey_ids.access_token)
                return {
                    'type': 'ir.actions.act_url',
                    'name': "Survey",
                    'target': 'self',
                    'url': '/survey/'+str(rec.id)+'/start/%s' % rec.survey_ids.access_token,
                }


    def action_survey_applicant(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Interview',
            'view_mode': 'tree,form',
            'res_model': 'survey.user_input',
            'domain': [('applicant_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def _compute_total_score(self):
        for rec in self:
            survey = rec.env['survey.user_input'].search([('applicant_id', '=', rec.id)]).mapped('scoring_percentage')
            if survey:
                rec.total_score = sum(survey)/len(survey)
            else:
                rec.total_score = 0