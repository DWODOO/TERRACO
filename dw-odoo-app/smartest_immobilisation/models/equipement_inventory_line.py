# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EquipementInventoryLIne(models.Model):
    _name = 'equipement.inventory.line'

    equipement = fields.Many2one(
        'maintenance.equipment'
    )

    category = fields.Many2one('maintenance.equipment.category')

    first_count =fields.Integer('First Count')

    date = fields.Date(
        string='Accounting Date'
    )

    serial_no = fields.Char('Serial Number')

    barcode = fields.Char(
        'Barcode', copy=False,
        help="International Article Number used for product identification.")

    equipement_inventory_id = fields.Many2one('equipement.inventory',string='inventory id')

