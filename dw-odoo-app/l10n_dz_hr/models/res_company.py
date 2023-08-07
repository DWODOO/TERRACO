# -*- coding:utf-8 -*-
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    use_employee_sequence = fields.Boolean(
        'Use employee registration number',
    )
    employee_sequence_id = fields.Many2one(
        'ir.sequence',
        'Employee registration number',
        ondelete='restrict',
        # default=lambda self: self.env.ref('l10n_dz_hr.sequence_hr_employee_registration_number')
    )

    use_contract_sequence = fields.Boolean(
        'Use contract sequence',
    )
    contract_sequence_id = fields.Many2one(
        'ir.sequence',
        'Employee contract sequence',
        ondelete='restrict',
        # default=lambda self: self.env.ref('l10n_dz_hr.sequence_hr_employee_contract')
    )
