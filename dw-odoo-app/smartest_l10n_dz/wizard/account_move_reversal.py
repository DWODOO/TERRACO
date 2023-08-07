# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    reversal_type = fields.Selection([
        ('reverse_debit_credit', 'Reverse Debit/Credit'),
        ('negative_debit_credit', 'Negative Debit/Credit'),
    ],
        string="Reversal Mode",
        default="negative_debit_credit"
    )

    def reverse_moves(self):
        context = dict(self._context, reversal_type=self.read(['reversal_type'])[0]['reversal_type'])
        return super(AccountMoveReversal, self.with_context(context)).reverse_moves()
