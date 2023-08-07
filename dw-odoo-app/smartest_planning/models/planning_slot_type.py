# -*- coding: utf-8 -*-

# Import Odoo libs
from odoo import _, fields, models


class SmartestPlanningSlotType(models.Model):
    _name = 'planning.slot.type'
    _description = 'Planning Shift Type'
    _order = 'sequence'

    name = fields.Char(
        'Name',
        required=True,
        index=True,
        translate=True
    )
    description = fields.Text(
        'Description',
        translate=True
    )
    sequence = fields.Integer(
        'Sequence',
        default=10
    )
    active = fields.Boolean(
        'Active',
        default=True
    )
    color = fields.Integer(
        'Color',
        default=0
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _('The type name must be unique'))
    ]
