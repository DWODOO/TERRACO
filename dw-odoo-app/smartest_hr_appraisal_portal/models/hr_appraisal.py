# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SmartestHrAppraisal(models.Model):
    _name = 'hr.appraisal'
    _inherit = ['hr.appraisal', 'portal.mixin']

    def _compute_access_url(self):
        super(SmartestHrAppraisal, self)._compute_access_url()
        for appraisal in self:
            appraisal.access_url = '/my/appraisals/%s' % appraisal.id
