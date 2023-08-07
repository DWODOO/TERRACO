# -*- coding:utf-8 -*-
from odoo import api, fields, models, _


class Contract(models.Model):
    _inherit = 'hr.contract'

    struct_id = fields.Many2one(
        'hr.payroll.structure',
        string='Salary Structure',
        # default=lambda self: self.env.ref('l10n_dz_payroll.structure_base_dz')
    )
