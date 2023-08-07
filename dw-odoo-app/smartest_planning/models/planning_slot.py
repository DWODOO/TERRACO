# -*- coding: utf-8 -*-

# Import Odoo libs
from odoo import fields, models


class SmartestPlanningSlot(models.Model):
    _inherit = 'planning.slot'

    type_id = fields.Many2one(
        'planning.slot.type',
        'Type',
        index=True,
    )
    type_color = fields.Integer(
        'Type Color',
        related='type_id.color'
    )
