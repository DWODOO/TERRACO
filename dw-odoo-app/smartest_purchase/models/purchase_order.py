from odoo import fields, models, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    READONLY_STATES = {
        'purchase': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }

    partner_id = fields.Many2one(
        'res.partner',
        domain='[("is_supplier","=", True)]'
    )
    order_type = fields.Many2one(
        'purchase.order.type',
        'Purchase Order Type'
    )
    create_invoice_visible = fields.Boolean(
        "Show Invoice Button",
        compute="_compute_create_invoice_visible"
    )  # Technical Field used to show/hide create invoice button on the purchase order form view
    currency_rate_import_purchase = fields.Float(
        "Currency Rate",
        # default=lambda self: self.env.company.currency_id.rate,
        readonly=False,
        store=True,
        digits=(8, 4),
        states=READONLY_STATES,
        help='Ratio between the purchase order currency and the company currency'
    )
    active = fields.Boolean(
        default=True
    )
    swift_number = fields.Char(
        "Swift N°"
    )
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
        compute='_amount_all'
    )  # This field used to store the amount of stamp duty tax if it exist
    amount_total_with_tva = fields.Monetary(
        'Total With TVA',
        currency_field='currency_id',
        store=True,
        readonly=True,
        tracking=True,
        compute='_amount_all'
    )  # This field used to store the total amount with taxes. Because the amount_stamp_tax is not yet included
    payment_method_id = fields.Many2one(
        "account.payment.method",
        tracking=True,
        states=READONLY_STATES,
        domain=[('payment_type', '=', 'inbound')]
    )  # This field is used to get the payment method and derive if the stamp duty tax is applicable or not.
    apply_stamp_duty_tax = fields.Boolean(
        "Apply Stamp Duty?",
        states=READONLY_STATES,
    )  # This field is used to compute amount_stamp_tax. The Stamp duty taxed is used only when this field is true

    @api.onchange('payment_method_id', 'use_stamp_tax')
    def _onchange_payment_method_id(self):
        if not self.use_stamp_tax:
            self.apply_stamp_duty_tax = False
        elif self.payment_method_id:
            self.apply_stamp_duty_tax = self.payment_method_id.apply_stamp_duty_tax

    @api.depends('order_line.price_total', 'apply_stamp_duty_tax')
    def _amount_all(self):
        """
        Override this method to add computation of amount_stamp_tax & amount_total_with_tva
        """
        super(PurchaseOrder, self)._amount_all()
        for order in self:
            amount_total_with_tva = order.amount_total
            company_id = order.company_id
            if not order.apply_stamp_duty_tax or order.amount_total < company_id.invoice_amount_min:
                order.update({
                    'amount_stamp_tax': 0.0,
                    'amount_total_with_tva': amount_total_with_tva,
                })
                continue
            slice_count = amount_total_with_tva // company_id.slice
            rest = amount_total_with_tva % company_id.slice
            if rest:
                slice_count += 1
            amount_stamp_tax = slice_count * company_id.slice_amount
            if amount_stamp_tax > company_id.stamp_tax_max:
                amount_stamp_tax = company_id.stamp_tax_max
            elif amount_stamp_tax < company_id.stamp_tax_min:
                amount_stamp_tax = company_id.stamp_tax_min
            order.update({
                'amount_stamp_tax': amount_stamp_tax,
                'amount_total_with_tva': amount_total_with_tva,
                'amount_total': amount_total_with_tva + amount_stamp_tax,
            })

    @api.depends('state', 'order_line.qty_received', 'invoice_status')
    def _compute_create_invoice_visible(self):
        for order in self:
            order.create_invoice_visible = (
                    order.state in ('purchase', 'done')
                    and order.invoice_status == 'to invoice'
                    and order.order_line
                    and any(
                (line.qty_received > 0 and line.product_id.type != 'service') or line.product_id.type == 'service'
                for line in order.mapped('order_line')
            )
            )

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.company.currency_id._convert_purchase(
                        order.company_id.po_double_validation_amount, order.currency_id, order.company_id,
                        order.currency_rate_import_purchase)) \
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True

    @api.onchange('currency_id')
    def _onchange_current_currency_id(self):
        self.currency_rate_import_purchase = self.currency_id.rate

    def _prepare_invoice(self):
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        invoice_vals.update({
            'payment_method_id': self.payment_method_id.id,
            'apply_stamp_duty_tax': self.apply_stamp_duty_tax,
            'currency_rate_purchase': self.currency_rate_import_purchase,
        })
        return invoice_vals


