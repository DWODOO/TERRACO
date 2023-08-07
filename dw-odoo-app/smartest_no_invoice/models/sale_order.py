# -*- coding: utf-8 -*-
from num2words import num2words
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SmartestSaleOrder(models.Model):
    _inherit = 'sale.order'

    date = fields.Date(required=True,
                          default=fields.Date.context_today)
    no_invoice = fields.Boolean(
        string="ND", default=False
    )

    @api.onchange('no_invoice','partner_id')
    def on_change_no_invoice(self):
        for this in self:
            if this.state == 'draft' and this.no_invoice:
                this.fiscal_position_id = self.env.ref('smartest_no_invoice.smartest_no_invoice_fiscal_position')
                return this.fiscal_position_id.check_fiscal_position_configuration()
            elif this.state == 'draft' and not this.no_invoice:
                this.fiscal_position_id = False


class SmartestSaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    no_invoice = fields.Boolean(
        string="ND", default=False
    )

    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = {
            'ref': order.client_order_ref,
            'move_type': 'out_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'no_invoice': self.no_invoice,
            'partner_id': order.partner_invoice_id.id,
            'fiscal_position_id': (order.fiscal_position_id or order.fiscal_position_id.get_fiscal_position(order.partner_id.id)).id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_reference': order.reference,
            'invoice_payment_term_id': order.payment_term_id.id,
            'partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,
            'team_id': order.team_id.id,
            'campaign_id': order.campaign_id.id,
            'medium_id': order.medium_id.id,
            'source_id': order.source_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'product_id': self.product_id.id,
                'product_uom_id': so_line.product_uom.id,
                'tax_ids': [(6, 0, so_line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [so_line.id])],
                'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id or False,
            })],
        }

        return invoice_vals
