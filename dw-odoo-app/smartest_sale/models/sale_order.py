# -*- coding: utf-8 -*-
from odoo import _, api, Command, fields, models
from odoo.tools.misc import formatLang


class SmartestSaleOrder(models.Model):
    _inherit = 'sale.order'

    use_stamp_tax = fields.Boolean(
        related='company_id.use_stamp_tax',
        tracking=True,
    )
    amount_stamp_tax = fields.Monetary(
        'Stamp Duty',
        currency_field='currency_id',
        store=True,
        readonly=True,
        tracking=True,
        compute='_compute_amounts'
    )  # This field used to store the amount of stamp duty tax if it exist
    amount_total_with_tva = fields.Monetary(
        'Total With TVA',
        currency_field='currency_id',
        store=True,
        readonly=True,
        tracking=True,
        compute='_compute_amounts'
    )  # This field used to store the total amount with taxes. Because the amount_stamp_tax is not yet included
    payment_method_id = fields.Many2one(
        "account.payment.method",
        readonly=True,
        tracking=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain=[('payment_type', '=', 'outbound')]
    )  # This field is used to get the payment method and derive if the stamp duty tax is applicable or not.
    payment_term_id = fields.Many2one(
        'account.payment.term',
        readonly=True,
        tracking=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}
    )
    apply_stamp_duty_tax = fields.Boolean(
        "Apply Stamp Duty?",
        readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}
    )  # This field is used to compute amount_stamp_tax. The Stamp duty taxed is used only when this field is true

    @api.onchange('payment_method_id', 'use_stamp_tax')
    def _onchange_payment_method_id(self):
        if not self.use_stamp_tax:
            self.apply_stamp_duty_tax = False
        elif self.payment_method_id:
            self.apply_stamp_duty_tax = self.payment_method_id.apply_stamp_duty_tax

    # @api.onchange('apply_stamp_duty_tax')
    # def _onchange_apply_stamp_duty_tax(self):
    #     self._compute_amounts()

    @api.depends('order_line.price_subtotal', 'order_line.price_tax', 'order_line.price_total', 'apply_stamp_duty_tax')
    def _compute_amounts(self):
        """
        Override this method to add computation of amount_stamp_tax & amount_total_with_tva
        """
        super(SmartestSaleOrder, self)._compute_amounts()
        for order in self:
            amount_total_with_tva = order.amount_total
            amount_stamp_tax = order._get_stamp_tax_amount(amount_total_with_tva)
            order.update({
                'amount_stamp_tax': amount_stamp_tax,
                'amount_total_with_tva': amount_total_with_tva,
                'amount_total': amount_total_with_tva + amount_stamp_tax,
            })

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'apply_stamp_duty_tax')
    def _compute_tax_totals(self):
        super(SmartestSaleOrder, self)._compute_tax_totals()
        for sale in self:
            tax_totals = sale.tax_totals
            if tax_totals and 'amount_total' in tax_totals and tax_totals['amount_total']:
                base_amount = tax_totals['amount_total']
                stamp_tax_amount = sale._get_stamp_tax_amount(base_amount)
                sale.amount_stamp_tax = stamp_tax_amount
                amount_total = base_amount + stamp_tax_amount
                tax_totals.update({
                    'stamp_tax_amount': stamp_tax_amount,
                    'formatted_stamp_tax_amount': formatLang(self.env, stamp_tax_amount, currency_obj=sale.currency_id),
                    'formatted_amount_total_with_stamp': formatLang(self.env, amount_total,
                                                                    currency_obj=sale.currency_id),
                    'amount_total': amount_total,
                    'formatted_amount_total': formatLang(self.env, amount_total, currency_obj=sale.currency_id),
                })
            sale.tax_totals = tax_totals

    def _prepare_invoice(self):
        invoice_vals = super(SmartestSaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'payment_method_id': self.payment_method_id.id,
            'apply_stamp_duty_tax': self.apply_stamp_duty_tax,
        })
        return invoice_vals

    def _get_stamp_tax_amount(self, base_amount):
        self.ensure_one()
        company_id = self.company_id
        if not self.use_stamp_tax \
                or not self.apply_stamp_duty_tax \
                or 0 in company_id.read(['slice', 'slice_amount']) \
                or base_amount < company_id.invoice_amount_min:
            return 0.0
        else:
            slice_count = base_amount // company_id.slice
            rest = base_amount % company_id.slice
            if rest:
                slice_count += 1
            amount_stamp_tax = slice_count * company_id.slice_amount
            if amount_stamp_tax > company_id.stamp_tax_max:
                amount_stamp_tax = company_id.stamp_tax_max
            elif amount_stamp_tax < company_id.stamp_tax_min:
                amount_stamp_tax = company_id.stamp_tax_min

            return amount_stamp_tax
