# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CashStatmentResPartner(models.Model):
    _inherit = 'res.partner'

    is_employee = fields.Boolean(
        'Employee',
    )  # This field is used to indicate if this partner is a employee instead of using default odoo mechanism

    @api.onchange('partner_account_group_id')
    def _onchange_partner_account_group_id(self):
        if self.is_employee or self.is_supplier and self.is_customer:
            self.property_account_receivable_id = self.partner_account_group_id.customer_account_id
            self.property_account_payable_id = self.partner_account_group_id.supplier_account_id
        else:
            if self.is_customer:
                self.property_account_receivable_id = self.partner_account_group_id.customer_account_id
            elif self.is_supplier:
                self.property_account_payable_id = self.partner_account_group_id.supplier_account_id