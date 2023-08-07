# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_employee_sequence = fields.Boolean(
        related='company_id.use_employee_sequence',
        readonly=False
    )

    employee_sequence_id = fields.Many2one(
        'ir.sequence',
        related='company_id.employee_sequence_id',
        readonly=False
    )

    use_contract_sequence = fields.Boolean(
        related='company_id.use_contract_sequence',
        readonly=False
    )

    contract_sequence_id = fields.Many2one(
        'ir.sequence',
        related='company_id.contract_sequence_id',
        readonly=False
    )

