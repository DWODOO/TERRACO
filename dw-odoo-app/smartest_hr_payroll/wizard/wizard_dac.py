import base64, xlsxwriter
from datetime import datetime

from odoo import models, fields, api, _
from odoo.http import request

cnt = 10
list1 = []
for i in range(2010, datetime.today().year + 1):
    list1.append((str(cnt), str(i)))
    cnt = cnt + 1


class WizardDac(models.TransientModel):
    _name = 'wizard.dac'

    date_year = fields.Selection(list1, required=True, store=True, string="Exercice", tracking=True)

    month = fields.Selection([
        ('01', 'Janvier'),
        ('02', 'Fevrier'),
        ('03', 'Mars'),
        ('04', 'Avril'),
        ('05', 'Mai'),
        ('06', 'Juin'),
        ('07', 'Juillet'),
        ('08', 'Aout'),
        ('09', 'Septembre'),
        ('10', 'Octobe'),
        ('11', 'Novembre'),
        ('12', 'Decembre'),
    ], string="Month", required=True, tracking=True)

    document = fields.Binary(string='Xls file', readonly='True')

    @api.model
    def def_employe_paie(self, path):
        date_year_month_id = str('20') + str(self.date_year) + str('-') + str(self.month)
        datetime_test_jan = datetime.strptime(date_year_month_id, '%Y-%m')
        date_jan = datetime_test_jan.strftime('%Y-%m')
        workbook = xlsxwriter.Workbook(path)
        worksheet = workbook.add_worksheet()
        worksheet.set_column(1, 20, 15)
        worksheet.set_column(0, 0, 20)
        worksheet.set_column(2, 2, 15)
        worksheet.set_column(5, 5, 3)
        format_date = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        bold = workbook.add_format({'bold': True})
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'yellow'})

        # Merge 3 cells.
        worksheet.merge_range('B1:D1', 'Exercice:  Du  ' + date_jan + '-01  Au  ' + date_jan + '-31', merge_format)
        worksheet.write('A3', 'ITEM', bold)
        worksheet.write('B3', 'Montant', bold)
        worksheet.write('A4', 'AC', bold)
        worksheet.write('A5', 'PP', bold)
        worksheet.write('A6', 'CE', bold)

        worksheet.write('A9', 'Nom et Prenom', bold)
        worksheet.write('B9', 'Date de Naissance', bold)
        worksheet.write('C9', 'NSS', bold)
        worksheet.write('D9', 'Date Entrée', bold)
        worksheet.write('E9', 'Date Sortie', bold)
        worksheet.write('F9', 'E/S', bold)

        rub_paie = self.env['hr.payslip'].search(
            [('date_from', 'like', date_jan), ('state', '!=', 'cancel')])

        total_ac = 0
        total_PP = 0
        total_cd = 0
        for paies in rub_paie:
            for line in paies.line_ids:
                if line.code == 'R400':
                    total_ac += line.total
                if line.code == 'R404':
                    total_PP += line.total
                if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                    total_cd += line.total

        worksheet.write('B4', total_ac)
        worksheet.write('B5', total_PP)
        worksheet.write('B6', total_cd)
        row = 9
        column = 0

        employee = rub_paie.contract_id.filtered(
            lambda contract: (contract.date_start and contract.date_start.strftime('%Y-%m') == date_jan) or (contract.date_end and contract.date_end.strftime('%Y-%m') == date_jan))

        for i in employee:
            worksheet.write(row, column, i.employee_id.name)
            if i.employee_id.birthday:
                worksheet.write(row, column + 1, i.employee_id.birthday, format_date)
            else:
                worksheet.write(row, column + 1, '')
            worksheet.write(row, column + 2, i.employee_id.social_security_number)
            f = i.date_start
            date_start = f.strftime('%Y-%m')
            if str(date_start) == str(date_jan):
                worksheet.write(row, column + 3, i.date_start, format_date)
                worksheet.write(row, column + 4, '')
                worksheet.write(row, column + 5, 'E', bold)

            else:
                worksheet.write(row, column + 3, i.date_start, format_date)
                worksheet.write(row, column + 4, i.date_end, format_date)
                worksheet.write(row, column + 5, 'S', bold)
            row += 1

        workbook.close()

    def init_dac(self):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value + "/Dac.xlsx"
        self.def_employe_paie(path)
        file = open(path, "rb")
        out = file.read()
        file.close()
        self.document = base64.b64encode(out)
        action = self.env.ref('smartest_hr_payroll.wizard_dac_action').read()[0]
        action['res_id'] = self.id
        action['context'] = {
            'smartest_hide_excel_btn': True
        }
        return action
