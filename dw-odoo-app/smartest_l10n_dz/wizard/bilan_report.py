# -*- coding: utf-8 -*-
import re

from odoo import api, models, fields
import logging
from datetime import date
_logger = logging.getLogger(__name__)


class BilanReport(models.TransientModel):
    _name = "bilan.report"
    _description = "Account Bilan Report"

    company_id = fields.Many2one('res.company', string='Company',readonly=True,default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string='Start Date', default=date.today().replace(day=1, month=1),required=True)
    date_to = fields.Date(string='End Date', default=date.today().replace(day=31, month=12),required=True)

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
    def get_bilan_lines(self, date_from, date_to):
        env = self.env['account.account']
        goodwill = self.get_account_balance(env.search([('code','=like','207%')]),date_from,date_to)
        goodwill_amort = self.get_account_balance(env.search(['|',('code','=like','2807%'),('code','=like','2907%')]),date_from,date_to)
        immo_incorp = self.get_account_balance(env.search([('code','=like','20%'),'!',('code','=like','207%')]),date_from,date_to)
        immo_incorp_amort = self.get_account_balance(env.search(['|',('code', '=like', '280%'),('code', '=like', '290%'),'!', ('code', '=like', '2807%'), '!', ('code', '=like', '2907%')]),date_from, date_to)
        terrains = self.get_account_balance(env.search([('code', '=like', '211%')]),date_from, date_to)
        terrains_amort = self.get_account_balance(env.search(['|',('code', '=like', '2811%'),('code', '=like', '2911%')]),date_from, date_to)
        batiment = self.get_account_balance(env.search(['|',('code', '=like', '212%'),('code', '=like', '213%')]),date_from, date_to)
        batiment_amort = self.get_account_balance(env.search(['|', ('code', '=like', '2812%'),'|',('code', '=like', '2813%'),'|',('code', '=like', '2912%'), ('code', '=like', '2913%')]),date_from, date_to)
        autre_immo_corp = self.get_account_balance(env.search([('code', '=like', '21%'),'!',('code', '=like', '211%')
                                                              ,'!',('code', '=like', '212%'),'!',('code', '=like', '213%')]),date_from, date_to)
        autre_immo_corp_amort = self.get_account_balance(env.search([ '|',('code', '=like', '281%'),('code', '=like', '291%')
                                                                    , '!',('code', '=like', '2811%'),'!',('code', '=like', '2812%')
                                                                    , '!',('code', '=like', '2813%')
                                                                    , '!',('code', '=like', '2911%'),'!',('code', '=like', '2812%')
                                                                    , '!',('code', '=like', '2913%')
                                                                    , '!',('code', '=like', '213%')]),date_from, date_to)

        immo_concession = self.get_account_balance(env.search([('code', '=like', '22%')]),date_from, date_to)
        immo_concession_amort = self.get_account_balance(env.search(['|',('code', '=like', '282%'),('code', '=like', '292%')]),date_from, date_to)
        immo_encours = self.get_account_balance(env.search([('code', '=like', '23%')]),date_from, date_to)
        immo_encours_amort = self.get_account_balance(env.search([('code', '=like', '293%')]),date_from, date_to)
        titre_equi = self.get_account_balance(env.search([('code', '=like', '265%')]), date_from, date_to)
        titre_equi_amort = self.get_account_balance(env.search([('code', '=like', '2965%')]), date_from, date_to)
        autres_participation = self.get_account_balance(env.search([('code', '=like', '26%'),'!',('code', '=like', '265%')
                                                              ,'!',('code', '=like', '269%')]),date_from, date_to)
        autres_participation_amort = self.get_account_balance(env.search([('code', '=like', '296%'),'!',('code', '=like', '2965%'),'!',('code', '=like', '2969%')]),date_from, date_to)
        autre_titre = self.get_account_balance(env.search(['|',('code', '=like', '271%'),'|',('code', '=like', '272%'),('code', '=like', '273%')]),date_from, date_to)
        autre_titre_amort = self.get_account_balance(env.search(['|',('code', '=like', '2971%'),'|',('code', '=like', '2972%'),('code', '=like', '2973%')]),date_from, date_to)
        pret = self.get_account_balance(env.search(['|',('code', '=like', '274%'),'|',('code', '=like', '275%'),('code', '=like', '276%')]),date_from, date_to)
        pret_amort = self.get_account_balance(env.search(['|',('code', '=like', '2974%'),'|',('code', '=like', '2975%'),'|',('code', '=like', '2976%'),('code', '=like', '298%')]),date_from, date_to)
        impots_actif = self.get_account_balance(env.search([('code', '=like', '133%')]), date_from, date_to)
        impots_actif_amort = 0
        stock_encours = self.get_account_balance(env.search([('code', '=like', '3%'),'!',('code', '=like', '39%')]),date_from, date_to)
        stock_encours_amort = self.get_account_balance(env.search([('code', '=like', '39%')]),date_from, date_to)
        clients = self.get_account_balance(env.search([('code', '=like', '41%'),'!',('code', '=like', '419%')]),date_from, date_to)
        clients_amort = self.get_account_balance(env.search([('code', '=like', '491%')]),date_from, date_to)
        debit = self.get_account_balance(env.search(['|',('code', '=like', '42%'),'|',('code', '=like', '43%'),
                                                     '|', ('code', '=like', '441%'),'|',('code', '=like', '442%'),
                                                     '|', ('code', '=like', '443%'),'|',('code', '=like', '449%')
                                                     ,'|',('code', '=like', '45%'),'|',('code', '=like', '46%')
                                                     ,'|',('code', '=like', '486%'),('code', '=like', '489%')]),date_from, date_to , 'D')
        autre_debiteur = self.get_account_balance(env.search([('code', '=like', '409%')]),date_from, date_to) + debit
        autre_debiteur_amort = self.get_account_balance(env.search(['|',('code', '=like', '495%'),('code', '=like', '496%')]), date_from, date_to)
        impots_assim = self.get_account_balance(env.search(['|',('code', '=like', '444%'),'|',('code', '=like', '445%'),('code', '=like', '447%')]), date_from, date_to , 'D')
        impots_assim_amort = 0
        autre_creance = self.get_account_balance(env.search([('code', '=like', '48%'),'!',('code', '=like', '486%'),'!',('code', '=like', '489%')]), date_from, date_to , 'D')
        autre_creance_amort = 0
        placements_actif = self.get_account_balance(env.search([('code', '=like', '50%'),'!',('code', '=like', '509%')]), date_from, date_to)
        placements_actif_amort = 0
        debit = self.get_account_balance(env.search(['|', ('code', '=like', '51%'), ('code', '=like', '52%')]), date_from, date_to, 'D')
        tresorerie = debit + self.get_account_balance(env.search(['|', ('code', '=like', '53%'), ('code', '=like', '54%')]), date_from, date_to)
        tresorerie_amort = self.get_account_balance(env.search([('code', '=like', '59%')]), date_from, date_to)
        immo_corp = terrains + batiment + autre_immo_corp + immo_concession
        immo_corp_amort = terrains_amort + batiment_amort + autre_immo_corp_amort + immo_concession_amort
        immo_finance = titre_equi + autres_participation + autre_titre + pret + impots_actif
        immo_finance_amort = titre_equi_amort + autres_participation_amort + autre_titre_amort + pret_amort + impots_actif_amort
        actif_non_courant = immo_finance + immo_encours + immo_corp + immo_incorp + goodwill
        actif_non_courant_amort = immo_finance_amort + immo_encours_amort + immo_corp_amort + immo_incorp_amort + goodwill_amort
        creance_assim = clients + autre_debiteur + impots_assim + autre_creance
        creance_assim_amort = clients_amort + autre_debiteur_amort + impots_assim_amort + autre_creance_amort
        dispo_assim = placements_actif + tresorerie
        dispo_assim_amort = placements_actif_amort + tresorerie_amort
        actif_courant = dispo_assim + stock_encours + creance_assim
        actif_courant_amort = dispo_assim_amort + stock_encours_amort + creance_assim_amort
        total_actif= actif_courant + actif_non_courant
        total_actif_amort = actif_courant_amort + actif_non_courant_amort


        #  **************   PASSIF ********************

        capital_emis = self.get_account_balance(env.search(['|',('code', '=like', '101%'),('code', '=like', '108%')]), date_from, date_to)
        capital_non_app = self.get_account_balance(env.search([('code', '=like', '109%')]), date_from, date_to)
        prime = self.get_account_balance(env.search(['|', ('code', '=like', '104%'),('code', '=like', '106%')]), date_from, date_to)
        ecart_reeval = self.get_account_balance(env.search([('code', '=like', '105%')]), date_from, date_to)
        ecart_equi = self.get_account_balance(env.search([('code', '=like', '107%')]), date_from, date_to)
        resultat_net = self.get_account_balance(env.search([('code', '=like', '12%')]), date_from, date_to)
        autre_capitaux = self.get_account_balance(env.search([('code', '=like', '11%')]), date_from, date_to)
        emprunt_dette = self.get_account_balance(env.search(['|',('code', '=like', '16%'),('code', '=like', '17%')]), date_from, date_to)
        impot_diff = self.get_account_balance(env.search(['|',('code', '=like', '134%'),('code', '=like', '155%')]), date_from, date_to)
        autre_dette = self.get_account_balance(env.search([('code', '=like', '229%')]), date_from, date_to)
        provision_produit = self.get_account_balance(env.search(['|',('code', '=like', '15%'),'|',('code', '=like', '131%'),('code', '=like', '132%'),'!',('code', '=like', '155%')]), date_from, date_to)
        fournisseur = self.get_account_balance(env.search([('code', '=like', '40%'),'!',('code', '=like', '409%')]), date_from, date_to)
        impots_passif = - self.get_account_balance(env.search(['|',('code', '=like', '444%'),'|',('code', '=like', '445%'),('code', '=like', '447%')]), date_from, date_to , 'C')
        credit = self.get_account_balance(env.search([
            '|', ('code', '=like', '42%'),  '|', ('code', '=like', '43%'), '|', ('code', '=like', '440%'),
            '|', ('code', '=like', '441%'), '|', ('code', '=like', '442%'), '|', ('code', '=like', '443%'),
            '|', ('code', '=like', '448%'), '|', ('code', '=like', '449%'), '|', ('code', '=like', '45%'),
            '|', ('code', '=like', '46%'), ('code', '=like', '48%')]), date_from, date_to , 'C')
        autre_dette_passif = -credit + self.get_account_balance(env.search(['|', ('code', '=like', '419%'), ('code', '=like', '509%')]), date_from, date_to)
        credit = self.get_account_balance(env.search(['|', ('code', '=like', '51%'), ('code', '=like', '52%')]), date_from, date_to , 'C')
        tresorerie_passif = -credit
        capitaux_propres = capital_emis + capital_non_app + prime + ecart_reeval + ecart_equi + resultat_net + autre_capitaux
        passif_non_courant = emprunt_dette + impot_diff + autre_dette + provision_produit
        passif_courant = fournisseur + impots_passif + autre_dette_passif + tresorerie_passif
        total_passif = capitaux_propres + passif_non_courant + passif_courant

        return {

        'goodwill':goodwill,
        'goodwill_amort': - goodwill_amort,
        'immo_incorp':immo_incorp,
        'immo_incorp_amort': - immo_incorp_amort,
        'terrains':terrains,
        'terrains_amort': - terrains_amort,
        'batiment':batiment,
        'batiment_amort': - batiment_amort,
        'autre_immo_corp':autre_immo_corp,
        'autre_immo_corp_amort': - autre_immo_corp_amort,
        'immo_concession':immo_concession,
        'immo_concession_amort': - immo_concession_amort,
        'immo_encours':immo_encours,
        'immo_encours_amort': - immo_encours_amort,
        'titre_equi':titre_equi,
        'titre_equi_amort': - titre_equi_amort,
        'autres_participation':autres_participation,
        'autres_participation_amort': - autres_participation_amort,
        'autre_titre':autre_titre,
        'autre_titre_amort': - autre_titre_amort,
        'pret':pret,
        'pret_amort': - pret_amort,
        'impots_actif':impots_actif,
        'impots_actif_amort': - impots_actif_amort,
        'stock_encours':stock_encours,
        'stock_encours_amort': - stock_encours_amort,
        'clients':clients,
        'clients_amort': - clients_amort,
        'autre_debiteur':autre_debiteur,
        'autre_debiteur_amort': - autre_debiteur_amort,
        'impots_assim':impots_assim,
        'impots_assim_amort': - impots_assim_amort,
        'autre_creance':autre_creance,
        'autre_creance_amort': - autre_creance_amort,
        'placements_actif':placements_actif,
        'placements_actif_amort': - placements_actif_amort,
        'tresorerie':tresorerie,
        'tresorerie_amort': - tresorerie_amort,
        'capital_emis': - capital_emis,
        'capital_non_app': - capital_non_app,
        'prime': - prime,
        'ecart_reeval': - ecart_reeval,
        'ecart_equi': - ecart_equi,
        'resultat_net': - resultat_net,
        'autre_capitaux': - autre_capitaux,
        'emprunt_dette': - emprunt_dette,
        'impot_diff': - impot_diff,
        'autre_dette': - autre_dette,
        'provision_produit': - provision_produit,
        'fournisseur': - fournisseur,
        'impots_passif': - impots_passif,
        'autre_dette_passif': - autre_dette_passif,
        'tresorerie_passif': - tresorerie_passif,
        'immo_corp':immo_corp,
        'immo_corp_amort': - immo_corp_amort,
        'immo_finance':immo_finance,
        'immo_finance_amort': - immo_finance_amort,
        'creance_assim': creance_assim,
        'creance_assim_amort': -  creance_assim_amort,
        'dispo_assim': dispo_assim,
        'dispo_assim_amort': -  dispo_assim_amort,
        'actif_courant': actif_courant,
        'actif_courant_amort': -  actif_courant_amort,
        'actif_non_courant': actif_non_courant,
        'actif_non_courant_amort': -  actif_non_courant_amort,
        'total_actif':total_actif,
        'total_actif_amort': - total_actif_amort,
        'capitaux_propres':- capitaux_propres,
        'passif_non_courant':- passif_non_courant,
        'passif_courant': - passif_courant,
        'total_passif': - total_passif,
        }
    def check_report(self):
        self.ensure_one()
        data = {
                'current': self.get_bilan_lines(self.date_from, self.date_to),
                'previous': self.get_bilan_lines(self.date_from.replace(year=self.date_from.year - 1), self.date_to.replace(year=self.date_to.year - 1)),
                'currency_id': self.company_id.currency_id,
                'current_year': self.date_from.year,
                'previous_year': self.date_from.year - 1,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'company': self.env.user.company_id.name,
                }
        return self.env.ref('smartest_l10n_dz.actif_passif_report_action').report_action(self, data=data)
