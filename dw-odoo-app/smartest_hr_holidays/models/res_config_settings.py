# -*- coding:utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    jours_conge = fields.Integer(
        string="Holiday must be requested before",
        related='company_id.jours_conge',
        readonly=False,
    )  # smartest_holidays_request_delay

    @api.constrains('jours_conge')
    def _check_jours_conge(self):
        if any(record.jours_conge < 0 for record in self):
            raise ValidationError(
                _('Number of days between holidays requests and holidays start date must be positive.')
            )
