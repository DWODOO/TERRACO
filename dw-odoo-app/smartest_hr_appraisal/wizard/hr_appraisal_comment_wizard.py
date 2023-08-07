# -*- coding: utf-8 -*-

# Import Odoo libs
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SmartestHrAppraisalLine(models.TransientModel):
    _name = 'hr.appraisal.comment.wizard'
    _description = 'Appraisal Comments Wizard'

    appraisal_line_id = fields.Many2one(
        'hr.appraisal.line',
        'Appraisal Line',
        required=True,
        readonly=True,
        store=True,
    )
    comment = fields.Html(
        'Comments',
        required=True
    )

    def action_post(self):
        self.ensure_one()
        return self.appraisal_line_id.message_post(body=self.comment, subject=_("Appraisal"))
