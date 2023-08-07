# -*- coding: utf-8 -*-
from odoo import models, fields


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    auto_post_invoice = fields.Boolean(
        "Validate invoice?",
        default=True
    )

    def _create_invoice(self, order, so_line, amount):
        """
        Override this method in order to post the invoice automatically if the field 'auto_post_invoice' is True
        """
        invoice_id = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        invoice_id._onchange_invoice_line_ids()
        return invoice_id
