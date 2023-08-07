# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    auto_reconciliation = fields.Boolean(
        "Auto Reconciliation"
    )  # This field is used on res.config.setting TransitModel. If this field is checked, for this company, when closing
    # a cash.ticket, its related payment will be reconciled automatically with its related invoices.
    auto_invoice_post = fields.Boolean(
        "Auto Invoice Post"
    )  # This field is used on res.config.setting TransitModel. If this field is checked, for this company, when closing
    # a cash.ticket, its related draft invoices will be confirmed automatically.
    cash_close_account_id = fields.Many2one(
        "account.account",
        "Cash Close Account"
    )
    cash_close_journal_id = fields.Many2one(
        "account.journal",
        "Cash Close Journal"
    )
