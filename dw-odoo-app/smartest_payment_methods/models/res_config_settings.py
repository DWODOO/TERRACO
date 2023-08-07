# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_reconciliation = fields.Boolean(
        related='company_id.auto_reconciliation',
        readonly=False
    )
    auto_invoice_post = fields.Boolean(
        related='company_id.auto_invoice_post',
        readonly=False
    )
    group_cash_close = fields.Boolean(
        "Cash Accounting Close",
        implied_group='smartest_payment_cash.group_cash_close'
    )
    cash_close_account_id = fields.Many2one(
        "account.account",
        related='company_id.cash_close_account_id',
        readonly=False
    )
    cash_close_journal_id = fields.Many2one(
        "account.journal",
        related='company_id.cash_close_journal_id',
        readonly=False
    )

    @api.onchange('auto_reconciliation')
    def _onchange_auto_reconciliation(self):
        """
        If the user chose to check the auto_reconciliation option, we set automatically the option
        auto_invoice_post as True to avoid generating error when trying to reconcile payment with a draft invoice.
        """
        if self.auto_reconciliation:
            self.auto_invoice_post = True

    @api.onchange('auto_invoice_post')
    def _onchange_auto_invoice_post(self):
        """
        If the user chose to uncheck the auto_invoice_post option, we set automatically the option
        auto_reconciliation as False to avoid generating error when trying to reconcile payment with a draft invoice.
        """
        if not self.auto_invoice_post:
            self.auto_reconciliation = False
