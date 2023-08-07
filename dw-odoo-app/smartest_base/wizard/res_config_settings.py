# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_res_partner_code = fields.Boolean(
        "Manage Partners Codes",
        implied_group='smartest_base.group_res_partner_code'
    )
