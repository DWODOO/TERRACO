# -*- coding: utf-8 -*-
from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_invoices(self, grouped=False, final=False):
        move_ids = super(SaleOrder, self)._create_invoices(grouped, final)
        for move in move_ids:
            move._onchange_invoice_line_ids()
        return move_ids
