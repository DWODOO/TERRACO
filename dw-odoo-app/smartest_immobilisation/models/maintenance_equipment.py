# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    barcode = fields.Char(
        'Barcode', copy=False,
        help="International Article Number used for product identification.")
