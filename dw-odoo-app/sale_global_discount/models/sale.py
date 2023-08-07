# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SmartestSaleOrder(models.Model):
    _inherit = 'sale.order'

    global_discount = fields.Float('Global Discount', compute="_compute_global_discount_percent", readonly=0, store=1)
    global_discount_percent = fields.Float('Global Discount', compute="_compute_global_discount", readonly=0, store=1)
    amount_untaxed_with_discount = fields.Float('Montant Brut', compute="_compute_amount_untaxed_with_discount", readonly=1, store=1)


    @api.depends('global_discount')
    def _compute_global_discount(self):
        for sale in self.sudo():
            sale.global_discount_percent = 0
            sale.order_line.discount = 0
            rate = sale.global_discount * 100 / sale.amount_untaxed
            sale.global_discount_percent = rate
            if rate != 0:
                self.sudo().create_discount_line(sale.global_discount,sale.id)
            else:
                sale.sudo().order_line.discount_amount = 0

    def create_discount_line(self,global_discount,sale_id):
        for sale in self:
            acctual_global_discount = 0
            if 'NewId_' in str(sale_id) :
                sale_id = int(str(sale_id).replace('NewId_',''))
            for line in sale.order_line:
                if line.id == sale.order_line[-1].id:
                    line.discount_amount = global_discount - acctual_global_discount
                else:
                    line.discount_amount = ((line.price_unit*line.product_uom_qty)/sale.amount_untaxed)*sale.global_discount
                    acctual_global_discount += line.discount_amount



    @api.depends('global_discount_percent')
    def _compute_global_discount_percent(self):
        for sale in self:
            sale.global_discount = 0
            sale.order_line.discount = 0
            inv_rate = sale.amount_untaxed * sale.global_discount_percent / 100
            sale.global_discount = inv_rate
            if inv_rate != 0:
                self.sudo().create_discount_line(sale.global_discount,sale.id)
            else:
                sale.sudo().order_line.discount_amount = 0

    @api.depends('global_discount','amount_untaxed')
    def _compute_amount_untaxed_with_discount(self):
        for sale in self:
            sale.amount_untaxed_with_discount = sale.amount_untaxed + sale.global_discount


class SmartestSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    invisible_on_sale = fields.Boolean(related='product_id.invisible_on_sale', readonly=True, store=False)
    discount_amount = fields.Monetary(string='Discount Amount')

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id','discount_amount')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded']- line.discount_amount,
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups('account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    def _prepare_invoice_line(self, **optional_values):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        :param optional_values: any parameter that should be added to the returned invoice line
        """
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'discount_amount': self.discount_amount,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
        }
        if self.order_id.analytic_account_id:
            res['analytic_account_id'] = self.order_id.analytic_account_id.id
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res