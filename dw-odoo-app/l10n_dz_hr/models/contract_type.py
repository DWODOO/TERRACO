# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ContractType(models.Model):
    _inherit = 'hr.contract.type'

    law_section_ids = fields.Many2many(
        'hr.law.sections',
        'hr_contract_type_law_sections',
        'type_id',
        'law_id',
    )
