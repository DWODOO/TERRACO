import pdb

from odoo import models


class CurrencyImport(models.Model):
    _inherit = "res.currency"

    def _convert_purchase(self, from_amount, to_currency, company, rate, round=True):
        """Returns the converted amount of ``from_amount``` from the currency
           ``self`` to the currency ``to_currency`` for the given ``date`` and
           company.

           :param company: The company from which we retrieve the convertion rate
           :param date: The nearest date from which we retriev the conversion rate.
           :param round: Round the result or not
        """
        self, to_currency = self or to_currency, to_currency or self
        assert self, "convert amount from unknown currency"
        assert to_currency, "convert amount to unknown currency"
        assert company, "convert amount from unknown company"
        assert rate, "convert amount without rate"
        # apply conversion rate
        if self == to_currency:
            to_amount = from_amount
        else:
            to_amount = from_amount * rate
        # apply rounding
        return to_currency.round(to_amount) if round else to_amount
