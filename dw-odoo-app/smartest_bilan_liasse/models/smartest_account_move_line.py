# -*- coding: utf-8 -*-
import base64
import pdb

import fillpdf
from odoo import models, fields, api
from fillpdf import fillpdfs
from datetime import date, datetime


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def credit_bilan_passif(self, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        date_reference = str(year) + '-' + '12' + '-' + '31'
        datetime_reference = datetime.strptime(date_reference, '%Y-%m-%d')

        query = ("""
        select   sum(a.credit-a.debit)   from account_move_line a inner join account_account b on (a.account_id=b.id)
        where a.date<= %(date)s and (b.code like '445%%' or b.code like '444%%' or b.code like '447%%') and a.parent_state='posted'
        group by b.code
        """)
        self.env.cr.execute(query, {'date': datetime_reference})
        # self.env.cr.execute('select case when sum(a.debit - a.credit) < 0 then sum(a.debit - a.credit) else 0 end '
        # 'from account_move_line a inner join account_account b on(a.account_id = b.id) where a.date <= \'%%%s%%\' '
        # 'and (b.code like \'445%\' or b.code like \'444%\' or b.code like \'447%\') group by b.code',tuple(x1))
        result = self.env.cr.fetchall()
        sum = 0
        for rec in result:
            if rec[0] > 0:
                sum += int(rec[0])
        return (sum)

    def debit_bilan_tcr(self, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        date_reference = str(year) + '-' + '12' + '-' + '31'
        date_reference_1 = str(year - 1) + '-' + '12' + '-' + '31'
        datetime_reference = datetime.strptime(date_reference, '%Y-%m-%d')
        datetime_reference_1 = datetime.strptime(date_reference_1, '%Y-%m-%d')

        query = ("""
        select   sum(a.debit-a.credit)   from account_move_line a inner join account_account b on (a.account_id=b.id)
        where a.date <= %(date)s and a.date > %(date_1)s and (b.code like '61%%' or b.code like '62%%') and a.parent_state='posted'
        group by b.code
        """)
        self.env.cr.execute(query, {'date': datetime_reference,
                                    'date_1': datetime_reference_1})

        result = self.env.cr.fetchall()
        sum = 0
        for rec in result:
            if rec[0] > 0:
                sum += int(rec[0])
        query = ("""
               select   sum(a.debit-a.credit)   from account_move_line a inner join account_account b on (a.account_id=b.id)
               where a.date <= %(date)s and a.date > %(date_1)s and (b.code like '611%%' or b.code like '613%%' or b.code like '615%%' or b.code like '616%%'
               or b.code like '621%%' or b.code like '623%%' or b.code like '625%%' or b.code like '622%%') and a.parent_state='posted'
               group by b.code
               """)
        self.env.cr.execute(query, {'date': datetime_reference,
                                    'date_1': datetime_reference_1})
        result = self.env.cr.fetchall()
        sub_sum = 0
        for rec in result:
            if rec[0] > 0:
                sub_sum += int(rec[0])

        return (sum - sub_sum)

    def credit_bilan_passif_autre_dettes(self, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        date_reference = str(year) + '-' + '12' + '-' + '31'
        datetime_reference = datetime.strptime(date_reference, '%Y-%m-%d')

        query = ("""
        select   sum(a.credit-a.debit)   from account_move_line a inner join account_account b on (a.account_id=b.id)
        where a.date<= %(date)s and (b.code like '42%%' or b.code like '43%%' or b.code like '440%%' 
        or b.code like '441%%' or b.code like '442%%' or b.code like '443%%' or b.code like '446%%' or b.code like '448%%' or b.code like '449%%'
        or b.code like '45%%' or b.code like '46%%' or b.code like '47%%' or b.code like '48%%' ) and a.parent_state='posted'
        group by b.code
        """)
        self.env.cr.execute(query, {'date': datetime_reference})
        # self.env.cr.execute('select case when sum(a.debit - a.credit) < 0 then sum(a.debit - a.credit) else 0 end '
        # 'from account_move_line a inner join account_account b on(a.account_id = b.id) where a.date <= \'%%%s%%\' '
        # 'and (b.code like \'445%\' or b.code like \'444%\' or b.code like \'447%\') group by b.code',tuple(x1))
        result = self.env.cr.fetchall()
        sum = 0
        for rec in result:
            if rec[0] > 0:
                sum += int(rec[0])
        return (sum)

    def credit_bilan_passif_tresorerie(self, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        date_reference = str(year) + '-' + '12' + '-' + '31'
        datetime_reference = datetime.strptime(date_reference, '%Y-%m-%d')

        query = ("""
        select   sum(a.credit-a.debit)   from account_move_line a inner join account_account b on (a.account_id=b.id)
        where a.date<= %(date)s and (b.code like '51%%' or b.code like '52%%' or b.code like '58%%' ) and a.parent_state='posted'
        group by b.code
        """)
        self.env.cr.execute(query, {'date': datetime_reference})
        result = self.env.cr.fetchall()
        sum = 0
        for rec in result:
            if rec[0] > 0:
                sum += int(rec[0])

        return (sum)

    def debit_bilan_actif(self, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        date_reference = str(year) + '-' + '12' + '-' + '31'
        datetime_reference = datetime.strptime(date_reference, '%Y-%m-%d')

        query = ("""
        select   sum(a.debit-a.credit)   from account_move_line a inner join account_account b on (a.account_id=b.id)
        where a.date<= %(date)s and (b.code like '445%%' or b.code like '444%%' or b.code like '447%%') and a.parent_state='posted'
        group by b.code
        """)
        self.env.cr.execute(query, {'date': datetime_reference})
        # self.env.cr.execute('select case when sum(a.debit - a.credit) < 0 then sum(a.debit - a.credit) else 0 end '
        # 'from account_move_line a inner join account_account b on(a.account_id = b.id) where a.date <= \'%%%s%%\' '
        # 'and (b.code like \'445%\' or b.code like \'444%\' or b.code like \'447%\') group by b.code',tuple(x1))
        result = self.env.cr.fetchall()
        sum = 0
        for rec in result:
            if rec[0] > 0:
                sum += int(rec[0])

        return (sum)

    def treasury_bilan_actif(self, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        date_reference = str(year) + '-' + '12' + '-' + '31'
        datetime_reference = datetime.strptime(date_reference, '%Y-%m-%d')

        query = ("""
        select   sum(a.debit-a.credit)   from account_move_line a inner join account_account b on (a.account_id=b.id)
        where a.date<= %(date)s and (b.code like '51%%' or b.code like '52%%' or b.code like '58%%') and a.parent_state='posted'
        group by b.code
        """)
        self.env.cr.execute(query, {'date': datetime_reference})
        result = self.env.cr.fetchall()
        sum = 0
        for rec in result:
            if rec[0] > 0:
                sum += int(rec[0])

        return (sum)

    def credit_bilan_activ_autre_debiteurs(self, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        date_reference = str(year) + '-' + '12' + '-' + '31'
        datetime_reference = datetime.strptime(date_reference, '%Y-%m-%d')

        query = ("""
        select   sum(a.debit-a.credit)   from account_move_line a inner join account_account b on (a.account_id=b.id)
        where a.date<= %(date)s and (b.code like '42%%' or b.code like '43%%' or b.code like '440%%' 
        or b.code like '441%%' or b.code like '442%%' or b.code like '443%%' or b.code like '446%%' or b.code like '448%%' or b.code like '449%%'
        or b.code like '45%%' or b.code like '46%%' or b.code like '47%%' or b.code like '486%%' or b.code like '489%%') and a.parent_state='posted'
        group by b.code
        """)
        self.env.cr.execute(query, {'date': datetime_reference})
        # self.env.cr.execute('select case when sum(a.debit - a.credit) < 0 then sum(a.debit - a.credit) else 0 end '
        # 'from account_move_line a inner join account_account b on(a.account_id = b.id) where a.date <= \'%%%s%%\' '
        # 'and (b.code like \'445%\' or b.code like \'444%\' or b.code like \'447%\') group by b.code',tuple(x1))
        result = self.env.cr.fetchall()
        sum = 0
        for rec in result:
            if rec[0] > 0:
                sum += int(rec[0])

        return (sum)

    def credit_bilan_activ_autre_creance(self, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        date_reference = str(year) + '-' + '12' + '-' + '31'
        datetime_reference = datetime.strptime(date_reference, '%Y-%m-%d')

        query = (""" 
        select   sum(a.debit-a.credit)   from account_move_line a inner join account_account b on (a.account_id=b.id)
        where a.date<= %(date)s and (b.code like '481%%' or b.code like '482%%' or b.code like '483%%' 
        or b.code like '484%%' or b.code like '485%%' or b.code like '487%%' or b.code like '488%%' or b.code like '480%%') and a.parent_state='posted'
        group by b.code
        """)
        self.env.cr.execute(query, {'date': datetime_reference})
        # self.env.cr.execute('select case when sum(a.debit - a.credit) < 0 then sum(a.debit - a.credit) else 0 end '
        # 'from account_move_line a inner join account_account b on(a.account_id = b.id) where a.date <= \'%%%s%%\' '
        # 'and (b.code like \'445%\' or b.code like \'444%\' or b.code like \'447%\') group by b.code',tuple(x1))
        result = self.env.cr.fetchall()
        sum = 0
        for rec in result:
            if rec[0] > 0:
                sum += int(rec[0])

        return (sum)

    def compute_sum(self, accounts, field_name, year, type_sum):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        if type(accounts) == list:
            x_sum = 0
            sum_total = 0
            credit_sum = 0
            debit_sum = 0
            for account in accounts:
                move_lines = self.env['account.move.line'].search(
                    [('account_id.code', 'like', account), ('parent_state', '=', 'posted'), ('date', 'like', year)])

                for line in move_lines:
                    if line.account_id.code[0:3] == str(account) or line.account_id.code[0:2] == str(account) or \
                            line.account_id.code[0:1] == str(account) or line.account_id.code[0:4] == str(account):
                        credit_sum += line.credit
                        debit_sum += line.debit

            if type_sum == 0:
                sum_total = credit_sum - debit_sum
                if sum_total < 0:
                    sum_total = 0
            if type_sum == 1:
                sum_total = debit_sum - credit_sum
                if sum_total < 0:
                    sum_total = 0
        else:
            move_lines = self.env['account.move.line'].search(
                [('account_id.code', 'like', accounts), ('parent_state', '=', 'posted'), ('date', 'like', year)])

            credit_sum = 0
            debit_sum = 0
            sum_total = 0
            for line in move_lines:

                if line.account_id.code[0:3] == str(accounts) or line.account_id.code[0:2] == str(accounts) or \
                        line.account_id.code[0:1] == str(accounts) or line.account_id.code[0:4] == str(accounts):
                    credit_sum += line.credit
                    debit_sum += line.debit

            if type_sum == 0:
                sum_total = credit_sum - debit_sum
                if sum_total < 0:
                    sum_total = 0
            if type_sum == 1:
                sum_total = debit_sum - credit_sum
                if sum_total < 0:
                    sum_total = 0

        data_dict = {
            field_name: (f'{int(sum_total):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            path + '/accounts_res.pdf',
            path + '/accounts_res.pdf',
            data_dict)
        return int(sum_total)

    def compute_sum_ba(self, accounts, field_name, year, type_sum):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        """
        if type_sum = 1 then debit else credit
        """
        date_reference = str(year) + '-' + '12' + '-' + '31'
        datetime_reference = datetime.strptime(date_reference, '%Y-%m-%d')
        # vente de marchandise
        if type(accounts) == list:
            x_sum = 0
            test99 = 0
            for account in accounts:
                move_lines = self.env['account.move.line'].search(
                    [('account_id.code', 'like', account), ('parent_state', '=', 'posted'),
                     ('date', '<=', datetime_reference)])
                y_sum = 0
                sold = 0
                for line in move_lines:
                    if line.account_id.code[0:3] == str(account) or line.account_id.code[0:2] == str(account) or \
                            line.account_id.code[0:1] == str(account) or line.account_id.code[0:4] == str(account):
                        sold = sold + line.debit - line.credit
                if type_sum == 1:
                    if sold > 0:
                        x_sum = x_sum + sold
                if type_sum == 0:
                    if sold < 0:
                        x_sum = x_sum + abs(sold)
                test99 = test99 + sold
        else:
            move_lines = self.env['account.move.line'].search(
                [('account_id.code', 'like', accounts), ('parent_state', '=', 'posted'),
                 ('date', '<=', datetime_reference)])
            x_sum = 0
            sold = 0
            for line in move_lines:
                if line.account_id.code[0:3] == str(accounts) or line.account_id.code[0:2] == str(accounts) or \
                        line.account_id.code[0:1] == str(accounts) or line.account_id.code[0:4] == str(accounts):
                    sold = sold + line.debit - line.credit
            if type_sum == 0:
                if sold < 0:
                    x_sum += abs(sold)
            elif type_sum == 1:
                if sold > 0:
                    x_sum += sold
        data_dict = {
            field_name: (f'{int(x_sum):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            path + '/BA.pdf',
            path + '/BA.pdf',
            data_dict)
        return int(x_sum)

    def compute_autres_services(self, field_name, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        accounts_liste = [611, 613, 615, 616, 621, 622, 623, 625]
        accounts_liste_sum = 0
        for account in accounts_liste:
            move_lines = self.env['account.move.line'].search(
                [('account_id.code', 'like', account), ('parent_state', '=', 'posted'), ('date', 'like', year)])
            y_sum = 0
            for line in move_lines:
                y_sum += line.debit - line.credit
            accounts_liste_sum += y_sum
        accounts_liste = [61, 62]
        accounts_liste_sum_61_62 = 0
        for account in accounts_liste:
            move_lines = self.env['account.move.line'].search(
                [('account_id.code', 'like', account), ('parent_state', '=', 'posted'), ('date', 'like', year)])
            y_sum = 0
            for line in move_lines:
                y_sum += line.debit - line.credit
            accounts_liste_sum_61_62 += y_sum
        total_sum = accounts_liste_sum_61_62 - accounts_liste_sum

        data_dict = {
            field_name: (f'{int(total_sum):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            path + '/accounts_res.pdf',
            path + '/accounts_res.pdf',
            data_dict)

    def compute_sold_bp(self, accounts, field_name, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        x_sum = 0
        date_reference = str(year) + '-' + '12' + '-' + '31'
        datetime_reference = datetime.strptime(date_reference, '%Y-%m-%d')

        if type(accounts) == list:
            # x_sum = 0
            for account in accounts:
                move_lines = self.env['account.move.line'].search(
                    [('account_id.code', 'like', account), ('parent_state', '=', 'posted'),
                     ('date', '<=', datetime_reference)])
                y_sum = 0
                for line in move_lines:
                    if line.account_id.code[0:3] == str(account) or line.account_id.code[0:2] == str(account) or \
                            line.account_id.code[0:1] == str(account) or line.account_id.code[0:4] == str(account):
                        if field_name == 'g5':
                            print(field_name, line.account_id.code)
                        y_sum += line.credit - line.debit
                x_sum = x_sum + y_sum
        else:
            move_lines = self.env['account.move.line'].search(
                [('account_id.code', 'like', accounts), ('parent_state', '=', 'posted'),
                 ('date', '<=', datetime_reference)])
            for line in move_lines:
                if line.account_id.code[0:3] == str(accounts) or line.account_id.code[0:2] == str(accounts) or \
                        line.account_id.code[0:1] == str(accounts) or line.account_id.code[0:4] == str(accounts):
                    x_sum += line.credit - line.debit

        data_dict = {
            field_name: (f'{int(x_sum):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            path + '/BP.pdf',
            path + '/BP.pdf',
            data_dict)
        return x_sum

    def compute_sold_ba(self, accounts, field_name, year, type_traitement):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        date_reference = str(year) + '-' + '12' + '-' + '31'
        datetime_reference = datetime.strptime(date_reference, '%Y-%m-%d')
        if type(accounts) == list:
            x_sum = 0
            for account in accounts:
                move_lines = self.env['account.move.line'].search(
                    [('account_id.code', 'like', (account)), ('parent_state', '=', 'posted'),
                     ('date', '<=', datetime_reference)])
                y_sum = 0
                for line in move_lines:
                    if line.account_id.code[0:3] == str(account) or line.account_id.code[0:2] == str(account) or \
                            line.account_id.code[0:1] == str(account) or line.account_id.code[0:4] == str(account):
                        y_sum += (line.debit - line.credit)
                x_sum += y_sum
        else:
            move_lines = self.env['account.move.line'].search(
                [('account_id.code', 'like', accounts), ('parent_state', '=', 'posted'),
                 ('date', '<=', datetime_reference)])
            x_sum = 0
            for line in move_lines:
                if line.account_id.code[0:3] == str(accounts) or line.account_id.code[0:2] == str(accounts) or \
                        line.account_id.code[0:4] == str(accounts) or line.account_id.code[0:1] == str(accounts):
                    x_sum += (line.debit - line.credit)
        zzz = abs(x_sum)
        if type_traitement == 0:
            data_dict = {
                field_name: (f'{(int((zzz))):,}').replace(",", " "),
            }
            fillpdfs.write_fillable_pdf(
                path + '/BA.pdf',
                path + '/BA.pdf',
                data_dict)
            return int(zzz)

        else:
            return int(zzz)

    def compute_autres_dettes_BP(self, field_name, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        date_reference = str(year) + '-' + '12' + '-' + '31'
        datetime_reference = datetime.strptime(date_reference, '%Y-%m-%d')
        accounts_sold = [419, 509]
        accounts_liste_sum = 0
        for account in accounts_sold:
            move_lines = self.env['account.move.line'].search(
                [('account_id.code', 'like', account), ('parent_state', '=', 'posted'),
                 ('date', '<=', datetime_reference)])
            y_sum = 0
            for line in move_lines:
                if line.account_id.code[0:3] == str(account) or line.account_id.code[0:2] == str(account) or \
                        line.account_id.code[0:1] == str(account) or line.account_id.code[0:4] == str(account):
                    y_sum += line.debit - line.credit
            accounts_liste_sum += y_sum

        accounts_credit = [42, 43, 440, 441, 442, 443, 446, 448, 449, 45, 46, 47, 48]
        for account in accounts_credit:
            move_lines = self.env['account.move.line'].search(
                [('account_id.code', 'like', account), ('parent_state', '=', 'posted'),
                 ('date', '<=', datetime_reference)])
            sold = 0
            y_sum = 0
            for line in move_lines:
                if line.account_id.code[0:3] == str(account) or line.account_id.code[0:2] == str(account) or \
                        line.account_id.code[0:1] == str(account) or line.account_id.code[0:4] == str(account):
                    sold = sold + line.credit - line.debit
            if sold > 0:
                y_sum += sold
            accounts_liste_sum += y_sum

        data_dict = {
            field_name: (f'{int(accounts_liste_sum):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            path + '/BP.pdf',
            path + '/BP.pdf',
            data_dict)

    def compute_sold_sub_accounts(self, accounts, sous_accounts, year, accounts_entier):
        date_reference = str(year) + '-' + '12' + '-' + '31'
        datetime_reference = datetime.strptime(date_reference, '%Y-%m-%d')
        total_sum = 0
        for index in range(len(accounts)):
            move_lines = self.env['account.move.line'].search(
                [('account_id.code', 'like', accounts[index]), ('parent_state', '=', 'posted'),
                 ('date', '<=', datetime_reference)])
            x_sum = 0
            for line in move_lines:
                if line.account_id.code[0:3] == str(accounts[index]) or line.account_id.code[0:2] == str(
                        accounts[index]) or \
                        line.account_id.code[0:1] == str(accounts[index]) or line.account_id.code[0:4] == str(
                    accounts[index]):
                    x_sum += line.credit - line.debit
            y_sum = 0
            if type(sous_accounts[index]) == list:
                for account in sous_accounts[index]:
                    move_lines = self.env['account.move.line'].search(
                        [('account_id.code', 'like', (account)), ('parent_state', '=', 'posted'),
                         ('date', '<=', datetime_reference)])
                    for line in move_lines:
                        if line.account_id.code[0:3] == str(account) or line.account_id.code[0:2] == str(account) or \
                                line.account_id.code[0:1] == str(account) or line.account_id.code[0:4] == str(
                            account):
                            y_sum += line.credit - line.debit

            total_sum += x_sum - y_sum
        if accounts_entier != 0:
            for account_entier in accounts_entier:
                move_lines = self.env['account.move.line'].search(
                    [('account_id.code', 'like', account_entier), ('parent_state', '=', 'posted'),
                     ('date', '<=', datetime_reference)])
                x_sum = 0
                for line in move_lines:
                    if line.account_id.code[0:3] == str(account_entier) or line.account_id.code[0:2] == str(
                            account_entier) or \
                            line.account_id.code[0:1] == str(account_entier) or line.account_id.code[0:4] == str(
                        account_entier):
                        x_sum += line.credit - line.debit
                total_sum += x_sum
        return abs(total_sum)

    def set_sub_accounts(self, value, field_name, pdf_var):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        data_dict = {
            field_name: (f'{int(value):,}').replace(",", " "),
        }
        # field_name: '{0:,}'.format(xx_sum).replace(',', ' '),
        fillpdfs.write_fillable_pdf(
            path + '/' + pdf_var + '.pdf',
            path + '/' + pdf_var + '.pdf',
            data_dict
        )

    def compute_sub_accounts_etat_cette_year(self, accounts, sous_accounts, year, testCD):
        date_reference = str(year) + '-' + '12' + '-' + '31'
        datetime_reference = datetime.strptime(date_reference, '%Y-%m-%d')
        total_sum_credit = 0
        total_sum_debit = 0
        for index in range(len(accounts)):
            move_lines = self.env['account.move.line'].search(
                [('account_id.code', 'like', accounts[index]), ('parent_state', '=', 'posted'),
                 ('date', 'like', datetime_reference)])
            x_sum_credit = 0
            x_sum_debit = 0
            for line in move_lines:
                if line.account_id.code[0:3] == str(accounts[index]) or line.account_id.code[0:2] == str(
                        accounts[index]) or \
                        line.account_id.code[0:1] == str(accounts[index]) or line.account_id.code[0:4] == str(
                    accounts[index]):
                    x_sum_credit += line.credit
            y_sum_credit = 0
            y_sum_debit = 0
            if type(sous_accounts[index]) == list:
                for account in sous_accounts[index]:
                    move_lines = self.env['account.move.line'].search(
                        [('account_id.code', 'like', (account)), ('parent_state', '=', 'posted'),
                         ('date', 'like', datetime_reference)])
                    for line in move_lines:
                        if line.account_id.code[0:3] == str(account) or line.account_id.code[0:2] == str(account) or \
                                line.account_id.code[0:1] == str(account) or line.account_id.code[0:4] == str(
                            account):
                            y_sum_credit += line.credit
                            y_sum_debit += line.debit
            total_sum_credit += x_sum_credit - y_sum_credit
            total_sum_debit += x_sum_debit - y_sum_debit
        if testCD == 0:
            return abs(total_sum_credit)

        if testCD == 1:
            return abs(total_sum_debit)

    def compute_sub_accounts_etat(self, accounts, sous_accounts, year, accounts_entier):
        date_reference = str(year) + '-' + '12' + '-' + '31'
        datetime_reference = datetime.strptime(date_reference, '%Y-%m-%d')
        total_sum = 0
        for index in range(len(accounts)):
            move_lines = self.env['account.move.line'].search(
                [('account_id.code', 'like', accounts[index]), ('parent_state', '=', 'posted'),
                 ('date', '<=', datetime_reference)])
            x_sum = 0
            for line in move_lines:
                if line.account_id.code[0:3] == str(accounts[index]) or line.account_id.code[0:2] == str(
                        accounts[index]) or \
                        line.account_id.code[0:1] == str(accounts[index]) or line.account_id.code[0:4] == str(
                    accounts[index]):
                    x_sum += line.credit
            y_sum = 0
            if type(sous_accounts[index]) == list:
                for account in sous_accounts[index]:
                    move_lines = self.env['account.move.line'].search(
                        [('account_id.code', 'like', (account)), ('parent_state', '=', 'posted'),
                         ('date', '<=', datetime_reference)])
                    for line in move_lines:
                        if line.account_id.code[0:3] == str(account) or line.account_id.code[0:2] == str(account) or \
                                line.account_id.code[0:1] == str(account) or line.account_id.code[0:4] == str(
                            account):
                            y_sum += line.credit

            total_sum += x_sum - y_sum
        if accounts_entier != 0:
            for account_entier in accounts_entier:
                move_lines = self.env['account.move.line'].search(
                    [('account_id.code', 'like', account_entier), ('parent_state', '=', 'posted'),
                     ('date', '<=', datetime_reference)])
                x_sum = 0
                for line in move_lines:
                    if line.account_id.code[0:3] == str(account_entier) or line.account_id.code[0:2] == str(
                            account_entier) or \
                            line.account_id.code[0:1] == str(account_entier) or line.account_id.code[0:4] == str(
                        account_entier):
                        x_sum += line.credit
                total_sum += x_sum
        return abs(total_sum)

    def set_sub_accounts_etat(self, value, field_name):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        data_dict = {
            field_name: (f'{int(value):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            path + '/etat6_5.pdf',
            path + '/etat6_5.pdf',
            data_dict)

    def compute_sum_etat56(self, accounts, field_name, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        date_reference = str(year) + '-' + '12' + '-' + '31'
        datetime_reference = datetime.strptime(date_reference, '%Y-%m-%d')
        if type(accounts) == list:
            credit_sum = 0
            debit_sum = 0
            for account in accounts:
                move_lines = self.env['account.move.line'].search(
                    [('account_id.code', 'like', account), ('parent_state', '=', 'posted'),
                     ('date', '<=', datetime_reference)])

                for line in move_lines:
                    if line.account_id.code[0:3] == str(account) or line.account_id.code[0:2] == str(account) or \
                            line.account_id.code[0:1] == str(account) or line.account_id.code[0:4] == str(account):
                        credit_sum += line.credit
                        debit_sum += line.debit
            sum_total = credit_sum
        else:
            move_lines = self.env['account.move.line'].search(
                [('account_id.code', 'like', accounts), ('parent_state', '=', 'posted'),
                 ('date', '<=', datetime_reference)])

            credit_sum = 0
            debit_sum = 0
            sum_total = 0
            for line in move_lines:

                if line.account_id.code[0:3] == str(accounts) or line.account_id.code[0:2] == str(accounts) or \
                        line.account_id.code[0:1] == str(accounts) or line.account_id.code[0:4] == str(accounts):
                    credit_sum += line.credit
                    debit_sum += line.debit
            sum_total = credit_sum
        data_dict = {
            field_name: (f'{int(sum_total):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            path + '/etat6_5.pdf',
            path + '/etat6_5.pdf',
            data_dict)
        return int(sum_total)

    def compute_sum_year_etat56(self, accounts, field_name, year, testCD):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        if type(accounts) == list:
            x_sum = 0
            sum_total = 0
            credit_sum = 0
            debit_sum = 0
            for account in accounts:
                move_lines = self.env['account.move.line'].search(
                    [('account_id.code', 'like', account), ('date', 'like', year)])

                for line in move_lines:
                    if line.account_id.code[0:3] == str(account) or line.account_id.code[0:2] == str(account) or \
                            line.account_id.code[0:1] == str(account) or line.account_id.code[0:4] == str(account):
                        credit_sum += line.credit
                        debit_sum += line.debit
            if testCD == 0:
                sum_total = credit_sum

            if testCD == 1:
                sum_total = debit_sum
        else:
            move_lines = self.env['account.move.line'].search(
                [('account_id.code', 'like', accounts), ('parent_state', '=', 'posted'), ('date', 'like', year)])

            credit_sum = 0
            debit_sum = 0
            sum_total = 0
            for line in move_lines:

                if line.account_id.code[0:3] == str(accounts) or line.account_id.code[0:2] == str(accounts) or \
                        line.account_id.code[0:1] == str(accounts) or line.account_id.code[0:4] == str(accounts):
                    credit_sum += line.credit
                    debit_sum += line.debit
            if testCD == 0:
                sum_total = credit_sum

            if testCD == 1:
                sum_total = debit_sum

        data_dict = {
            field_name: (f'{int(sum_total):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            path + '/etat6_5.pdf',
            path + '/etat6_5.pdf',
            data_dict)
        return int(sum_total)

    def compute_tva_sousaccounts_etat(self, accounts, sous_accounts, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        date_reference = str(year)
        datetime_reference = datetime.strptime(date_reference, '%Y')
        total = 0
        total_sous = 0
        total_accounts = 0
        list_tva = []
        for index in range(len(accounts)):
            move_lines = self.env['account.move.line'].search(
                [('account_id.code', 'like', accounts[index]), ('parent_state', '=', 'posted'), ('date', 'like', year)])
            x_sum = 0
            for line in move_lines:
                if line.account_id.code[0:3] == str(accounts[index]) or line.account_id.code[0:2] == str(
                        accounts[index]) or \
                        line.account_id.code[0:1] == str(accounts[index]) or line.account_id.code[0:4] == str(
                    accounts[index]):
                    move = self.env['account.move'].search(
                        [('payment_reference', 'like', line.move_id.payment_reference)])
                    for p in move.line_ids:
                        if p.account_id.code[0:3] == str('40457') or p.account_id.code[0:2] == str(
                                '40457') or p.account_id.code[0:1] == str('40457') or p.account_id.code[0:4] == str(
                            '40457'):

                            list_tva.append(move)
                            list_tva = list(set(list_tva))

                            for l in list_tva:
                                i = 0
                                for line in l.line_ids:
                                    if line.account_id.code[0:3] == str('40457') or line.account_id.code[0:2] == str(
                                            '40457') or line.account_id.code[0:1] == str(
                                        '40457') or line.account_id.code[0:4] == str('40457'):
                                        total_accounts = line.debit
                                        break
                                break

            if type(sous_accounts[index]) == list:
                for account in sous_accounts[index]:
                    move_lines = self.env['account.move.line'].search(
                        [('account_id.code', 'like', (account)), ('parent_state', '=', 'posted'),
                         ('date', 'like', year)])
                    for line in move_lines:
                        if line.account_id.code[0:3] == str(account) or line.account_id.code[0:2] == str(account) or \
                                line.account_id.code[0:1] == str(account) or line.account_id.code[0:4] == str(
                            account):
                            move = self.env['account.move'].search(
                                [('payment_reference', 'like', line.move_id.payment_reference)])
                            for p in move.line_ids:
                                if p.account_id.code[0:3] == str('40457') or p.account_id.code[0:2] == str(
                                        '40457') or p.account_id.code[0:1] == str('40457') or p.account_id.code[
                                                                                              0:4] == str(
                                    '40457'):

                                    list_tva.append(move)
                                    list_tva = list(set(list_tva))

                                    for l in list_tva:
                                        i = 0
                                        for line in l.line_ids:
                                            if line.account_id.code[0:3] == str('40457') or line.account_id.code[
                                                                                            0:2] == str(
                                                '40457') or line.account_id.code[0:1] == str(
                                                '40457') or line.account_id.code[0:4] == str('40457'):
                                                total_sous = line.debit

                                                break

                                        break
            total = total_accounts - total_sous
        return abs(total)

    def compute_tva_etat6_cette_year(self, accounts, field_name, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        date_reference = str(year)
        datetime_reference = datetime.strptime(date_reference, '%Y')
        total = 0
        list_tva = []
        print("test marche")
        if type(accounts) == list:
            for account in accounts:
                move_lines = self.env['account.move.line'].search(
                    [('account_id.code', 'like', account), ('parent_state', '=', 'posted'), ('date', 'like', year)])

                for line in move_lines:
                    if line.account_id.code[0:3] == str(account) or line.account_id.code[0:2] == str(
                            account) or line.account_id.code[0:1] == str(account) or line.account_id.code[0:4] == str(
                            account):
                        move = self.env['account.move'].search(
                            [('payment_reference', 'like', line.move_id.payment_reference)])
                        for p in move.line_ids:
                            if p.account_id.code[0:3] == str('40457') or p.account_id.code[0:2] == str(
                                    '40457') or p.account_id.code[0:1] == str('40457') or p.account_id.code[0:4] == str(
                                '40457'):
                                list_tva.append(move)
                                list_tva = list(set(list_tva))
                                for l in list_tva:
                                    for line in l.line_ids:
                                        if line.account_id.code[0:3] == str('40457') or line.account_id.code[
                                                                                        0:2] == str(
                                                '40457') or line.account_id.code[0:1] == str(
                                            '40457') or line.account_id.code[0:4] == str('40457'):
                                            total = line.debit
                                            break
                                    break
        else:
            move_lines = self.env['account.move.line'].search(
                [('account_id.code', 'like', accounts), ('date', 'like', year)])

            for line in move_lines:
                if line.account_id.code[0:3] == str(accounts) or line.account_id.code[0:2] == str(accounts) or \
                        line.account_id.code[0:1] == str(accounts) or line.account_id.code[0:4] == str(accounts):
                    move = self.env['account.move'].search(
                        [('payment_reference', 'like', line.move_id.payment_reference)])
                    total = 0
                    for p in move.line_ids:
                        if p.account_id.code[0:3] == str('40457') or p.account_id.code[0:2] == str(
                                '40457') or p.account_id.code[0:1] == str('40457') or p.account_id.code[0:4] == str(
                                '40457'):
                            list_tva.append(move)
                            list_tva = list(set(list_tva))
                            for l in list_tva:
                                i = 0
                                for line in l.line_ids:
                                    if line.account_id.code[0:3] == str('40457') or line.account_id.code[0:2] == str(
                                            '40457') or line.account_id.code[0:1] == str(
                                            '40457') or line.account_id.code[0:4] == str('40457'):
                                        total = line.debit
                                        break
                                break
        data_dict = {
            field_name: (f'{int(total):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            path + '/etat6_5.pdf',
            path + '/etat6_5.pdf',
            data_dict)
        return int(total)

    def default_get_imobili(self, year, path):
        date_reference = '31' + '-' + '12' + '-' + str(year)
        datetime_reference = datetime.strptime(date_reference, '%d-%m-%Y').date()
        imobilisation = self.env['account.asset'].search([])
        list_imo = imobilisation
        name = []
        print(len(list_imo), 'list imobilisation')
        i = 0
        amortissement = 0
        valeur_net = 0
        for list in list_imo:
            if list.depreciation_move_ids and list.state == 'close':
                for line in list.depreciation_move_ids:
                    if line.date == datetime_reference:
                        amortissement = line.asset_depreciated_value
                        valeur_net = list.original_value - line.asset_depreciated_value
            else:
                amortissement = 0
                valeur_net = 0
            i = i + 1

            var1 = str('NIC') + str(i)
            var2 = str('Date') + str(i)
            var3 = str('MNA') + str(i)
            var4 = str('AP') + str(i)
            var5 = str('VNC') + str(i)
            data_dict = {
                var1: list.name,
                var2: list.acquisition_date,
                var3: amortissement,
                var4: list.method,
                var5: valeur_net,
            }
            if i == 8:
                break
            fillpdfs.write_fillable_pdf(
                path + '/etat7_8.pdf',
                path + '/etat7_8.pdf',
                data_dict)

    def compute_TI(self, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        self.default_get_imobili(year, path)

    def compute_TMV(self, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        # ----------etat5----------
        # premiére ligne
        self.compute_sum_etat56([2807], 'DC_Goodwill', year)
        self.compute_sum_year_etat56([2807], 'DE_Goodwill', year, 0)
        self.compute_sum_year_etat56([2807], 'DS_Goodwill', year, 1)
        self.compute_sum_year_etat56([2807], 'DFE_Goodwill', year, 0)

        # deuxieme ligne
        xxx = self.compute_sub_accounts_etat([280], [[2087]], year, 0)
        self.set_sub_accounts_etat(xxx, 'DC_ii')
        yyy = self.compute_sub_accounts_etat_cette_year([280], [[2087]], year, 0)
        self.set_sub_accounts_etat(yyy, 'DE_ii')

        yyy = self.compute_sub_accounts_etat_cette_year([280], [[2087]], year, 1)
        self.set_sub_accounts_etat(yyy, 'DS_ii')

        yyy = self.compute_sub_accounts_etat_cette_year([280], [[2087]], year, 0)
        self.set_sub_accounts_etat(yyy, 'DFE_ii')

        # 3éme ligne
        self.compute_sum_etat56([281], 'DC_ic', year)
        self.compute_sum_year_etat56([281], 'DE_ic', year, 0)
        self.compute_sum_year_etat56([281], 'DS_ic', year, 1)
        self.compute_sum_year_etat56([281], 'DFE_ic', year, 0)

        # 4éme ligne
        self.compute_sum_etat56(286, 'DC_p', year)
        self.compute_sum_year_etat56([286], 'DE_p', year, 0)
        self.compute_sum_year_etat56([286], 'DS_p', year, 1)
        self.compute_sum_year_etat56([286], 'DFE_p', year, 0)

        # 5éme ligne
        self.compute_sum_etat56(287, 'DC_aa', year)
        self.compute_sum_year_etat56([287], 'DE_aa', year, 0)
        self.compute_sum_year_etat56([287], 'DS_aa', year, 1)
        self.compute_sum_year_etat56([287], 'DFE_aa', year, 0)

        # --------etat6------
        # 1ere ligne

        self.compute_sum_year_etat56([207], 'MB_Goodwill', year, 1)
        self.compute_tva_etat6_cette_year([207], 'TVA_Goodwill', year)

        # 2eme ligne

        zzz = self.compute_sub_accounts_etat_cette_year([20], [[207]], year, 1)
        self.set_sub_accounts_etat(zzz, 'MB_ii')

        lll = self.compute_tva_sousaccounts_etat([20], [[207]], year)
        self.set_sub_accounts_etat(lll, 'TVA_ii')

        # 3eme ligne

        self.compute_sum_year_etat56(21, 'MB_ic', year, 1)
        self.compute_tva_etat6_cette_year([21], 'TVA_ic', year)

        # 4éme ligne
        self.compute_sum_year_etat56(26, 'MB_p', year, 1)
        self.compute_tva_etat6_cette_year([26], 'TVA_p', year)

        # 5eme ligne

        aaa = self.compute_sub_accounts_etat_cette_year([27], [[275], [279]], year, 1)
        self.set_sub_accounts_etat(aaa, 'MB_aa')

        fff = self.compute_tva_sousaccounts_etat([27], [[275], [279]], year)
        self.set_sub_accounts_etat(fff, 'TVA_aa')

    def compute_TCR(self, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value
        # if the last parametre in the fuction compute_sum = 0 then credit elseif =1 then debit
        # vente de marchandise
        # N
        self.compute_sum(700, 'v', year, 0)
        # N-1
        self.compute_sum(700, 'bb', year - 1, 0)

        # prioduit vendue
        # produit fabriqué----------------------------------------------------
        # N
        self.compute_sum([701, 702, 703], 'v1', year, 0)
        # N-1
        self.compute_sum([701, 702, 703], 'bb1', year - 1, 0)
        # prestation de services-------------------------------------------------
        # N
        self.compute_sum([705, 706], 'v2', year, 0)
        # N-1
        self.compute_sum([705, 706], 'bb2', year - 1, 0)
        # vente de traveaux--------------------------------------------------------
        # N
        self.compute_sum(704, 'v3', year, 0)
        # N-1
        self.compute_sum(704, 'bb3', year - 1, 0)

        # produit annexes--------------------------------------------------------------
        # N
        self.compute_sum(708, 'v4', year, 0)
        # N-1
        self.compute_sum(708, 'bb4', year - 1, 0)

        # rabais, remises, ristournes accordés----------------------------------------
        # N
        self.compute_sum(709, 'z', year, 1)
        # N-1
        self.compute_sum(709, 'aa', year - 1, 1)

        # production stocké ou déstocké-------------------------------------------------
        # N
        self.compute_sum(72, 'dd', year, 0)
        self.compute_sum(72, 'cc', year, 1)
        # N-1
        self.compute_sum(72, 'ff', year - 1, 0)
        self.compute_sum(72, 'ee', year - 1, 1)

        # production immobilisée--------------------------------------------------------
        # N
        self.compute_sum(73, 'dd1', year, 0)
        # N-1
        self.compute_sum(73, 'ff1', year - 1, 0)

        # subventions d'exploitation-------------------------------------------------------
        # N
        self.compute_sum(74, 'dd2', year, 0)
        # N-1
        self.compute_sum(74, 'ff2', year - 1, 0)

        # achat de marchandises vendues------------------------------------------------------
        # N
        self.compute_sum(600, 'mm', year, 1)
        # N-1
        self.compute_sum(600, 'ab', year - 1, 1)

        # matieres premieres------------------------------------------------------------------
        # N
        self.compute_sum(601, 'mm1', year, 1)
        # N-1
        self.compute_sum(601, 'aab1', year - 1, 1)

        # autres approvisionnements----------------------------------------------------------------
        # N
        self.compute_sum(602, 'mm2', year, 1)
        # N-1
        self.compute_sum(602, 'ab2', year - 1, 1)

        # variations des stocks------------------------------------------------------------------------
        # N
        self.compute_sum(603, 'mm3', year, 1)
        self.compute_sum(603, 'ab1', year, 0)
        # N-1
        self.compute_sum(603, 'dd3', year - 1, 1)
        self.compute_sum(603, 'ccm', year - 1, 0)

        # achats d'etudes et de prestation de services----------------------------------------------------------
        # N
        self.compute_sum(604, 'mm4', year, 1)
        # N-1
        self.compute_sum(604, 'dd4', year - 1, 1)

        # autres consommations------------------------------------------------------------------------------
        # N
        self.compute_sum([605, 606, 607, 608], 'mm5', year, 1)
        # N-1
        self.compute_sum([605, 606, 607, 608], 'dd5', year - 1, 1)

        # rabais, remises, restournes obtenus sur achats-------------------------------------------------------
        # N
        self.compute_sum(609, 'ab3', year, 0)
        # N-1
        self.compute_sum(609, 'ab4', year - 1, 0)

        # services exterieurs--------------------------------------------------------------------------------------------------------------------
        # sous-traitance generale--------------------------------------------------------------------------------
        # N
        self.compute_sum(611, 'mm6', year, 1)
        # N-1
        self.compute_sum(611, 'dd6', year - 1, 1)

        # locations-----------------------------------------------------------------------------------------------
        # N
        self.compute_sum(613, 'mm7', year, 1)
        # N-1
        self.compute_sum(613, 'dd7', year - 1, 1)

        # entretien, reparations et mainetenance-------------------------------------------------------------------
        # N
        self.compute_sum(615, 'mm8', year, 1)
        # N-1
        self.compute_sum(615, 'dd8', year - 1, 1)

        # primes d'assurances---------------------------------------------------------------------------------------
        # N
        self.compute_sum(616, 'mm9', year, 1)
        # N-1
        self.compute_sum(616, 'dd9', year - 1, 1)

        # personnel exterieur a l'entreprise------------------------------------------------------------------------
        # N
        self.compute_sum(621, 'mm10', year, 1)
        # N-1
        self.compute_sum(621, 'dd10', year - 1, 1)

        # remunerations= d'intermediaires et honoraires-------------------------------------------------------------
        # N
        self.compute_sum(622, 'mm11', year, 1)
        # N-1
        self.compute_sum(622, 'dd11', year - 1, 1)

        # publicité-------------------------------------------------------------------------------------------------
        # N
        self.compute_sum(623, 'mm12', year, 1)
        # N-1
        self.compute_sum(623, 'dd12', year - 1, 1)

        # deplacements, missions et receptions-----------------------------------------------------------------------
        # N
        self.compute_sum(625, 'mm13', year, 1)
        # N-1
        self.compute_sum(625, 'dd13', year - 1, 1)

        # autres services--------------------------------------------------------------------------------------------
        # N
        sum = self.debit_bilan_tcr(year)
        data_dict = {
            'mm14': (f'{int(sum):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            path + '/accounts_res.pdf',
            path + '/accounts_res.pdf',
            data_dict)
        # autres services--------------------------------------------------------------------------------------------
        # N -1
        sum = self.debit_bilan_tcr(year - 1)
        data_dict = {
            'dd14': (f'{int(sum):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            path + '/accounts_res.pdf',
            path + '/accounts_res.pdf',
            data_dict)
        # self.compute_autres_services('mm14', year)
        # N-1
        # xxx = self.compute_sold_sub_accounts([61, 62], [[611, 613, 615, 616], [621, 623, 622, 622]], year, 0)
        # self.set_sub_accounts(xxx, 'dd14', "accounts_res")
        # self.compute_autres_services('dd14', year - 1)

        # rabais, remises, ristournes obtenus sur services exterieurs-------------------------------------------------
        # N
        self.compute_sum(619, 'ab5', year, 0)
        # N-1
        self.compute_sum(619, 'ab6', year - 1, 0)

        # charges de personnel----------------------------------------------------------------------------------------
        # N
        self.compute_sum(63, 'cp', year, 1)
        # N-1
        self.compute_sum(63, 'cp4', year - 1, 1)

        # impots et taxes et versement assimilés----------------------------------------------------------------------
        # N
        self.compute_sum(64, 'cp1', year, 1)
        # N-1
        self.compute_sum(64, 'cp5', year - 1, 1)

        # autres produits opérationnels--------------------------------------------------------------------------------
        # N
        self.compute_sum(75, 'yy', year, 0)
        # N-1
        self.compute_sum(75, 'sb', year - 1, 0)

        # autres charges operationnelles---------------------------------------------------------------------------------
        # N
        self.compute_sum(65, 'zz', year, 1)
        # N-1
        self.compute_sum(65, 'sw', year - 1, 1)

        # dotation aux amortissements------------------------------------------------------------------------------------
        # N
        self.compute_sum(68, 'zz1', year, 1)
        # N-1
        self.compute_sum(68, 'sw1', year - 1, 1)

        # reprise sur pertes de valeur et provisions---------------------------------------------------------------------
        # N
        self.compute_sum(78, 'yy1', year, 0)
        # N-1
        self.compute_sum(78, 'sb1', year - 1, 0)

        # produit financiers---------------------------------------------------------------------------------------------
        # N
        self.compute_sum(76, 'am', year, 0)
        # N-1
        self.compute_sum(76, 'am1', year - 1, 0)

        # charges financieres--------------------------------------------------------------------------------------------
        # N
        self.compute_sum(66, 'am2', year, 1)
        # N-1
        self.compute_sum(66, 'am3', year - 1, 1)

        # elements extraordinaires (produits) (*)------------------------------------------------------------------------
        # N
        self.compute_sum(77, 'aam', year, 0)
        # N-1
        self.compute_sum(77, 'aam1', year - 1, 0)

        # elements extraordinaires (charges) (*)-------------------------------------------------------------------------
        # N
        self.compute_sum(67, 'aam2', year, 1)
        # N-1
        self.compute_sum(67, 'aam3', year - 1, 1)

        # impots exigibles sur resultats---------------------------------------------------------------------------------
        # N
        self.compute_sum([695, 698], 'kk', year, 1)
        # N-1
        self.compute_sum([695, 698], 'kk2', year - 1, 1)

        # impots differes (variations) sur resultats---------------------------------------------------------------------
        # N
        self.compute_sum([692, 693], 'kk1', year, 1)
        self.compute_sum([692, 693], 'kk10', year, 0)
        # N-1
        self.compute_sum([692, 693], 'kk3', year - 1, 1)
        self.compute_sum([692, 693], 'kk20', year - 1, 0)
        #

    def bilan_passif(self, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value

        """Capital �mis (ou accounts de l'exploitant)"""
        self.compute_sold_bp([101, 108], 'g', year)
        self.compute_sold_bp([101, 108], 'm', year - 1)

        """Capital non appel�"""
        self.compute_sold_bp(109, 'g1', year)
        self.compute_sold_bp(109, 'm1', year - 1)

        """Primes et r�serves( R�serves consolid�s ) """
        self.compute_sold_bp([103, 104, 106], 'g2', year)
        self.compute_sold_bp([103, 104, 106], 'm2', year - 1)

        """Ecart de r��valuation """
        self.compute_sold_bp(105, 'g3', year)
        self.compute_sold_bp(105, 'm3', year - 1)

        """Ecart d'�quivalence """
        self.compute_sold_bp(107, 'g4', year)
        self.compute_sold_bp(107, 'm4', year - 1)

        """R�sultat net ( R�sultat net du groupe )"""
        self.compute_sold_bp([7, 6, 12, 896, 897], 'g5', year)
        self.compute_sold_bp([7, 6, 12, 896, 897], 'm5', year - 1)

        """ Autres capitaux propores - Report � nouveau """
        self.compute_sold_bp(11, 'g6', year)
        self.compute_sold_bp(11, 'm6', year - 1)

        """Emprunts et dettes financi�res """
        self.compute_sold_bp([16, 17], 'n', year)
        self.compute_sold_bp([16, 17], 'o', year - 1)

        """Imp�ts (diff�r�s et provisionn�s) """
        self.compute_sold_bp([134, 155], 'n1', year)
        self.compute_sold_bp([134, 155], 'o1', year - 1)

        self.compute_sold_bp([229, 269], 'n2', year)
        self.compute_sold_bp([229, 269], 'o2', year - 1)

        """Fournisseurs et accountss rattach�s """
        xxx = self.compute_sold_sub_accounts([40], [[409]], year, 0)
        self.set_sub_accounts(xxx, 'p', "BP")

        """ Imp�ts"""
        xxx = self.compute_sold_sub_accounts([40], [[409]], year - 1, 0)
        self.set_sub_accounts(xxx, 's', "BP")

        """ Autres dettes """
        xxx = self.credit_bilan_passif(year)
        self.set_sub_accounts(xxx, 'p1', "BP")
        xxx = self.credit_bilan_passif(year - 1)
        self.set_sub_accounts(xxx, 's1', "BP")

        xxx = self.compute_sold_bp([419, 509], '', year) + self.credit_bilan_passif_autre_dettes(year)
        self.set_sub_accounts(abs(xxx), 'p2', "BP")
        xxx = self.compute_sold_bp([419, 509], '', year - 1) + self.credit_bilan_passif_autre_dettes(year - 1)
        self.set_sub_accounts(abs(xxx), 's2', "BP")

        """Tr�sorerie passif """
        xxx = self.credit_bilan_passif_tresorerie(year)
        self.set_sub_accounts(xxx, 'p3', "BP")
        xxx = self.credit_bilan_passif_tresorerie(year - 1)
        self.set_sub_accounts(xxx, 's3', "BP")

    def bilan_actif(self, year):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value

        # ecart - goodwill-----------------------------------------------------------------------------------------------
        self.compute_sold_ba(207, 'a1', year, 0)
        self.compute_sold_ba([2807, 2907], 'b1', year, 0)

        # immobilisations incorporelles----------------------------------------------------------------------------------
        xxx = self.compute_sold_sub_accounts([20], [[207]], year, 0)
        self.set_sub_accounts(xxx, 'a2', "BA")

        xxx = self.compute_sold_sub_accounts([280, 290], [[2807], [2907]], year, 0)
        self.set_sub_accounts(xxx, 'b2', "BA")

        # terrains-------------------------------------------------------------------------------------------------------
        self.compute_sold_ba(211, 'a4', year, 0)
        self.compute_sold_ba([2811, 2911], 'b4', year, 0)

        # batiments------------------------------------------------------------------------------------------------------
        self.compute_sold_ba([212, 213], 'a5', year, 0)
        self.compute_sold_ba([2812, 2912, 2813, 2913], 'b5', year, 0)

        # autres immobilisations corporelles-----------------------------------------------------------------------------
        xxx = self.compute_sold_sub_accounts([21], [[211, 212, 213]], year, 0)
        self.set_sub_accounts(xxx, 'a6', "BA")

        xxx = self.compute_sold_sub_accounts([281, 291], [[2811, 2812, 2813], [2911, 2912, 2913]], year, 0)
        self.set_sub_accounts(xxx, 'b6', "BA")

        # immobilisations en concession----------------------------------------------------------------------------------
        xxx = self.compute_sold_sub_accounts([22], [[229]], year, 0)
        self.set_sub_accounts(xxx, 'a7', "BA")

        xxx = self.compute_sold_sub_accounts([282, 292], [[2829], [2929]], year, 0)
        self.set_sub_accounts(xxx, 'b7', "BA")

        ##immobilisations en cours--------------------------------------------------------------------------------------
        self.compute_sold_ba([23], 'a8', year, 0)
        self.compute_sold_ba([283, 293], 'b8', year, 0)

        # titre mise en equivalence--------------------------------------------------------------------------------------
        self.compute_sold_ba([265], 'a10', year, 0)
        self.set_sub_accounts(0, 'b10', "BA")

        # Autres participations et cr�ances rattach�es-------------------------------------------------------------------
        xxx = self.compute_sold_sub_accounts([26], [[265, 269]], year, 0)
        self.set_sub_accounts(xxx, 'a11', "BA")

        xxx = self.compute_sold_sub_accounts([296], [[2965, 2969]], year, 0)
        self.set_sub_accounts(xxx, 'b11', "BA")

        #	Autres titres immobilis�s-----------------------------------------------------------------------------------
        self.compute_sold_ba([271, 272, 273], 'a12', year, 0)
        self.compute_sold_ba([2971, 2972, 2973], 'b12', year, 0)

        #	Pr�ts et autres actifs financiers non courants--------------------------------------------------------------
        self.compute_sold_ba([274, 275, 276], 'a13', year, 0)
        self.compute_sold_ba([2974, 2975, 2976, 298], 'b13', year, 0)

        #	Imp�ts diff�r�s actif --------------------------------------------------------------------------------------
        self.compute_sold_ba([133], 'a14', year, 0)
        self.set_sub_accounts(0, 'b14', "BA")

        #	Stocks et encours ------------------------------------------------------------------------------------------
        xxx = self.compute_sold_sub_accounts([3], [[39]], year, 0)
        self.set_sub_accounts(xxx, 'e', "BA")

        self.compute_sold_ba([39], 'f', year, 0)

        # Clients--------------------------------------------------------------------------------------------------------
        xxx = self.compute_sold_sub_accounts([41], [[419]], year, 0)
        self.set_sub_accounts(xxx, 'e2', "BA")

        self.compute_sold_ba([491], 'f2', year, 0)

        #	Autres d�biteurs--------------------------------------------------------------------------------------------
        xxx = self.compute_sold_ba([409], '', year, 0) + self.credit_bilan_activ_autre_debiteurs(year)
        self.set_sub_accounts(xxx, 'e3', "BA")

        self.compute_sold_ba([495, 496], 'f3', year, 0)

        # Imp�ts et assimil�s-------------------------------------------------------------------------------------------

        xxx = self.debit_bilan_actif(year)
        self.set_sub_accounts(xxx, 'e4', "BA")

        self.set_sub_accounts(0, 'f4', "BA")

        #	Autres cr�ances et emplois assimil�s------------------------------------------------------------------------
        xxx = self.credit_bilan_activ_autre_creance(year)
        self.set_sub_accounts(xxx, 'e5', "BA")

        self.set_sub_accounts(0, 'f5', "BA")

        #	Placements et autres actifs financiers courants ------------------------------------------------------------
        xxx = self.compute_sold_sub_accounts([50], [[509]], year, 0)
        self.set_sub_accounts(xxx, 'e7', "BA")

        self.set_sub_accounts(0, 'f7', "BA")

        #	Tr�sorerie--------------------------------------------------------------------------------------------------
        xxx = self.compute_sold_ba([53, 54], '', year, 0) + self.treasury_bilan_actif(year)
        self.set_sub_accounts(xxx, 'e8', "BA")

        self.compute_sold_ba([59], 'f8', year, 0)

        """
        ecart d'aquisition N-1---------------------------------------------------------------------------
        """
        xxx = self.compute_sold_ba(207, 'a1', year - 1, 1) - self.compute_sold_ba([2807, 2907], 'b1', year - 1, 1)
        self.set_sub_accounts(xxx, 'd1', "BA")

        """
        IMMOBILISATION INCORPORELLE N-1---------------------------------------------------------------------------
        """
        sum = self.compute_sold_sub_accounts([20], [[207]], year - 1, 0) - self.compute_sold_sub_accounts([280, 290],
                                                                                                          [[2807],
                                                                                                           [2907]],
                                                                                                          year - 1, 0)
        self.set_sub_accounts(sum, 'd2', "BA")

        """
        terrains N-1---------------------------------------------------------------------------
        """
        sum = self.compute_sold_ba(211, 'a4', year - 1, 1) - self.compute_sold_ba([2811, 2911], 'b4', year - 1, 1)
        self.set_sub_accounts(sum, 'd4', "BA")

        """
        Batiments N-1---------------------------------------------------------------------------
        """
        sum = self.compute_sold_ba([212, 213], 'a5', year - 1, 1) - self.compute_sold_ba([2812, 2912, 2813, 2913],
                                                                                         'b5', year - 1, 1)

        self.set_sub_accounts(sum, 'd5', "BA")

        """
        autres immobilisation corporelles N-1---------------------------------------------------------------------------
        """

        sum = self.compute_sold_sub_accounts([21], [[211, 212, 213]], year - 1, 0) - \
              self.compute_sold_sub_accounts([281, 291], [[2811, 2812, 2813], [2911, 2912, 2913]], year - 1, 0)
        self.set_sub_accounts(sum, 'd6', "BA")

        """
         immobilisation en concession N-1---------------------------------------------------------------------------
        """
        sum = self.compute_sold_sub_accounts([22], [[229]], year - 1, 0) - self.compute_sold_sub_accounts([282, 292],
                                                                                                          [[2829],
                                                                                                           [2929]],
                                                                                                          year - 1, 0)

        self.set_sub_accounts(sum, 'd7', "BA")

        """
        immobilisations en cours N-1---------------------------------------------------------------------------
        """
        sum = self.compute_sold_ba([23], 'a8', year - 1, 1) - self.compute_sold_ba([283, 293], 'a8', year - 1, 1)
        self.set_sub_accounts(sum, 'd8', "BA")

        """
         titre mise en equivalence N-1---------------------------------------------------------------------------
        """

        self.compute_sold_ba([265], 'd10', year - 1, 0)

        """
        Autres participations et cr�ances rattach�es---------------------------------------------------------------------------
        """

        xxx = self.compute_sold_sub_accounts([26], [[265, 269]], year - 1, 0) - self.compute_sold_sub_accounts([296], [
            [2965, 2969]], year - 1, 0)
        self.set_sub_accounts(xxx, 'd11', "BA")

        """

        Autres titres immobilis�s---------------------------------------------------------------------------
        """
        sum = self.compute_sold_ba([271, 272, 273], 'a12', year - 1, 1) - self.compute_sold_ba([2971, 2972, 2973],
                                                                                               'b12', year - 1, 1)
        self.set_sub_accounts(sum, 'd12', "BA")

        """
        Pr�ts et autres actifs financiers non courants---------------------------------------------------------------------------
        """
        sum = self.compute_sold_ba([274, 275, 276], 'a13', year - 1, 1) - self.compute_sold_ba([2974, 2975, 2976, 298],
                                                                                               'b13', year - 1, 1)
        self.set_sub_accounts(sum, 'd13', "BA")

        """
        Imp�ts diff�r�s actif n-1---------------------------------------------------------------------------
        """
        sum = self.compute_sold_ba([133], 'a14', year - 1, 1) - 0
        self.set_sub_accounts(sum, 'd14', "BA")

        """
        Stocks et encours N-1---------------------------------------------------------------------------
        """

        sum = self.compute_sold_sub_accounts([3], [[39]], year - 1, 0) - self.compute_sold_ba([39], 'f', year - 1, 1)
        self.set_sub_accounts(sum, 'k', "BA")

        """
        Clients N-1---------------------------------------------------------------------------
        """

        sum = self.compute_sold_sub_accounts([41], [[419]], year - 1, 0) - self.compute_sold_ba([491], 'f2', year - 1,
                                                                                                1)
        self.set_sub_accounts(sum, 'k2', "BA")

        """
        Autres d�biteurs N-1---------------------------------------------------------------------------
        """

        sum = self.compute_sold_ba([409], '', year - 1, 0) + self.credit_bilan_activ_autre_debiteurs(year - 1)
        self.set_sub_accounts(sum, 'k3', "BA")

        # Imp�ts et assimil�s-------------------------------------------------------------------------------------------
        xxx = self.debit_bilan_actif(year - 1)
        self.set_sub_accounts(xxx, 'k4', "BA")

        #	Autres cr�ances et emplois assimil�s------------------------------------------------------------------------
        xxx = self.credit_bilan_activ_autre_creance(year - 1)
        self.set_sub_accounts(xxx, 'k5', "BA")

        #	Placements et autres actifs financiers courants ------------------------------------------------------------
        xxx = self.compute_sold_sub_accounts([50], [[509]], year - 1, 0)
        self.set_sub_accounts(xxx, 'k7', "BA")

        #	Tr�sorerie--------------------------------------------------------------------------------------------------
        xxx = self.compute_sold_ba([53, 54], '', year - 1, 0) + self.compute_sum_ba(
            [51, 52, 58], '', year - 1, 1) - self.compute_sold_ba([59], 'f8', year - 1, 1)
        self.set_sub_accounts(xxx, 'k8', "BA")

    def compute_sum_credit_debit(self, move_lines, account, year):
        debit = sum(
            move_lines.filtered(lambda o: o if o.account_id.code == account and int(o.date.year) == int(year) else False).mapped(
                'debit'))
        credit = sum(
            move_lines.filtered(lambda o: o if o.account_id.code == account and int(o.date.year) == int(year) else False).mapped(
                'credit'))
        return debit, credit

    def compute_stock_table_1_2(self, year):
        move_lines = self.env['account.move.line']

        # Stock Table
        accounts = self.env['account.account'].search([('code', '=ilike', '3%')]).mapped('code')
        stock_move_lines = move_lines.search([('account_id.code', 'in', accounts)])
        sums = {
            'sold_n_1': [],
            'debit': [],
            'credit': [],
            'sold_n': [],
        }
        debit = 0
        credit = 0
        for root in accounts:
            if int(root[0:2]) in [30, 31, 32, 33, 34, 35, 36, 37]:
                debit, credit = self.compute_sum_credit_debit(stock_move_lines, root, year - 1)
                self.set_sub_accounts((debit - credit), 'Sdebut_' + root[0:2], "stock_table_1_2")
                sums['sold_n_1'].append((debit - credit))
                debit, credit = self.compute_sum_credit_debit(stock_move_lines, root, year)
                self.set_sub_accounts(debit, 'Debit_' + root[0:2], "stock_table_1_2")
                self.set_sub_accounts(credit, 'Credit_' + root[0:2], "stock_table_1_2")
                self.set_sub_accounts((debit - credit), 'Sfin_' + root[0:2], "stock_table_1_2")
                sums['debit'].append(debit)
                sums['credit'].append(credit)
                sums['sold_n'].append((debit - credit))

        self.set_sub_accounts(sum(sums['sold_n_1']), 'sold_n_1', "stock_table_1_2")
        self.set_sub_accounts(sum(sums['sold_n']), 'sold_n', "stock_table_1_2")
        self.set_sub_accounts(sum(sums['debit']), 'sdebit', "stock_table_1_2")
        self.set_sub_accounts(sum(sums['credit']), 'scredit', "stock_table_1_2")

        # Production Stock Table
        result_move_lines = move_lines.search([('account_id', '=ilike', '72%'), ('date', 'like', year)])
        debit = sum(result_move_lines.mapped('debit'))
        credit = sum(result_move_lines.mapped('credit'))
        self.set_sub_accounts(debit, 'Debit1', "stock_table_1_2")
        self.set_sub_accounts(credit, 'Credit1', "stock_table_1_2")
        if debit > credit:
            self.set_sub_accounts((debit-credit), 'Debiteur1', "stock_table_1_2")
        else:
            self.set_sub_accounts((credit - debit), 'Crediteur1', "stock_table_1_2")

    def compute_charge_table_3_4(self, year):
        move_lines = self.env['account.move.line']
        accounts = self.env['account.account']
        sums = {}
        # Charge Table
        charge_accounts = accounts.search([('code', '=ilike', '6%')])
        charge_move_lines = move_lines.search([('account_id', 'in', charge_accounts.ids)])
        for root in charge_accounts.mapped('code'):
            # other services
            if int(root[0:3]) == 614:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 617:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 618:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 624:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 626:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 627:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 628:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))

            # personal charges
            elif int(root[0:3]) == 631:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 634:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 635:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 636:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 637:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 638:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))

            # Taxes
            elif int(root[0:3]) == 641:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 642:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 645:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))

            # Other operational charges
            elif int(root[0:3]) == 651:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 652:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 653:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 654:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 655:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 656:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 657:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 658:
                debit, credit = self.compute_sum_credit_debit(charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))

        total1 = 0
        self.set_sub_accounts(sum(sums['614']) if '614' in sums else 0, 'Charges_locatives', "charge_table_3_4")
        total1 += sum(sums['614']) if '614' in sums else 0
        self.set_sub_accounts(sum(sums['617']) if '617' in sums else 0, 'Etudes_recherches', "charge_table_3_4")
        total1 += sum(sums['617']) if '617' in sums else 0
        self.set_sub_accounts(sum(sums['618']) if '618' in sums else 0, 'Documentation_divers', "charge_table_3_4")
        total1 += sum(sums['618']) if '618' in sums else 0
        self.set_sub_accounts(sum(sums['624']) if '624' in sums else 0, 'Transports_ biens', "charge_table_3_4")
        total1 += sum(sums['624']) if '624' in sums else 0
        self.set_sub_accounts(sum(sums['626']) if '626' in sums else 0, 'Frais_ postaux', "charge_table_3_4")
        total1 += sum(sums['626']) if '626' in sums else 0
        self.set_sub_accounts(sum(sums['627']) if '627' in sums else 0, 'Services_bancaires', "charge_table_3_4")
        total1 += sum(sums['627']) if '627' in sums else 0
        self.set_sub_accounts(sum(sums['628']) if '628' in sums else 0, 'Cotisations_divers', "charge_table_3_4")
        total1 += sum(sums['628']) if '628' in sums else 0
        self.set_sub_accounts(total1, 'TOTAL 1', "charge_table_3_4")

        total2 = 0
        self.set_sub_accounts(sum(sums['631']) if '631' in sums else 0, 'Rem_personnel', "charge_table_3_4")
        total2 += sum(sums['631']) if '631' in sums else 0
        self.set_sub_accounts(sum(sums['634']) if '634' in sums else 0, 'Rem_exp', "charge_table_3_4")
        total2 += sum(sums['634']) if '634' in sums else 0
        self.set_sub_accounts(sum(sums['635']) if '635' in sums else 0, 'Cotisations_org_sociaux', "charge_table_3_4")
        total2 += sum(sums['635']) if '635' in sums else 0
        self.set_sub_accounts(sum(sums['636']) if '636' in sums else 0, 'Charges_exp', "charge_table_3_4")
        total2 += sum(sums['636']) if '636' in sums else 0
        self.set_sub_accounts(sum(sums['637']) if '637' in sums else 0, 'Autres_charges', "charge_table_3_4")
        total2 += sum(sums['637']) if '637' in sums else 0
        self.set_sub_accounts(sum(sums['638']) if '638' in sums else 0, 'Autres_charges_pers', "charge_table_3_4")
        total2 += sum(sums['638']) if '638' in sums else 0
        self.set_sub_accounts(total2, 'TOTAL 2', "charge_table_3_4")

        total3 = 0
        self.set_sub_accounts(sum(sums['641']) if '641' in sums else 0, 'Imp', "charge_table_3_4")
        total3 += sum(sums['641']) if '641' in sums else 0
        self.set_sub_accounts(sum(sums['642']) if '642' in sums else 0, 'Imp_nrecup', "charge_table_3_4")
        total3 += sum(sums['642']) if '642' in sums else 0
        self.set_sub_accounts(sum(sums['645']) if '645' in sums else 0, 'Autres_imp', "charge_table_3_4")
        total3 += sum(sums['645']) if '645' in sums else 0
        self.set_sub_accounts(total3, 'TOTAL 3', "charge_table_3_4")
        self.set_sub_accounts((total1+total2+total3), 'TOTAL  1 2 3', "charge_table_3_4")

        total4 = 0
        self.set_sub_accounts(sum(sums['651']) if '651' in sums else 0, 'Redevances_concessions', "charge_table_3_4")
        total4 += sum(sums['651']) if '651' in sums else 0
        self.set_sub_accounts(sum(sums['652']) if '652' in sums else 0, 'Moins_values_actifs', "charge_table_3_4")
        total4 += sum(sums['652']) if '652' in sums else 0
        self.set_sub_accounts(sum(sums['653']) if '653' in sums else 0, 'Jetons_presence', "charge_table_3_4")
        total4 += sum(sums['653']) if '653' in sums else 0
        self.set_sub_accounts(sum(sums['654']) if '654' in sums else 0, 'Perte_creances', "charge_table_3_4")
        total4 += sum(sums['654']) if '654' in sums else 0
        self.set_sub_accounts(sum(sums['655']) if '655' in sums else 0, 'Quotepart_resultat', "charge_table_3_4")
        total4 += sum(sums['655']) if '655' in sums else 0
        self.set_sub_accounts(sum(sums['656']) if '656' in sums else 0, 'Amendes_pen', "charge_table_3_4")
        total4 += sum(sums['656']) if '656' in sums else 0
        self.set_sub_accounts(sum(sums['657']) if '657' in sums else 0, 'Charges_exceptionnelles', "charge_table_3_4")
        total4 += sum(sums['657']) if '657' in sums else 0
        self.set_sub_accounts(sum(sums['658']) if '658' in sums else 0, 'Autres', "charge_table_3_4")
        total4 += sum(sums['658']) if '658' in sums else 0
        self.set_sub_accounts(total4, 'TOT', "charge_table_3_4")

        # Other charge table
        other_charge_accounts = accounts.search([('code', '=ilike', '75%')])
        other_charge_move_lines = move_lines.search([('account_id.code', 'in', other_charge_accounts.ids)])

        for root in other_charge_accounts.mapped('code'):
            # Other operational charges
            if int(root[0:3]) == 751:
                debit, credit = self.compute_sum_credit_debit(other_charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 752:
                debit, credit = self.compute_sum_credit_debit(other_charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 753:
                debit, credit = self.compute_sum_credit_debit(other_charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 754:
                debit, credit = self.compute_sum_credit_debit(other_charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 755:
                debit, credit = self.compute_sum_credit_debit(other_charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 756:
                debit, credit = self.compute_sum_credit_debit(other_charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 757:
                debit, credit = self.compute_sum_credit_debit(other_charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))
            elif int(root[0:3]) == 758:
                debit, credit = self.compute_sum_credit_debit(other_charge_move_lines, root, year)
                if root[0:3] not in sums:
                    sums[root[0:3]] = []
                sums[root[0:3]].append((debit-credit))

        total5 = 0
        self.set_sub_accounts(sum(sums['751']) if '751' in sums else 0, 'Redevances_brevets', "charge_table_3_4")
        total5 += sum(sums['751']) if '751' in sums else 0
        self.set_sub_accounts(sum(sums['752']) if '752' in sums else 0, 'Plus_values_actifs', "charge_table_3_4")
        total5 += sum(sums['752']) if '752' in sums else 0
        self.set_sub_accounts(sum(sums['753']) if '753' in sums else 0, 'Jetons_rem', "charge_table_3_4")
        total5 += sum(sums['753']) if '753' in sums else 0
        self.set_sub_accounts(sum(sums['754']) if '754' in sums else 0, 'Quotesparts_subventions', "charge_table_3_4")
        total5 += sum(sums['754']) if '754' in sums else 0
        self.set_sub_accounts(sum(sums['755']) if '755' in sums else 0, 'Quotepart_op', "charge_table_3_4")
        total5 += sum(sums['755']) if '755' in sums else 0
        self.set_sub_accounts(sum(sums['756']) if '756' in sums else 0, 'Rent_creances', "charge_table_3_4")
        total5 += sum(sums['756']) if '756' in sums else 0
        self.set_sub_accounts(sum(sums['757']) if '757' in sums else 0, 'Produits_exceptionnels', "charge_table_3_4")
        total5 += sum(sums['757']) if '757' in sums else 0
        self.set_sub_accounts(sum(sums['758']) if '758' in sums else 0, 'Autres_produits', "charge_table_3_4")
        total5 += sum(sums['758']) if '758' in sums else 0
        self.set_sub_accounts(total5, 'TOTAL_2', "charge_table_3_4")
