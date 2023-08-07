# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IntermediateLine(models.Model):
    _name = 'intermediate.line'

    equipement = fields.Many2one(
        'maintenance.equipment'
    )

    category = fields.Many2one('maintenance.equipment.category')

    serial_no = fields.Char('Serial Number')





