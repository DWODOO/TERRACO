# -*- coding: utf-8 -*-
from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    def set_to_close(self):
        """
        Override this method to implement Algerian Depreciation dispose
        """
        context = dict(self._context, close_entry=True)
        return super(AccountAsset, self.with_context(context)).set_to_close()
