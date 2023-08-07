# -*- coding: utf-8 -*-
import logging
from datetime import date

from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class BilanReport(models.TransientModel):
    _name = 'amortissement.report'
    _description = 'Depreciation Report '

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        readonly=True,
        default=lambda self: self.env.user.company_id
    )
    date_from = fields.Date(
        string='Start Date',
        default=date.today().replace(day=1, month=1),
        required=True
    )
    date_to = fields.Date(
        string='End Date',
        default=date.today().replace(day=31, month=12),
        required=True
    )

    @api.model
    def _get_account_balance(self, accounts, date_from=None, date_to=None, mode=None):
        # Initialize domain
        domain = [
            ('move_id.state', '=', 'posted'),
            ('account_id', 'in', accounts.mapped('id')),
            ('date', '<=', date_to),
            ('date', '>=', date_from)
        ]

        # Search Journal entries
        line_ids = self.env['account.move.line'].search(domain)

        # If the mode is Credit
        if str(mode) == 'C':
            return sum(line_ids.mapped('credit'))

        # If the mode is Debit
        if str(mode) == 'D':
            return sum(line_ids.mapped('debit'))

        # If no mode defined then use the balance amount
        return sum(line_ids.mapped('balance'))

    @api.model
    def _get_amortissement_lines(self, date_from, date_to):
        env = self.env['account.account']

        goodwill_amort = [
            - self._get_account_balance(env.search([('code', '=like', '2807%')]), False, date_from),
            self._get_account_balance(env.search([('code', '=like', '2807%')]), date_from, date_to, 'C'),
            self._get_account_balance(env.search([('code', '=like', '2807%')]), date_from, date_to, 'D'),
            - self._get_account_balance(env.search([('code', '=like', '2807%')]), False, date_to),
        ]

        immo_incorp_amort = [
            - self._get_account_balance(env.search([('code', '=like', '280%'), '!', ('code', '=like', '2807%')]), False,
                                        date_from),
            self._get_account_balance(env.search([('code', '=like', '280%'), '!', ('code', '=like', '2807%')]),
                                      date_from, date_to, 'C'),
            self._get_account_balance(env.search([('code', '=like', '280%'), '!', ('code', '=like', '2807%')]),
                                      date_from, date_to, 'D'),
            - self._get_account_balance(env.search([('code', '=like', '280%'), '!', ('code', '=like', '2807%')]), False,
                                        date_to),
        ]

        immo_corp_amort = [
            - self._get_account_balance(env.search([('code', '=like', '281%')]), False, date_from),
            self._get_account_balance(env.search([('code', '=like', '281%')]), date_from, date_to, 'C'),
            self._get_account_balance(env.search([('code', '=like', '281%')]), date_from, date_to, 'D'),
            - self._get_account_balance(env.search([('code', '=like', '281%')]), False, date_to),
        ]

        participation_amort = [
            - self._get_account_balance(env.search([('code', '=like', '286%')]), False, date_from),
            self._get_account_balance(env.search([('code', '=like', '286%')]), date_from, date_to, 'C'),
            self._get_account_balance(env.search([('code', '=like', '286%')]), date_from, date_to, 'D'),
            - self._get_account_balance(env.search([('code', '=like', '286%')]), False, date_to),
        ]
        autre_actif_amort = [
            - self._get_account_balance(env.search([('code', '=like', '287%')]), False, date_from),
            self._get_account_balance(env.search([('code', '=like', '287%')]), date_from, date_to, 'C'),
            self._get_account_balance(env.search([('code', '=like', '287%')]), date_from, date_to, 'D'),
            - self._get_account_balance(env.search([('code', '=like', '287%')]), False, date_to),
        ]

        total = [
            goodwill_amort[0] + immo_incorp_amort[0] + immo_corp_amort[0] + participation_amort[0] + autre_actif_amort[
                0],
            goodwill_amort[1] + immo_incorp_amort[1] + immo_corp_amort[1] + participation_amort[1] + autre_actif_amort[
                1],
            goodwill_amort[2] + immo_incorp_amort[2] + immo_corp_amort[2] + participation_amort[2] + autre_actif_amort[
                2],
            goodwill_amort[3] + immo_incorp_amort[3] + immo_corp_amort[3] + participation_amort[3] + autre_actif_amort[
                3],
        ]

        return {
            'goodwill_amort': goodwill_amort,
            'immo_incorp_amort': immo_incorp_amort,
            'immo_corp_amort': immo_corp_amort,
            'participation_amort': participation_amort,
            'autre_actif_amort': autre_actif_amort,
            'total': total
        }

    def check_report(self):
        self.ensure_one()
        data = {
            'amortissement': self._get_amortissement_lines(self.date_from, self.date_to),
            'currency_id': self.company_id.currency_id,
            'current_year': self.date_from.year,
            'previous_year': self.date_from.year - 1,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'company': self.env.user.company_id.name,
        }
        return self.env.ref('smartest_l10n_dz.tableau_amortissement_report_action').report_action(self, data=data)
