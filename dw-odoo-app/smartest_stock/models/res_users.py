# -*- coding:utf-8 -*-
from odoo import models, fields


class SmartestResUsers(models.Model):
    _inherit = 'res.users'

    smartest_warehouse_ids = fields.Many2many(
        'stock.warehouse',
        string="Autorisé"
    )

    def write(self, vals):
        if vals.get('smartest_warehouse_ids'):
            self.env['ir.rule'].clear_caches()
        return super(SmartestResUsers, self).write(vals)
