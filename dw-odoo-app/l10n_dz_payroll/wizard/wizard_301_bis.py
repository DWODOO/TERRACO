import pdb
from datetime import datetime
import base64, xlsxwriter

from odoo import models, fields, api, _
from odoo.http import request

cnt = 10
list1 = []
for i in range(2010, datetime.today().year + 1):
    list1.append((str(cnt), str(i)))
    cnt = cnt + 1


class Wizard301Bis(models.TransientModel):
    _name = 'wizard.301.bis'

    reference_date = fields.Selection(list1, required=True, store=True, string="Exercice", tracking=True)
    document = fields.Binary(string='Xls file', readonly='True')

    @api.model
    def def_employe_paie(self, reference_date, path):

        workbook = xlsxwriter.Workbook(path)
        worksheet = workbook.add_worksheet()
        worksheet.set_column(1, 200, 25)
        bold = workbook.add_format({'bold': True})
        worksheet.write('A1', 'Matricule', bold)
        worksheet.write('B1', 'Nom et Prenom', bold)
        worksheet.write('C1', 'Poste Occuper', bold)
        worksheet.write('D1', 'Base Jan', bold)
        worksheet.write('E1', 'IRG Jan', bold)
        worksheet.write('F1', 'IRG 10%', bold)
        worksheet.write('G1', 'Base Fev', bold)
        worksheet.write('H1', 'IRG Fev', bold)
        worksheet.write('I1', 'IRG 10%', bold)
        worksheet.write('J1', 'Base Mar', bold)
        worksheet.write('K1', 'IRG Mar', bold)
        worksheet.write('L1', 'IRG 10%', bold)
        worksheet.write('M1', 'Base Avr', bold)
        worksheet.write('N1', 'IRG Avr', bold)
        worksheet.write('O1', 'IRG 10%', bold)
        worksheet.write('P1', 'Base Mai', bold)
        worksheet.write('Q1', 'IRG Mai', bold)
        worksheet.write('R1', 'IRG 10%', bold)
        worksheet.write('S1', 'Base Juin', bold)
        worksheet.write('T1', 'IRG Juin', bold)
        worksheet.write('U1', 'IRG 10%', bold)
        worksheet.write('V1', 'Base Jui', bold)
        worksheet.write('W1', 'IRG Jui', bold)
        worksheet.write('X1', 'IRG 10%', bold)
        worksheet.write('Y1', 'Base Aout', bold)
        worksheet.write('Z1', 'IRG Aout', bold)
        worksheet.write('AA1', 'IRG 10%', bold)
        worksheet.write('AB1', 'Base Sep', bold)
        worksheet.write('AC1', 'IRG Sep', bold)
        worksheet.write('AD1', 'IRG 10%', bold)
        worksheet.write('AE1', 'Base Oct', bold)
        worksheet.write('AF1', 'IRG Oct', bold)
        worksheet.write('AG1', 'IRG 10%', bold)
        worksheet.write('AH1', 'Base Nov', bold)
        worksheet.write('AI1', 'IRG Nov', bold)
        worksheet.write('AJ1', 'IRG 10%', bold)
        worksheet.write('AK1', 'Base Dec', bold)
        worksheet.write('AL1', 'IRG Dec', bold)
        worksheet.write('AM1', 'IRG 10%', bold)
        row = 1
        column = 0
        somme_jan = 0
        somme_fev = 0
        somme_mar = 0
        somme_avr = 0
        somme_mai = 0
        somme_juin = 0
        somme_juill = 0
        somme_aout = 0
        somme_sept = 0
        somme_oct = 0
        somme_nov = 0
        somme_dec = 0
        irg_jan = 0
        irg_jan_ = 0
        irg_fev = 0
        irg_fev_ = 0
        irg_mar = 0
        irg_mar_ = 0
        irg_avr = 0
        irg_avr_ = 0
        irg_mai = 0
        irg_mai_ = 0
        irg_juin = 0
        irg_juin_ = 0
        irg_juill = 0
        irg_juill_ = 0
        irg_aout = 0
        irg_aout_ = 0
        irg_sept = 0
        irg_sept_ = 0
        irg_oct = 0
        irg_oct_ = 0
        irg_nov = 0
        irg_nov_ = 0
        irg_dec = 0
        irg_dec_ = 0

        employee = self.env['hr.employee'].search([])
        for i in employee:
            worksheet.write(row, column, i.id)
            worksheet.write(row, column + 1, i.name)
            worksheet.write(row, column + 2, i.job_id.name)
            rub_paie = self.env['hr.payslip'].search(
                [('date_from', 'like', reference_date), ('employee_id.id', '=', i.id), ('state', 'in', ['paid', 'verify'
                    , 'done'])])
            date_test = str('20') + str(reference_date)

            for r in rub_paie:
                date_from = r.date_from.strftime('%Y-%m')

                date_du_jan = date_test + str('-') + str('01') + str('-') + str('01')
                datetime_test_jan = datetime.strptime(date_du_jan, '%Y-%m-%d')
                date_jan = datetime_test_jan.strftime('%Y-%m')

                date_du_fev = date_test + str('-') + str('02') + str('-') + str('01')
                datetime_test_fev = datetime.strptime(date_du_fev, '%Y-%m-%d')
                date_fev = datetime_test_fev.strftime('%Y-%m')

                date_du_mar = date_test + str('-') + str('03') + str('-') + str('01')
                datetime_test_mar = datetime.strptime(date_du_mar, '%Y-%m-%d')
                date_mar = datetime_test_mar.strftime('%Y-%m')

                date_du_avr = date_test + str('-') + str('04') + str('-') + str('01')
                datetime_test_avr = datetime.strptime(date_du_avr, '%Y-%m-%d')
                date_avr = datetime_test_avr.strftime('%Y-%m')

                date_du_mai = date_test + str('-') + str('05') + str('-') + str('01')
                datetime_test_mai = datetime.strptime(date_du_mai, '%Y-%m-%d')
                date_mai = datetime_test_mai.strftime('%Y-%m')

                date_du_juin = date_test + str('-') + str('06') + str('-') + str('01')
                datetime_test_juin = datetime.strptime(date_du_juin, '%Y-%m-%d')
                date_juin = datetime_test_juin.strftime('%Y-%m')

                date_du_jui = date_test + str('-') + str('07') + str('-') + str('01')
                datetime_test_jui = datetime.strptime(date_du_jui, '%Y-%m-%d')
                date_jui = datetime_test_jui.strftime('%Y-%m')

                date_du_aout = date_test + str('-') + str('08') + str('-') + str('01')
                datetime_test_aout = datetime.strptime(date_du_aout, '%Y-%m-%d')
                date_aout = datetime_test_aout.strftime('%Y-%m')

                date_du_sep = date_test + str('-') + str('09') + str('-') + str('01')
                datetime_test_sep = datetime.strptime(date_du_sep, '%Y-%m-%d')
                date_sep = datetime_test_sep.strftime('%Y-%m')

                date_du_oct = date_test + str('-') + str('10') + str('-') + str('01')
                datetime_test_oct = datetime.strptime(date_du_oct, '%Y-%m-%d')
                date_oct = datetime_test_oct.strftime('%Y-%m')

                date_du_nov = date_test + str('-') + str('11') + str('-') + str('01')
                datetime_test_nov = datetime.strptime(date_du_nov, '%Y-%m-%d')
                date_nov = datetime_test_nov.strftime('%Y-%m')

                date_du_dec = date_test + str('-') + str('12') + str('-') + str('01')
                datetime_test_dec = datetime.strptime(date_du_dec, '%Y-%m-%d')
                date_dec = datetime_test_dec.strftime('%Y-%m')

                if date_from == date_jan:
                    for line in r.line_ids:
                        if line.code == 'R501':
                            worksheet.write(row, column + 3, line.amount)
                            somme_jan += line.amount
                        if line.code == 'R600':
                            worksheet.write(row, column + 4, line.amount)
                            irg_jan += line.amount

                        if line.code == 'R606':
                            worksheet.write(row, column + 5, line.amount)
                            irg_jan_ += line.amount

                if date_from == date_fev:
                    for line in r.line_ids:
                        if line.code == 'R501':
                            worksheet.write(row, column + 6, line.amount)
                            somme_fev += line.amount
                        if line.code == 'R600':
                            worksheet.write(row, column + 7, line.amount)
                            irg_fev += line.amount
                        if line.code == 'R606':
                            worksheet.write(row, column + 8, line.amount)
                            irg_fev_ += line.amount
                if date_from == date_mar:
                    for line in r.line_ids:
                        if line.code == 'R501':
                            worksheet.write(row, column + 9, line.amount)
                            somme_mar += line.amount
                        if line.code == 'R600':
                            worksheet.write(row, column + 10, line.amount)
                            irg_mar += line.amount
                        if line.code == 'R606':
                            worksheet.write(row, column + 11, line.amount)
                            irg_mar_ += line.amount
                if date_from == date_avr:
                    for line in r.line_ids:
                        if line.code == 'R501':
                            worksheet.write(row, column + 12, line.amount)
                            somme_avr += line.amount
                        if line.code == 'R600':
                            worksheet.write(row, column + 13, line.amount)
                            irg_avr += line.amount
                        if line.code == 'R606':
                            worksheet.write(row, column + 14, line.amount)
                            irg_avr_ += line.amount
                if date_from == date_mai:
                    for line in r.line_ids:
                        if line.code == 'R501':
                            worksheet.write(row, column + 15, line.amount)
                            somme_mai += line.amount
                        if line.code == 'R600':
                            worksheet.write(row, column + 16, line.amount)
                            irg_mai += line.amount
                        if line.code == 'R606':
                            worksheet.write(row, column + 17, line.amount)
                            irg_mai_ += line.amount
                if date_from == date_juin:
                    for line in r.line_ids:
                        if line.code == 'R501':
                            worksheet.write(row, column + 18, line.amount)
                            somme_juin += line.amount
                        if line.code == 'R600':
                            worksheet.write(row, column + 19, line.amount)
                            irg_juin += line.amount
                        if line.code == 'R606':
                            worksheet.write(row, column + 20, line.amount)
                            irg_juin_ += line.amount
                if date_from == date_jui:
                    for line in r.line_ids:
                        if line.code == 'R501':
                            worksheet.write(row, column + 21, line.amount)
                            somme_juill += line.amount
                        if line.code == 'R600':
                            worksheet.write(row, column + 22, line.amount)
                            irg_juill += line.amount
                        if line.code == 'R606':
                            worksheet.write(row, column + 23, line.amount)
                            irg_juill_ += line.amount
                if date_from == date_aout:
                    for line in r.line_ids:
                        if line.code == 'R501':
                            worksheet.write(row, column + 24, line.amount)
                            somme_aout += line.amount
                        if line.code == 'R600':
                            worksheet.write(row, column + 25, line.amount)
                            irg_aout += line.amount
                        if line.code == 'R606':
                            worksheet.write(row, column + 26, line.amount)
                            irg_aout_ += line.amount
                if date_from == date_sep:
                    for line in r.line_ids:
                        if line.code == 'R501':
                            worksheet.write(row, column + 27, line.amount)
                            somme_sept += line.amount
                        if line.code == 'R600':
                            worksheet.write(row, column + 28, line.amount)
                            irg_sept += line.amount
                        if line.code == 'R606':
                            worksheet.write(row, column + 29, line.amount)
                            irg_sept_ += line.amount
                if date_from == date_oct:
                    for line in r.line_ids:
                        if line.code == 'R501':
                            worksheet.write(row, column + 30, line.amount)
                            somme_oct += line.amount
                        if line.code == 'R600':
                            worksheet.write(row, column + 31, line.amount)
                            irg_oct += line.amount
                        if line.code == 'R606':
                            worksheet.write(row, column + 32, line.amount)
                            irg_oct_ += line.amount
                if date_from == date_nov:
                    for line in r.line_ids:
                        if line.code == 'R501':
                            worksheet.write(row, column + 33, line.amount)
                            somme_nov += line.amount
                        if line.code == 'R600':
                            worksheet.write(row, column + 34, line.amount)
                            irg_nov += line.amount
                        if line.code == 'R606':
                            worksheet.write(row, column + 35, line.amount)
                            irg_nov_ += line.amount

                if date_from == date_dec:
                    for line in r.line_ids:
                        if line.code == 'R501':
                            worksheet.write(row, column + 36, line.amount)
                            somme_dec += line.amount

                        if line.code == 'R600':
                            worksheet.write(row, column + 37, line.amount)
                            irg_dec += line.amount
                        if line.code == 'R606':
                            worksheet.write(row, column + 38, line.amount)
                            irg_dec_ += line.amount
            row += 1

        worksheet.write(row + 1, column + 3, somme_jan)
        worksheet.write(row + 1, column + 4, irg_jan)
        worksheet.write(row + 1, column + 5, irg_jan_)
        worksheet.write(row + 1, column + 6, somme_fev)
        worksheet.write(row + 1, column + 7, irg_fev)
        worksheet.write(row + 1, column + 8, irg_fev_)
        worksheet.write(row + 1, column + 9, somme_mar)
        worksheet.write(row + 1, column + 10, irg_mar)
        worksheet.write(row + 1, column + 11, irg_mar_)
        worksheet.write(row + 1, column + 12, somme_avr)
        worksheet.write(row + 1, column + 13, irg_avr)
        worksheet.write(row + 1, column + 14, irg_avr_)
        worksheet.write(row + 1, column + 15, somme_mai)
        worksheet.write(row + 1, column + 16, irg_mai)
        worksheet.write(row + 1, column + 17, irg_mai_)
        worksheet.write(row + 1, column + 18, somme_juin)
        worksheet.write(row + 1, column + 19, irg_juin)
        worksheet.write(row + 1, column + 20, irg_juin_)
        worksheet.write(row + 1, column + 21, somme_juill)
        worksheet.write(row + 1, column + 22, irg_juill)
        worksheet.write(row + 1, column + 23, irg_juill_)
        worksheet.write(row + 1, column + 24, somme_aout)
        worksheet.write(row + 1, column + 25, irg_aout)
        worksheet.write(row + 1, column + 26, irg_aout_)
        worksheet.write(row + 1, column + 27, somme_sept)
        worksheet.write(row + 1, column + 28, irg_sept)
        worksheet.write(row + 1, column + 29, irg_sept_)
        worksheet.write(row + 1, column + 30, somme_oct)
        worksheet.write(row + 1, column + 31, irg_oct)
        worksheet.write(row + 1, column + 32, irg_oct_)
        worksheet.write(row + 1, column + 33, somme_nov)
        worksheet.write(row + 1, column + 34, irg_nov)
        worksheet.write(row + 1, column + 35, irg_nov_)
        worksheet.write(row + 1, column + 36, somme_dec)
        worksheet.write(row + 1, column + 37, irg_dec)
        worksheet.write(row + 1, column + 38, irg_dec_)

        workbook.close()

    def init_doc(self):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value + "/301bis.xlsx"
        self.def_employe_paie(self.reference_date, path)
        file = open(path, "rb")
        out = file.read()
        file.close()
        self.document = base64.b64encode(out)
        action = self.env.ref('l10n_dz_payroll.wizard_301_bis_action').read()[0]
        action['res_id'] = self.id
        action['context'] = {
            'smartest_hide_excel_301_btn': True
        }
        return action
