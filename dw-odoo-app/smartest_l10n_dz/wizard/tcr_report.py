# -*- coding: utf-8 -*-
import re

from odoo import api, models, fields
import logging
from datetime import date
_logger = logging.getLogger(__name__)


class BilanReport(models.TransientModel):
    _name = "tcr.report"
    _description = "TCR Report"

    company_id = fields.Many2one('res.company', string='Company',readonly=True,default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string='Start Date', default=date.today().replace(day=1, month=1), required=True)
    date_to = fields.Date(string='End Date', default=date.today().replace(day=31, month=12), required=True)

    def get_account_balance(self, accounts,date_from=None,date_to=None,etat = None):
        if date_from:
            line_ids = self.env['account.move.line'].search([('move_id.state', '=', 'posted'),
                                                         ('date','<=',date_to),('date','>=',date_from),
                                                         ('account_id', 'in', accounts.mapped('id'))])
        else:
            line_ids = self.env['account.move.line'].search([('move_id.state', '=', 'posted'), ('date', '<=', date_to),
                                                             ('account_id', 'in', accounts.mapped('id'))])
        if str(etat) == 'C':
            return sum(line_ids.mapped('credit'))
        if str(etat) == 'D':
            return sum(line_ids.mapped('debit'))
        return sum(line_ids.mapped('balance'))
    def get_tcr_lines(self, date_from, date_to):
        env = self.env['account.account']
        vente_produit = self.get_account_balance(env.search([('code', '=like', '70%')]), date_from, date_to)
        variation_stock = self.get_account_balance(env.search([('code', '=like', '72%')]), date_from, date_to)
        production_immo = self.get_account_balance(env.search([('code', '=like', '73%')]), date_from, date_to)
        subvention_exploitation = self.get_account_balance(env.search([('code', '=like', '74%')]), date_from, date_to)
        achat_consomme = self.get_account_balance(env.search([('code', '=like', '60%')]), date_from, date_to)
        services = self.get_account_balance(env.search(['|',('code', '=like', '61%'),('code', '=like', '62%')]), date_from, date_to)
        charge_personnel = self.get_account_balance(env.search([('code', '=like', '63%')]), date_from, date_to)
        impot = self.get_account_balance(env.search([('code', '=like', '64%')]), date_from, date_to)
        autres_produits = self.get_account_balance(env.search([('code', '=like', '75%')]), date_from, date_to)
        autres_charges = self.get_account_balance(env.search([('code', '=like', '65%')]), date_from, date_to)
        dotation_ammo = self.get_account_balance(env.search([('code', '=like', '68%')]), date_from, date_to)
        reprise_perte = self.get_account_balance(env.search([('code', '=like', '78%')]), date_from, date_to)
        produits_finance = self.get_account_balance(env.search([('code', '=like', '76%')]), date_from, date_to)
        charges_finance = self.get_account_balance(env.search([('code', '=like', '66%')]), date_from, date_to)
        impots_exigibles = self.get_account_balance(env.search(['|',('code', '=like', '695'),('code', '=like', '698%')]), date_from, date_to)
        impots_diff = self.get_account_balance(env.search(['|',('code', '=like', '692'),('code', '=like', '693%')]), date_from, date_to)
        produit_extra = self.get_account_balance(env.search([('code', '=like', '77%')]), date_from, date_to)
        charge_extra = self.get_account_balance(env.search([('code', '=like', '67%')]), date_from, date_to)
        production_exercice = vente_produit + variation_stock + production_immo + subvention_exploitation
        consommation_exercice = achat_consomme + services
        val_exploitation = - production_exercice - consommation_exercice
        exe_brut = val_exploitation - charge_personnel - impot
        somme = - autres_produits - autres_charges - dotation_ammo - reprise_perte
        res_operation = exe_brut + somme
        res_financier = - produits_finance - charges_finance
        res_avant_impot = res_operation + res_financier
        total_produits = - vente_produit - variation_stock - production_immo - autres_produits - reprise_perte - produits_finance
        total_charges = achat_consomme + services + charge_personnel + impot + autres_charges + dotation_ammo + charges_finance + impots_exigibles + impots_diff
        res_net_activite = total_produits - total_charges
        res_extra = - produit_extra - charge_extra
        res_net_exercice = res_net_activite + res_extra
        return {

            'vente_produit': - vente_produit,
            'variation_stock': - variation_stock,
            'production_immo': - production_immo,
            'subvention_exploitation':- subvention_exploitation,
            'achat_consomme': achat_consomme,
            'services': services,
            'charge_personnel': charge_personnel,
            'impot': impot,
            'autres_produits': - autres_produits,
            'autres_charges': autres_charges,
            'dotation_ammo': dotation_ammo,
            'reprise_perte': - reprise_perte,
            'produits_finance': - produits_finance,
            'charges_finance': charges_finance,
            'impots_exigibles': impots_exigibles,
            'impots_diff': impots_diff,
            'produit_extra': - produit_extra,
            'charge_extra': charge_extra,
            'production_exercice': - production_exercice,
            'consommation_exercice': consommation_exercice,
            'val_exploitation': val_exploitation,
            'exe_brut': exe_brut,
            'res_operation': res_operation,
            'res_financier': res_financier,
            'res_avant_impot': res_avant_impot,
            'total_produits': total_produits,
            'total_charges': total_charges,
            'res_extra': res_extra,
            'res_net_activite': res_net_activite,
            'res_net_exercice': res_net_exercice

        }

    def check_report(self):
        self.ensure_one()
        data = {'current': self.get_tcr_lines(self.date_from, self.date_to),
                'previous': self.get_tcr_lines(self.date_from.replace(year=self.date_from.year - 1), self.date_to.replace(year=self.date_to.year - 1)),
                'currency_id': self.company_id.currency_id,
                'current_year': self.date_from.year,
                'previous_year': self.date_from.year - 1,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'company': self.env.user.company_id.name,
                }
        return self.env.ref('smartest_l10n_dz.tcr_report_dz_action').report_action(self, data=data)
