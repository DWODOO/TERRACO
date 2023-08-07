# -*- coding: utf-8 -*-
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class SmartestAccountPayment(models.Model):
    _inherit = 'account.payment'


    no_invoice_payment = fields.Boolean(
        string="ND",
        default=False
    )
    unlock_seq = fields.Boolean(default=False, store=True, help="check this button if you don't want to change a seq number")

    def action_post(self):
        for payment in self:
            IrSequence = self.env['ir.sequence']
            if not payment.unlock_seq:
                if payment.no_invoice_payment :
                    payment.name = IrSequence.next_by_code('account.payment.not.declared')
                    payment.on_change_no_invoice()
                else:
                    payment.name = IrSequence.next_by_code('account.payment.declared')
        return super(SmartestAccountPayment, self).action_post()


    def on_change_no_invoice(self):
        for this in self:
            if this.state == 'draft' and this.no_invoice_payment and this.payment_type == 'inbound' :
                this.fiscal_position_id = self.env.ref('smartest_no_invoice.smartest_no_invoice_fiscal_position')
                this.move_id.no_invoice = True
                if this.move_id.line_ids:
                    for line in this.move_id.line_ids.filtered(lambda this: this.account_id.user_type_id.type == 'receivable') :
                        line.sudo().account_id = this.fiscal_position_id.property_account_receivable_id
