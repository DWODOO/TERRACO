# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class SmartestFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    property_account_receivable_id = fields.Many2one('account.account', string="Customer Account")

    def check_fiscal_position_configuration(self):
        for position in self:
            if not position.tax_ids and not position.account_ids:
                return {
                    'warning': {
                        'title': _('Warning !'),
                        'message': _(
                            f"Please Make sure to configure the Fiscal Position. ({position.name})",
                        ),
                    }
                }