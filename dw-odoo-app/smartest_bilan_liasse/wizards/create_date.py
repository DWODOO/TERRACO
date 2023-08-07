# -*- coding: utf-8 -*-
import base64
import pathlib
import pdb

from odoo import models, fields, api
from fillpdf import fillpdfs
import PyPDF2 as pypdf
import json
import os
import re
from datetime import date, datetime


def get_path(specification):
    path = pathlib.Path(__file__).parent.resolve()
    path_list = str(path).split('/')
    if specification =='module':
        paths = '/'.join(map(str, path_list[:-1]))
    else:
        paths = '/'.join(map(str, path_list[:-4]))
    return paths


class SmartestReport(models.TransientModel):
    _name = 'create.report.wizard'

    document = fields.Binary(string="Document",readonly=True)
    name = fields.Selection([
        ('TCR', 'Compte Resultat'),
        ('BA', 'Bilan Actif'),
        ('BP', 'Bilan Passif'),
        ('MSP', 'Etat 01_02'),
        ('COP', 'Etat 03_04'),
        ('TMV', 'Etat 05_06'),
        ('TI', 'Etat 07_08'),
    ], required=True, default='TCR')

    date = fields.Selection(selection=lambda self: self.dynamic_selection(),default=datetime.today().year,required=True,string="Année")

    def dynamic_selection(self):
        year = datetime.today().year
        YEARS = [year - i for i in range(10)]
        select = []
        for rec in YEARS:
            select = select + [(rec, rec)]
        return select


    def get_street(self,obj):
        adress = ''
        if obj.street:
           adress += str(obj.street)

        if obj.street2:
           adress += ' '+str(obj.street2)


        if obj.street :
           adress += ' '+str(obj.city)

        return adress

    def init_doc(self):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        test_sum = self.env['res.company'].search(
            [],limit=1)
        adress = self.get_street(test_sum)
        if self.name == 'TCR':
            annee = int(self.date)
            test999 = annee
            data_dict = {
                'NIF': test_sum.fiscal_identification,
                'Exercice du' : '01/01/'+self.date,
                'au': '31/12/'+self.date,
                'Des_entreprise' : test_sum.name,
                'Adresse' : adress
            }
            fillpdfs.write_fillable_pdf(
                get_path('module')+'/report/compte_res.pdf',
                path + '/compte_res.pdf',
                data_dict
                )
            self.env['account.move.line'].compute_TCR(annee)
            file = open(path+"/compte_res.pdf", "rb")
            out = file.read()
            file.close()
            self.document = base64.b64encode(out)
            self.total_tcr(path)

        if self.name == 'BA':
            annee = int(self.date)
            data_dict = {
                'NIF': test_sum.fiscal_identification,
                'Exercice clos le': '31/12/' + self.date,
                'Des_entreprise': test_sum.name,
                'Adresse': adress
            }
            # pdb.set_trace()
            fillpdfs.write_fillable_pdf(
                get_path('module')+'/report/BA.pdf',
                path+'/BA.pdf',
                data_dict
            )
            self.env['account.move.line'].bilan_actif(annee)
            file = open(path+"/BA.pdf", "rb")
            out = file.read()
            file.close()
            self.document = base64.b64encode(out)
            self.total_bilan_actif(path)

        if self.name == 'BP':
            annee = int(self.date)
            data_dict = {
                'NIF': test_sum.fiscal_identification,
                'Exercice clos le': '31/12/' + self.date,
                'Des_entreprise': test_sum.name,
                'Adresse': adress
                # 'p': 10,
                # 's': 10,
            }
            fillpdfs.write_fillable_pdf(
                get_path('module')+'/report/BP.pdf',
                path+'/BP.pdf', data_dict
            )
            self.env['account.move.line'].bilan_passif(annee)

            file = open(path+"/BP.pdf", "rb")
            out = file.read()
            file.close()
            self.document = base64.b64encode(out)
            self.total_bilan_passif(path)
        date_test = str(self.date)+'-'+'12'+'-'+'31'
        datetime_test = datetime.strptime(date_test,'%Y-%m-%d')

        if self.name == 'TMV':
            annee = int(self.date)
            data_dict = {
                'NIF': test_sum.fiscal_identification,
                'Exercice': '01/01/' + str(self.date),
                'au': '31/12/' + str(self.date),
                'Des_entreprise': test_sum.name,
                'Adresse': adress

            }
            fillpdfs.write_fillable_pdf(
                get_path('module')+'/report/etat6_5.pdf',
                path+'/etat6_5.pdf',
                data_dict
            )
            self.env['account.move.line'].compute_TMV(annee)

            file = open(
                path+"/etat6_5.pdf", "rb")
            out = file.read()
            file.close()
            self.document = base64.b64encode(out)
            self.total_TMV(path)
        # date_test = str(self.date)+'-'+'12'+'-'+'31'
        # datetime_test = datetime.strptime(date_test,'%Y-%m-%d')

        if self.name == 'TI':
            annee = int(self.date)
            data_dict = {
                'NIF': test_sum.fiscal_identification,
                'Exercice': '01/01/' + str(self.date),
                'au': '31/12/' + str(self.date),
                'Des_entreprise': test_sum.name,
                'Adresse': str(test_sum.street) + str(' ') + str(test_sum.street2) + str(' ') + str(test_sum.city),

            }
            fillpdfs.write_fillable_pdf(
                get_path('module')+'/report/etat7_8.pdf',
                path+'/etat7_8.pdf',
                data_dict
            )
            self.env['account.move.line'].compute_TI(annee)
            file = open(path+"/etat7_8.pdf", "rb")
            out = file.read()
            file.close()
            self.document = base64.b64encode(out)
            self.total_TI(path)

        if self.name == 'MSP':
            data_dict = {
                'NIF': test_sum.fiscal_identification,
                'Exercice': '01/01/' + str(self.date),
                'au': '31/12/' + str(self.date),
                'Des_entreprise': test_sum.name,
                'Adresse': str(test_sum.street) + str(' ') + str(test_sum.street2) + str(' ') + str(test_sum.city),
            }
            fillpdfs.write_fillable_pdf(
                get_path('module') + '/report/stock_table_1_2.pdf',
                path + '/stock_table_1_2.pdf',
                data_dict
            )
            annee = int(self.date)
            self.env['account.move.line'].compute_stock_table_1_2(annee)
            file = open(path+"/stock_table_1_2.pdf", "rb")
            out = file.read()
            file.close()
            self.document = base64.b64encode(out)

        if self.name == 'COP':
            data_dict = {
                'NIF': test_sum.fiscal_identification,
                'Exercice': '01/01/' + str(self.date),
                'au': '31/12/' + str(self.date),
                'Des_entreprise': test_sum.name,
                'Adresse': str(test_sum.street) + str(' ') + str(test_sum.street2) + str(' ') + str(test_sum.city),
            }
            fillpdfs.write_fillable_pdf(
                get_path('module') + '/report/charge_table_3_4.pdf',
                path + '/charge_table_3_4.pdf',
                data_dict
            )
            annee = int(self.date)
            self.env['account.move.line'].compute_charge_table_3_4(annee)
            file = open(path+"/charge_table_3_4.pdf", "rb")
            out = file.read()
            file.close()
            self.document = base64.b64encode(out)

        return {
            'name': ('Raport'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'create.report.wizard',
            'target': 'new',
            'res_id': self.id,
        }

    def total_TI(self, path):
        file = open(path+"/etat7_8.pdf", "rb")
        out = file.read()
        file.close()
        self.document = base64.b64encode(out)

    def total_TMV(self, path):
        file = open(path+"/etat6_5.pdf", "rb")
        out = file.read()
        pdf = pypdf.PdfFileReader(file)
        dics = pdf.getFormTextFields()

        # ------------------etat5

        total_credit_prece = int(self.empty_square(dics['DC_Goodwill'])) + int(self.empty_square(dics['DC_ii'])) + int(
            self.empty_square(dics['DC_p'])) + int(self.empty_square(dics['DC_aa'])) + int(
            self.empty_square(dics['DC_ic']))
        total_credit_actuel = int(self.empty_square(dics['DE_Goodwill'])) + int(self.empty_square(dics['DE_ii'])) + int(
            self.empty_square(dics['DE_p'])) + int(self.empty_square(dics['DE_aa'])) + int(
            self.empty_square(dics['DE_ic']))
        total_debit_actuel = int(self.empty_square(dics['DS_Goodwill'])) + int(self.empty_square(dics['DS_ii'])) + int(
            self.empty_square(dics['DS_p'])) + int(self.empty_square(dics['DS_aa'])) + int(
            self.empty_square(dics['DS_ic']))

        total_dfe = int(self.empty_square(dics['DFE_Goodwill'])) + int(self.empty_square(dics['DFE_ii'])) + int(
            self.empty_square(dics['DFE_p'])) + int(self.empty_square(dics['DFE_aa'])) + int(
            self.empty_square(dics['DFE_ic']))

        total_ligne1 = int(self.empty_square(dics['DS_Goodwill'])) + int(self.empty_square(dics['DC_Goodwill'])) + int(
            self.empty_square(dics['DE_Goodwill']))
        total_ligne2 = int(self.empty_square(dics['DC_ii'])) + int(self.empty_square(dics['DS_ii'])) + int(
            self.empty_square(dics['DE_ii']))
        total_ligne3 = int(self.empty_square(dics['DC_ic'])) + int(self.empty_square(dics['DS_ic'])) + int(
            self.empty_square(dics['DE_ic']))
        total_ligne4 = int(self.empty_square(dics['DC_p'])) + int(self.empty_square(dics['DS_p'])) + int(
            self.empty_square(dics['DE_p']))
        total_ligne5 = int(self.empty_square(dics['DC_aa'])) + int(self.empty_square(dics['DS_aa'])) + int(
            self.empty_square(dics['DE_aa']))
        total_lignes = total_ligne1 + total_ligne2 + total_ligne3 + total_ligne4 + total_ligne5

        sous_ligne1 = int(self.empty_square(dics['DE_Goodwill'])) - int(self.empty_square(dics['DFE_Goodwill']))
        sous_ligne2 = int(self.empty_square(dics['DE_ii'])) - int(self.empty_square(dics['DFE_ii']))
        sous_ligne3 = int(self.empty_square(dics['DE_ic'])) - int(self.empty_square(dics['DFE_ic']))
        sous_ligne4 = int(self.empty_square(dics['DE_p'])) - int(self.empty_square(dics['DFE_p']))
        sous_ligne5 = int(self.empty_square(dics['DE_aa'])) - int(self.empty_square(dics['DFE_aa']))

        # --------------------etat6

        montant_ligne1 = int(self.empty_square(dics['MB_Goodwill'])) - int(self.empty_square(dics['TVA_Goodwill']))
        montant_ligne2 = int(self.empty_square(dics['MB_ii'])) - int(self.empty_square(dics['TVA_ii']))
        montant_ligne3 = int(self.empty_square(dics['MB_ic'])) - int(self.empty_square(dics['TVA_ic']))
        montant_ligne4 = int(self.empty_square(dics['MB_p'])) - int(self.empty_square(dics['TVA_p']))
        montant_ligne5 = int(self.empty_square(dics['MB_aa'])) - int(self.empty_square(dics['TVA_aa']))

        total_mna = montant_ligne1 + montant_ligne2 + montant_ligne3 + montant_ligne4 + montant_ligne5

        total_debit_etat6 = int(self.empty_square(dics['MB_Goodwill'])) + int(self.empty_square(dics['MB_ii'])) + int(
            self.empty_square(dics['MB_ic'])) + int(self.empty_square(dics['MB_p'])) + int(
            self.empty_square(dics['MB_aa']))

        total_tva = int(self.empty_square(dics['TVA_Goodwill'])) + int(self.empty_square(dics['TVA_ii'])) + int(
            self.empty_square(dics['TVA_ic'])) + int(self.empty_square(dics['TVA_p'])) + int(
            self.empty_square(dics['TVA_aa']))

        total_sous = sous_ligne1 + sous_ligne2 + sous_ligne3 + sous_ligne4 + sous_ligne5
        file.close()
        data_dict = {
            'TOTAL_DC': (f'{int(total_credit_prece):,}').replace(",", " "),
            'TOTAL_DE': (f'{int(total_credit_actuel):,}').replace(",", " "),
            'TOTAL_DS': (f'{int(total_debit_actuel):,}').replace(",", " "),
            'DF_Goodwill': (f'{int(total_ligne1):,}').replace(",", " "),
            'DF_ii': (f'{int(total_ligne2):,}').replace(",", " "),
            'DF_ic': (f'{int(total_ligne3):,}').replace(",", " "),
            'DF_p': (f'{int(total_ligne4):,}').replace(",", " "),
            'DF_aa': (f'{int(total_ligne5):,}').replace(",", " "),
            'TOTAL DC': (f'{int(total_lignes):,}').replace(",", " "),
            'TOTAL_DFE': (f'{int(total_dfe):,}').replace(",", " "),
            'EC_Goodwill': (f'{int(sous_ligne1):,}').replace(",", " "),
            'EC_ii': (f'{int(sous_ligne2):,}').replace(",", " "),
            'EC_ic': (f'{int(sous_ligne3):,}').replace(",", " "),
            'EC_p': (f'{int(sous_ligne4):,}').replace(",", " "),
            'EC_aa': (f'{int(sous_ligne5):,}').replace(",", " "),
            'TOTAL_EC': (f'{int(total_sous):,}').replace(",", " "),
            'TOTAL_MB': (f'{int(total_debit_etat6):,}').replace(",", " "),
            'MNA_Goodwill': (f'{int(montant_ligne1):,}').replace(",", " "),
            'MNA_ii': (f'{int(montant_ligne2):,}').replace(",", " "),
            'MNA_ic': (f'{int(montant_ligne3):,}').replace(",", " "),
            'MNA_p': (f'{int(montant_ligne4):,}').replace(",", " "),
            'MNA_aa': (f'{int(montant_ligne5):,}').replace(",", " "),
            'TOTAL_MNA': (f'{int(total_mna):,}').replace(",", " "),
            'TOTAL_TVA': (f'{int(total_tva):,}').replace(",", " "),

        }
        fillpdfs.write_fillable_pdf(
            path+'/etat6_5.pdf',
            path+'/etat6_5.pdf',
            data_dict)

        file = open(path+"/etat6_5.pdf", "rb")
        out = file.read()
        file.close()
        self.document = base64.b64encode(out)
        os.remove(path+"/etat6_5.pdf")

    def remove_comma(self,dict):
        return re.sub(" ","",(dict))

    def total_tcr(self, path):
        file = open(path+"/compte_res.pdf", "rb")
        out = file.read()
        pdf = pypdf.PdfFileReader(file)
        dics = pdf.getFormTextFields()

        my_field_value = sum([int(self.empty_square(dics['v'])), int(self.empty_square(dics['v1'])),
                            int(self.empty_square(dics['v2'])), int(self.empty_square(dics['v3'])),
                            int(self.empty_square(dics['v4']))]) - int(self.empty_square(dics['z']))

        my_field_valueN_1 = sum([int(self.empty_square(dics['bb'])), int(self.empty_square(dics['bb1'])),
                                int(self.empty_square(dics['bb2'])), int(self.empty_square(dics['bb3'])),
                                 int(self.empty_square(dics['bb4']))]) - int(self.empty_square(dics['aa']))

        production_exercice = int(self.empty_square(dics['dd'])) + int(self.empty_square(dics['dd1'])) \
                              + int(self.empty_square(dics['dd2'])) + my_field_value - int(self.empty_square(dics['cc']))

        production_exercice_1 = int(self.empty_square(dics['ff'])) + int(self.empty_square(dics['ff1'])) + \
                                int(self.empty_square(dics['ff2'])) + my_field_valueN_1 - int(self.empty_square(dics['ee']))

        consomation_exercice = int(self.empty_square(dics['mm'])) + int(self.empty_square(dics['mm1'])) + int(self.empty_square(dics['mm2']))  + \
                               int(self.empty_square(dics['mm3'])) + int(self.empty_square(dics['mm4'])) + int(self.empty_square(dics['mm5'])) + \
                               int(self.empty_square(dics['mm6']))  + int(self.empty_square(dics['mm7'])) + int(self.empty_square(dics['mm8'])) + \
                               int(self.empty_square(dics['mm9'])) + int(self.empty_square(dics['mm10']))  + int(self.empty_square(dics['mm11'])) + \
                               int(self.empty_square(dics['mm12'])) + int(self.empty_square(dics['mm13'])) + int(self.empty_square(dics['mm14']))  - \
                               int(self.empty_square(dics['ab1'])) - int(self.empty_square(dics['ab3'])) - int(self.empty_square(dics['ab5']))

        consomation_exercice_1 = int(self.empty_square(dics['ab'])) + int(self.empty_square(dics['aab1'])) + int(self.empty_square(dics['ab2']))  + \
                                 int(self.empty_square(dics['dd3'])) + int(self.empty_square(dics['dd4'])) + int(self.empty_square(dics['dd5'])) + \
                                 int(self.empty_square(dics['dd6']))  + int(self.empty_square(dics['dd7'])) + int(self.empty_square(dics['dd8'])) + \
                                 int(self.empty_square(dics['dd9'])) + int(self.empty_square(dics['dd10']))  + int(self.empty_square(dics['dd11'])) + \
                                 int(self.empty_square(dics['dd12'])) + int(self.empty_square(dics['dd13'])) + int(self.empty_square(dics['dd14']))  - \
                                 int(self.empty_square(dics['ccm'])) - int(self.empty_square(dics['ab4'])) - int(self.empty_square(dics['ab6']))

        valeur_ajoute = production_exercice - consomation_exercice
        valeur_ajoute_1 =  production_exercice_1 - consomation_exercice_1

        if my_field_valueN_1 == 0:
            valeur_ajoute_1 = 0
        if my_field_value == 0:
            valeur_ajoute = 0

        excedent_brut = valeur_ajoute - int(self.empty_square(dics['cp'])) - int(self.empty_square(dics['cp1']))
        excedent_brut_1 = valeur_ajoute_1 - int(self.empty_square(dics['cp4'])) - int(self.empty_square(dics['cp5']))

        if valeur_ajoute == 0:
            excedent_brut = 0
        if valeur_ajoute_1 == 0:
            excedent_brut_1 = 0

        resultat_operation = excedent_brut - int(self.empty_square(dics['zz'])) - int(self.empty_square(dics['zz1'])) + \
                             int(self.empty_square(dics['yy']))  + int(self.empty_square(dics['yy1']))

        resultat_operation_1 = excedent_brut_1 - int(self.empty_square(dics['sw'])) - int(self.empty_square(dics['sw1']))+ \
                               int(self.empty_square(dics['sb']))  + int(self.empty_square(dics['sb1']))


        if excedent_brut == 0:
            resultat_operation = 0
        if excedent_brut_1 == 0:
            resultat_operation_1 = 0

        resultat_ordinaire = resultat_operation + int(self.empty_square(dics['am']))  - int(self.empty_square(dics['am2']))
        resultat_ordinaire_1 = resultat_operation_1 + int(dics['am1'])  - int(dics['am3'])

        resultat_extra_ordinaire = resultat_ordinaire - int(self.empty_square(dics['aam2'])) + int(self.empty_square(dics['aam']))
        resultat_extra_ordinaire_1 = resultat_ordinaire_1 - int(self.empty_square(dics['aam3'])) + int(self.empty_square(dics['aam1']))

        resultat_net =  resultat_extra_ordinaire + sum([int(self.empty_square(dics['kk'])),
                        int(self.remove_comma(dics['kk1']))]) - int(self.empty_square(dics['kk10']))
        resultat_net_1 =  resultat_extra_ordinaire_1 + sum([int(self.empty_square(dics['kk2'])),
                          int(self.empty_square(dics['kk3']))]) - int(self.empty_square(dics['kk20']))

        if resultat_ordinaire == 0:
            resultat_net = 0
        if resultat_ordinaire_1 == 0:
            resultat_net_1 = 0

        file.close()
        data_dict = {
            'can': (f'{int(my_field_value):,}').replace(",", " "),
            'can-1': (f'{int(my_field_valueN_1):,}').replace(",", " "),
            'pen': (f'{int(production_exercice):,}').replace(",", " "),
            'pen-1': (f'{int(production_exercice_1):,}').replace(",", " "),
            'cen': (f'{int(consomation_exercice):,}').replace(",", " "),
            'cen-1': (f'{int(consomation_exercice_1):,}').replace(",", " "),
            'vaen': (f'{int(valeur_ajoute):,}').replace(",", " "),
            'vaen-1': (f'{int(valeur_ajoute_1):,}').replace(",", " "),
            'eben': (f'{int(excedent_brut):,}').replace(",", " "),
            'eben-1': (f'{int(excedent_brut_1):,}').replace(",", " "),
            'ron': (f'{int(resultat_operation):,}').replace(",", " "),
            'ron-1': (f'{int(resultat_operation_1):,}').replace(",", " "),
            'rorn': (f'{int(resultat_ordinaire):,}').replace(",", " "),
            'rorn-1': (f'{int(resultat_ordinaire_1):,}').replace(",", " "),
            'ren': (f'{int(resultat_extra_ordinaire):,}').replace(",", " "),
            'ren_1': (f'{int(resultat_extra_ordinaire_1):,}').replace(",", " "),
            'rnn': (f'{int(resultat_net):,}').replace(",", " "),
            'rnn-1': (f'{int(resultat_net_1):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            path+'/compte_res.pdf',
            path+'/compte_res.pdf',
            data_dict)

        file = open(path+"/compte_res.pdf", "rb")
        out = file.read()
        pdf = pypdf.PdfFileReader(file)
        dics = pdf.getFormTextFields()
        file.close()

        for rec in dics:
            if len(rec) < 5 and dics[rec] != None:
                xyz = self.remove_comma(dics[rec])
                indice = dics[rec].find('.')
                car = dics[rec][indice:]
                if indice != -1:
                    dics[rec] = dics[rec].replace(car, '')

            if dics[rec] == '0' or dics[rec] == None:
                dics[rec] = ''

        fillpdfs.write_fillable_pdf(
            path+'/compte_res.pdf',
            path+'/compte_res.pdf',
            dics)
        file = open(path+"/compte_res.pdf", "rb")
        out = file.read()
        pdf = pypdf.PdfFileReader(file)
        dics = pdf.getFormTextFields()
        file.close()
        self.document = base64.b64encode(out)
        os.remove(path+"/compte_res.pdf")

    def empty_square(self,x):
        if x is None:
            return 0
        else:
            return float(self.remove_comma(x))

    def test_int(self,x):
        if x is None:
            return 0
        else:
            return int(self.remove_comma(x))

    def total_bilan_passif(self, path):
        file = open(path+"/BP.pdf", "rb")
        out = file.read()
        pdf = pypdf.PdfFileReader(file)
        dics = pdf.getFormTextFields()

        total1 = self.empty_square(dics['g']) + self.empty_square(dics['g1']) + self.empty_square(dics['g2']) + \
                 self.empty_square(dics['g3']) + self.empty_square(dics['g4']) + self.empty_square(dics['g5']) + \
                 self.empty_square(dics['g6']) + self.empty_square(dics['g7']) + self.empty_square(dics['g8'])

        total1_1 = self.empty_square(dics['m']) + self.empty_square(dics['m1']) + self.empty_square(dics['m2']) + \
                   self.empty_square(dics['m3']) + self.empty_square(dics['m4']) + self.empty_square(dics['m5']) + \
                   self.empty_square(dics['m6']) + self.empty_square(dics['m7']) + self.empty_square(dics['m8'])

        total2 = self.empty_square(dics['n']) + self.empty_square(dics['n1']) + self.empty_square(dics['n2']) + \
                 self.empty_square(dics['n3'])

        total2_1 = self.empty_square(dics['o']) + self.empty_square(dics['o1']) + self.empty_square(dics['o2']) + \
                   self.empty_square(dics['o3'])

        total3 = self.empty_square(dics['p']) + self.empty_square(dics['p1']) + self.empty_square(dics['p2']) + \
                 self.empty_square(dics['p3'])

        total3_1 = self.empty_square(dics['s']) + self.empty_square(dics['s1']) + self.empty_square(dics['s2']) + \
                   self.empty_square(dics['s3'])

        total_passif = total1 + total2 + total3
        total_passif_1 = total1_1 + total2_1 + total3_1

        file.close()
        data_dict = {
            't1': (f'{int(total1):,}').replace(",", " "),
            't1-1': (f'{int(total1_1):,}').replace(",", " "),
            't2': (f'{int(total2):,}').replace(",", " "),
            't2-1': (f'{int(total2_1):,}').replace(",", " "),
            't3': (f'{int(total3):,}').replace(",", " "),
            't3-1': (f'{int(total3_1):,}').replace(",", " "),
            'tp': (f'{int(total_passif):,}').replace(",", " "),
            'tp-1': (f'{int(total_passif_1):,}').replace(",", " "),

        }
        fillpdfs.write_fillable_pdf(
            path+'/BP.pdf',
            path+'/BP.pdf',
            data_dict)

        file = open(path+"/BP.pdf", "rb")
        out = file.read()
        pdf = pypdf.PdfFileReader(file)
        dics = pdf.getFormTextFields()
        file.close()

        for rec in dics:
            if len(rec) < 5 and dics[rec] != None:
                xyz = self.remove_comma(dics[rec])
                indice = dics[rec].find('.')
                car = dics[rec][indice:]
                if indice != -1:
                    dics[rec] = dics[rec].replace(car, '')
            if dics[rec] == '0' or dics[rec] == None:
                dics[rec] = ''

        fillpdfs.write_fillable_pdf(
            path+'/BP.pdf',
            path+'/BP.pdf',
            dics)
        file = open(path+"/BP.pdf", "rb")
        out = file.read()
        pdf = pypdf.PdfFileReader(file)
        dics = pdf.getFormTextFields()
        file.close()

        self.document = base64.b64encode(out)

        os.remove(path+"/BP.pdf")

    def total_bilan_actif(self, path):
        file = open(path+"/BA.pdf", "rb")
        out = file.read()
        pdf = pypdf.PdfFileReader(file)
        dics = pdf.getFormTextFields()

        acart = self.empty_square(dics['a1']) - self.empty_square(dics['b1'])
        immobili_incor = self.empty_square(dics['a2']) - self.empty_square(dics['b2'])
        terrain = self.empty_square(dics['a4']) - self.empty_square(dics['b4'])
        batim = self.empty_square(dics['a5']) - self.empty_square(dics['b5'])
        autre_immobili_incor = self.empty_square(dics['a6']) - self.empty_square(dics['b6'])
        immobili_concession = self.empty_square(dics['a7']) - self.empty_square(dics['b7'])
        immobili_cour = self.empty_square(dics['a8']) - self.empty_square(dics['b8'])
        titre = self.empty_square(dics['a10']) - self.empty_square(dics['b10'])
        autre_partici = self.empty_square(dics['a11']) - self.empty_square(dics['b11'])
        autre_titre = self.empty_square(dics['a12']) - self.empty_square(dics['b12'])
        pret_autre = self.empty_square(dics['a13']) - self.empty_square(dics['b13'])
        impot = self.empty_square(dics['a14']) - self.empty_square(dics['b14'])
        total_actif_non_circu_brut =  self.empty_square(dics['a1']) + self.empty_square(dics['a2']) + self.empty_square(dics['a4']) + \
                                      self.empty_square(dics['a5']) + self.empty_square(dics['a6']) + self.empty_square(dics['a7']) + \
                                      self.empty_square(dics['a8']) + self.empty_square(dics['a10']) + self.empty_square(dics['a11']) + \
                                      self.empty_square(dics['a12']) + self.empty_square(dics['a13']) + self.empty_square(dics['a14'])

        total_actif_non_circu_pert =  self.empty_square(dics['b1']) + self.empty_square(dics['b2']) + self.empty_square(dics['b4']) + \
                                      self.empty_square(dics['b5']) + self.empty_square(dics['b6']) + self.empty_square(dics['b7']) + \
                                      self.empty_square(dics['b8']) + self.empty_square(dics['b10']) + self.empty_square(dics['b11']) + \
                                      self.empty_square(dics['b12']) + self.empty_square(dics['b13']) + self.empty_square(dics['b14'])

        total_actif_non_circu_net = total_actif_non_circu_brut - total_actif_non_circu_pert

        stock_et_encours = self.empty_square(dics['e']) - self.empty_square(dics['f'])
        client = self.empty_square(dics['e2']) - self.empty_square(dics['f2'])
        autre_debiteurs = self.empty_square(dics['e3']) - self.empty_square(dics['f3'])
        impots_et_assimiles = self.empty_square(dics['e4']) - self.empty_square(dics['f4'])
        autre_creance = self.empty_square(dics['e5']) - self.empty_square(dics['f5'])
        placement = self.empty_square(dics['e7']) - self.empty_square(dics['f7'])
        tresorerie = self.empty_square(dics['e8']) - self.empty_square(dics['f8'])

        total_actif_courant_brut = self.empty_square(dics['e']) + self.empty_square(dics['e2']) + self.empty_square(dics['e3']) + \
                                   self.empty_square(dics['e4']) + self.empty_square(dics['e5']) + self.empty_square(dics['e7']) + \
                                   self.empty_square(dics['e8'])

        total_actif_courant_pert = self.empty_square(dics['f']) + self.empty_square(dics['f2']) + self.empty_square(dics['f3']) + \
                                   self.empty_square(dics['f4']) + self.empty_square(dics['f5']) + self.empty_square(dics['f7']) + \
                                   self.empty_square(dics['f8'])

        total_actif_courant_net = total_actif_courant_brut - total_actif_courant_pert

        total_actif_general_brut = total_actif_non_circu_brut + total_actif_courant_brut
        total_actif_general_perte = total_actif_non_circu_pert + total_actif_courant_pert
        total_actif_general_net =  total_actif_non_circu_net + total_actif_courant_net

        total_actif_non_circu_net_1 = self.empty_square(dics['d1']) + self.empty_square(dics['d2']) + self.empty_square(dics['d4']) + \
                                      self.empty_square(dics['d5']) + self.empty_square(dics['d6']) + self.empty_square(dics['d7']) + \
                                      self.empty_square(dics['d8']) + self.empty_square(dics['d10']) + self.empty_square(dics['d11']) + \
                                      self.empty_square(dics['d12']) + self.empty_square(dics['d13']) + self.empty_square(dics['d14'])

        total_actif_courant_net_1 = self.empty_square(dics['k']) + self.empty_square(dics['k2']) + self.empty_square(dics['k3']) + \
                                    self.empty_square(dics['k4']) + self.empty_square(dics['k5']) + self.empty_square(dics['k7']) + \
                                    self.empty_square(dics['k8'])

        total_g_net_1 = total_actif_non_circu_net_1 + total_actif_courant_net_1

        file.close()
        data_dict = {
            'c1': (f'{int(acart):,}').replace(",", " "),
            'c2': (f'{int(immobili_incor):,}').replace(",", " "),
            'c4': (f'{int(terrain):,}').replace(",", " "),
            'c5': (f'{int(batim):,}').replace(",", " "),
            'c6': (f'{int(autre_immobili_incor):,}').replace(",", " "),
            'c7': (f'{int(immobili_concession):,}').replace(",", " "),
            'c8': (f'{int(immobili_cour):,}').replace(",", " "),
            'c10': (f'{int(titre):,}').replace(",", " "),
            'c11': (f'{int(autre_partici):,}').replace(",", " "),
            'c12': (f'{int(autre_titre):,}').replace(",", " "),
            'c13': (f'{int(pret_autre):,}').replace(",", " "),
            'c14': (f'{int(impot):,}').replace(",", " "),

            'ncbrut': (f'{int(total_actif_non_circu_brut):,}').replace(",", " "),
            'ncperte': (f'{int(total_actif_non_circu_pert):,}').replace(",", " "),
            'ncnet': (f'{int(total_actif_non_circu_net):,}').replace(",", " "),

            'j': (f'{int(stock_et_encours):,}').replace(",", " "),
            'j2': (f'{int(client):,}').replace(",", " "),
            'j3': (f'{int(autre_debiteurs):,}').replace(",", " "),
            'j4': (f'{int(impots_et_assimiles):,}').replace(",", " "),
            'j5': (f'{int(autre_creance):,}').replace(",", " "),
            'j7': (f'{int(placement):,}').replace(",", " "),
            'j8': (f'{int(tresorerie):,}').replace(",", " "),

            'cbrut': (f'{int(total_actif_courant_brut):,}').replace(",", " "),
            'cpert': (f'{int(total_actif_courant_pert):,}').replace(",", " "),
            'cnet': (f'{int(total_actif_courant_net):,}').replace(",", " "),

            'gbrut': (f'{int(total_actif_general_brut):,}').replace(",", " "),
            'gpert': (f'{int(total_actif_general_perte):,}').replace(",", " "),
            'gnet': (f'{int(total_actif_general_net):,}').replace(",", " "),

            'ncnet-1': (f'{int(total_actif_non_circu_net_1):,}').replace(",", " "),
            'cnet-1': (f'{int(total_actif_courant_net_1):,}').replace(",", " "),
            'gnet-1': (f'{int(total_g_net_1):,}').replace(",", " "),

        }
        fillpdfs.write_fillable_pdf(
            path+'/BA.pdf',
            path+'/BA.pdf',
            data_dict)

        file = open(path+"/BA.pdf", "rb")
        out = file.read()
        pdf = pypdf.PdfFileReader(file)
        dics = pdf.getFormTextFields()
        file.close()

        for rec in dics:
            if len(rec) < 5 and dics[rec] != None:
                xyz = self.remove_comma(dics[rec])
                indice = dics[rec].find('.')
                car = dics[rec][indice:]
                if indice != -1:
                    dics[rec] = dics[rec].replace(car, '')
            if dics[rec] == '0' or dics[rec] == None:
                dics[rec] = ''

        fillpdfs.write_fillable_pdf(
            path+'/BA.pdf',
            path+'/BA.pdf',
            dics)
        file = open(path+"/BA.pdf", "rb")
        out = file.read()
        pdf = pypdf.PdfFileReader(file)
        dics = pdf.getFormTextFields()
        file.close()

        self.document = base64.b64encode(out)
        os.remove(path+"/BA.pdf")


