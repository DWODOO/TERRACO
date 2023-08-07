# -*- coding:utf-8 -*-
from datetime import datetime

from odoo import fields, models


class SmartestHrDepartureWizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'

    departure_reason = fields.Selection(
        [
            ('contract_end', 'Fin de contract'),
            ('trial_period', 'Période d\'éssaie non concluante'),
    ])
