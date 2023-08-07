# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools

class SmartestStockMove(models.Model):
    _inherit = 'stock.move'

    def product_price_update_before_done(self, forced_qty=None):
        for move in self:
            for move in self:
                smartest_cost = move._get_price_unit()
                move.product_tmpl_id.smartest_product_last_cost = smartest_cost
            return super(SmartestStockMove, self).product_price_update_before_done()