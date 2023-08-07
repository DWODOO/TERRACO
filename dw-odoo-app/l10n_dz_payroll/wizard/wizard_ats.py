from odoo import models,fields,api,_
from datetime import datetime
import openpyxl
import base64

from fillpdf import fillpdfs

import os

class Wizardats(models.TransientModel):
    _name = 'wizard.ats'

    id_emp = fields.Many2one('hr.employee',string="Employée")

    id_signataire = fields.Many2one('hr.employee',string="Signataire")
    your_date_field = fields.Date(string='Your string', default=datetime.today())

    document = fields.Binary(string="Document", readonly=True)
    mois = fields.Integer(string="Combien de mois")

    # field_year = fields.Selection(list1,
    #             required=True, store=True, string="Date", tracking=True)
    type_date_fin = fields.Selection([
        ('date_fin', 'Fin de contrat'),
        ('autre', 'AUTRE')
        ],
        string='Type', required=True, )
    date_fin = fields.Date(string="Date du dernier jour de travail")
    date_reprise = fields.Date(string="Date de reprise")


    @api.model
    def def_ats_excel(self):

        wb_obj = openpyxl.load_workbook('/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats.xlsx')
        sheet_obj = wb_obj.active



        # for i in employee:
        c3 = sheet_obj['C21']
        c3.value = self.id_emp.last_name
        c2 = sheet_obj['D24']
        c2.value = self.id_emp.first_name
        c4 = sheet_obj['N22']
        c4.value = self.id_emp.registration_number
        c5 = sheet_obj['E26']
        c5.value = self.id_emp.birthday
        c6 = sheet_obj['L27']
        c6.value = self.id_emp.birth_commune_id.name
 
        c7 = sheet_obj['E29']
        c7.value = self.id_emp.job_id.name
        c8 = sheet_obj['D28']
        c8.value = self.id_emp.street

        c10 = sheet_obj['F11']
        c10.value =self.id_emp.company_id.name

        c11 = sheet_obj['D16']
        c11.value = self.id_emp.company_id.street
        #
        #     rub_paie = self.env['hr.payslip'].search(
        #         [])

        employee = self.env['hr.contract'].search([('employee_id.id','=',self.id_emp.id)])
        c9 = sheet_obj['Q36']
        c9.value = employee.date_start


        if self.type_date_fin == 'date_fin':
            date_fin = employee.date_end
            date_fin_year = date_fin.strftime('%Y')
            date_fin_month = date_fin.strftime('%m')
            date_fin_year=int(date_fin_year)
            date_fin_month=int(date_fin_month)
            c12 = sheet_obj['Q39']
            c12.value = employee.date_end

            if date_fin_month == 1:
                date_fin_month=12
                date_fin_year-=1
            else :
                date_fin_month -=1
            self.mois-=1
            
            source = wb_obj.get_sheet_by_name('ATS-P2')
            ai21 = source['AI21']
            ai21.value = self.your_date_field
            ap21 = source['AP21']
            ap21.value = self.id_emp.work_location_id.name
            aj25 = source['AJ25']
            aj25.value = self.id_signataire.name
            a = source['A7']
            a.value = str(date_fin_year)+"-"+str(date_fin_month)
            date_spes = str(date_fin_year) + "-" + str(date_fin_month)
            
            date_spes = datetime.strptime(date_spes, '%Y-%m')
            
            date_spes = date_spes.strftime('%Y-%m')
            paie = self.env['hr.payslip'].search(
                [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
            
            b = source['K7']
            for line in paie.worked_days_line_ids:
                if line.work_entry_type_id.code == 'WORK100':
                    b.value = line.number_of_days
                    break
                for line in paie.line_ids:
                    if line.code == 'GROSS':
                        total_ac = line.total
                        d = source['AE7']
                        d.value = total_ac
                    if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                        total_cd = line.total + total_ac
                        d = source['AO7']
                        d.value = total_cd

            if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month=12
                        date_fin_year-=1

                    else :
                        date_fin_month -=1
                    self.mois-=1
                    date_spes=str(date_fin_year)+"-"+str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes,'%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                    a = source['A8']
                    a.value = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    b = source['K8']
                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code== 'WORK100':
                            b.value= line.number_of_days
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            d = source['AE8']
                            d.value = total_ac
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            d = source['AO8']
                            d.value = total_cd


            if self.mois > 0:
                if date_fin_month == 1:
                    date_fin_month = 12
                    date_fin_year -= 1

                else:
                    date_fin_month -= 1
                self.mois-=1
                a = source['A9']
                a.value = str(date_fin_year) + "-" + str(date_fin_month)
                date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                
                date_spes = datetime.strptime(date_spes, '%Y-%m')
                
                date_spes = date_spes.strftime('%Y-%m')
                paie = self.env['hr.payslip'].search(
                    [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                
                b = source['K9']
                for line in paie.worked_days_line_ids:
                    if line.work_entry_type_id.code == 'WORK100':
                        b.value = line.number_of_days
                    break
                for line in paie.line_ids:
                    if line.code == 'GROSS':
                        total_ac = line.total
                        d = source['AE9']
                        d.value = total_ac
                    if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                        total_cd = line.total + total_ac
                        d = source['AO9']
                        d.value = total_cd
            if self.mois > 0:
                if date_fin_month == 1:
                    date_fin_month = 12
                    date_fin_year -= 1

                else:
                    date_fin_month -= 1
                self.mois -= 1
                a = source['A10']
                a.value = str(date_fin_year) + "-" + str(date_fin_month)
                date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                
                date_spes = datetime.strptime(date_spes, '%Y-%m')
                
                date_spes = date_spes.strftime('%Y-%m')
                paie = self.env['hr.payslip'].search(
                    [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                
                b = source['K10']
                for line in paie.worked_days_line_ids:
                    if line.work_entry_type_id.code == 'WORK100':
                        b.value = line.number_of_days
                    break
                for line in paie.line_ids:
                    if line.code == 'GROSS':
                        total_ac = line.total
                        d = source['AE10']
                        d.value = total_ac
                    if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                        total_cd = line.total + total_ac
                        d = source['AO10']
                        d.value = total_cd
            if self.mois > 0:
                if date_fin_month == 1:
                    date_fin_month = 12
                    date_fin_year -= 1

                else:
                    date_fin_month -= 1
                self.mois -= 1
                a = source['A11']
                a.value = str(date_fin_year) + "-" + str(date_fin_month)
                date_spes = str(date_fin_year) + "-" + str(date_fin_month)
              
                date_spes = datetime.strptime(date_spes, '%Y-%m')
              
                date_spes = date_spes.strftime('%Y-%m')
                paie = self.env['hr.payslip'].search(
                    [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
          
                b = source['K11']
                for line in paie.worked_days_line_ids:
                    if line.work_entry_type_id.code == 'WORK100':
                        b.value = line.number_of_days
                    break
                for line in paie.line_ids:
                    if line.code == 'GROSS':
                        total_ac = line.total
                        d = source['AE11']
                        d.value = total_ac
                    if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                        total_cd = line.total + total_ac
                        d = source['AO11']
                        d.value = total_cd
            if self.mois > 0:
                if date_fin_month == 1:
                    date_fin_month = 12
                    date_fin_year -= 1

                else:
                    date_fin_month -= 1
                self.mois -= 1
                a = source['A12']
                a.value = str(date_fin_year) + "-" + str(date_fin_month)
                date_spes = str(date_fin_year) + "-" + str(date_fin_month)
             
                date_spes = datetime.strptime(date_spes, '%Y-%m')
                
                date_spes = date_spes.strftime('%Y-%m')
                paie = self.env['hr.payslip'].search(
                    [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                
                b = source['K12']
                for line in paie.worked_days_line_ids:
                    if line.work_entry_type_id.code == 'WORK100':
                        b.value = line.number_of_days
                    break
                for line in paie.line_ids:
                    if line.code == 'GROSS':
                        total_ac = line.total
                        d = source['AE12']
                        d.value = total_ac
                    if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                        total_cd = line.total + total_ac
                        d = source['AO12']
                        d.value = total_cd
            if self.mois > 0:
                if date_fin_month == 1:
                    date_fin_month = 12
                    date_fin_year -= 1

                else:
                    date_fin_month -= 1
                self.mois -= 1
                a = source['A13']
                a.value = str(date_fin_year) + "-" + str(date_fin_month)
                date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                
                date_spes = datetime.strptime(date_spes, '%Y-%m')
                
                date_spes = date_spes.strftime('%Y-%m')
                paie = self.env['hr.payslip'].search(
                    [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                
                b = source['K13']
                for line in paie.worked_days_line_ids:
                    if line.work_entry_type_id.code == 'WORK100':
                        b.value = line.number_of_days
                    break
                for line in paie.line_ids:
                    if line.code == 'GROSS':
                        total_ac = line.total
                        d = source['AE13']
                        d.value = total_ac
                    if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                        total_cd = line.total + total_ac
                        d = source['AO13']
                        d.value = total_cd

            if self.mois > 0:
                if date_fin_month == 1:
                    date_fin_month = 12
                    date_fin_year -= 1

                else:
                    date_fin_month -= 1
                self.mois -= 1
                a = source['A14']
                a.value = str(date_fin_year) + "-" + str(date_fin_month)
                date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                
                date_spes = datetime.strptime(date_spes, '%Y-%m')
                
                date_spes = date_spes.strftime('%Y-%m')
                paie = self.env['hr.payslip'].search(
                    [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                
                b = source['K14']
                for line in paie.worked_days_line_ids:
                    if line.work_entry_type_id.code == 'WORK100':
                        b.value = line.number_of_days
                    break
                for line in paie.line_ids:
                    if line.code == 'GROSS':
                        total_ac = line.total
                        d = source['AE14']
                        d.value = total_ac
                    if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                        total_cd = line.total + total_ac
                        d = source['AO14']
                        d.value = total_cd

            if self.mois > 0:
                if date_fin_month == 1:
                    date_fin_month = 12
                    date_fin_year -= 1

                else:
                    date_fin_month -= 1
                self.mois -= 1
                a = source['A15']
                a.value = str(date_fin_year) + "-" + str(date_fin_month)
                date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                
                date_spes = datetime.strptime(date_spes, '%Y-%m')
                
                date_spes = date_spes.strftime('%Y-%m')
                paie = self.env['hr.payslip'].search(
                    [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                
                b = source['K15']
                for line in paie.worked_days_line_ids:
                    if line.work_entry_type_id.code == 'WORK100':
                        b.value = line.number_of_days
                    break
                for line in paie.line_ids:
                    if line.code == 'GROSS':
                        total_ac = line.total
                        d = source['AE15']
                        d.value = total_ac
                    if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                        total_cd = line.total + total_ac
                        d = source['AO15']
                        d.value = total_cd
            if self.mois > 0:
                if date_fin_month == 1:
                    date_fin_month = 12
                    date_fin_year -= 1

                else:
                    date_fin_month -= 1
                self.mois -= 1
                a = source['A16']
                a.value = str(date_fin_year) + "-" + str(date_fin_month)
                date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                
                date_spes = datetime.strptime(date_spes, '%Y-%m')
                
                date_spes = date_spes.strftime('%Y-%m')
                paie = self.env['hr.payslip'].search(
                    [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                
                b = source['K16']
                for line in paie.worked_days_line_ids:
                    if line.work_entry_type_id.code == 'WORK100':
                        b.value = line.number_of_days
                    break
                for line in paie.line_ids:
                    if line.code == 'GROSS':
                        total_ac = line.total
                        d = source['AE16']
                        d.value = total_ac
                    if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                        total_cd = line.total + total_ac
                        d = source['AO16']
                        d.value = total_cd

            if self.mois > 0:
                if date_fin_month == 1:
                    date_fin_month = 12
                    date_fin_year -= 1

                else:
                    date_fin_month -= 1
                self.mois -= 1
                a = source['A17']
                a.value = str(date_fin_year) + "-" + str(date_fin_month)
                date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                
                date_spes = datetime.strptime(date_spes, '%Y-%m')
                
                date_spes = date_spes.strftime('%Y-%m')
                paie = self.env['hr.payslip'].search(
                    [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                
                b = source['K17']
                for line in paie.worked_days_line_ids:
                    if line.work_entry_type_id.code == 'WORK100':
                        b.value = line.number_of_days
                    break
                for line in paie.line_ids:
                    if line.code == 'GROSS':
                        total_ac = line.total
                        d = source['AE17']
                        d.value = total_ac
                    if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                        total_cd = line.total + total_ac
                        d = source['AO17']
                        d.value = total_cd

            if self.mois > 0:
                if date_fin_month == 1:
                    date_fin_month = 12
                    date_fin_year -= 1

                else:
                    date_fin_month -= 1
                self.mois -= 1
                a = source['A18']
                a.value = str(date_fin_year) + "-" + str(date_fin_month)
                date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                
                date_spes = datetime.strptime(date_spes, '%Y-%m')
                
                date_spes = date_spes.strftime('%Y-%m')
                paie = self.env['hr.payslip'].search(
                    [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                
                b = source['K18']
                for line in paie.worked_days_line_ids:
                    if line.work_entry_type_id.code == 'WORK100':
                        b.value = line.number_of_days
                    break
                for line in paie.line_ids:
                    if line.code == 'GROSS':
                        total_ac = line.total
                        d = source['AE18']
                        d.value = total_ac
                    if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                        total_cd = line.total + total_ac
                        d = source['AO18']
                        d.value = total_cd
            if self.mois > 0:
                if date_fin_month == 1:
                    date_fin_month = 12
                    date_fin_year -= 1

                else:
                    date_fin_month -= 1
                self.mois -= 1
                a = source['A19']
                a.value = str(date_fin_year) + "-" + str(date_fin_month)
                date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                
                date_spes = datetime.strptime(date_spes, '%Y-%m')
                
                date_spes = date_spes.strftime('%Y-%m')
                paie = self.env['hr.payslip'].search(
                    [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                
                b = source['K19']
                for line in paie.worked_days_line_ids:
                    if line.work_entry_type_id.code == 'WORK100':
                        b.value = line.number_of_days
                    break
                for line in paie.line_ids:
                    if line.code == 'GROSS':
                        total_ac=line.total
                        d = source['AE19']
                        d.value = total_ac
                    if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                        total_cd = line.total +total_ac
                        d = source['AO19']
                        d.value = total_cd
        else:
            if self.type_date_fin == 'autre':
                c13 = sheet_obj['Q39']
                c13.value = self.date_fin
                c14 = sheet_obj['Q42']
                c14.value = self.date_reprise

                date_fin = self.date_fin
                date_fin_year = date_fin.strftime('%Y')
                date_fin_month = date_fin.strftime('%m')
                date_fin_year = int(date_fin_year)
                date_fin_month = int(date_fin_month)

                if date_fin_month == 1:
                    date_fin_month = 12
                    date_fin_year -= 1
                else:
                    date_fin_month -= 1
                self.mois -= 1

                source = wb_obj.get_sheet_by_name('ATS-P2')
                a = source['A7']
                a.value = str(date_fin_year) + "-" + str(date_fin_month)
                date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                
                date_spes = datetime.strptime(date_spes, '%Y-%m')
                
                date_spes = date_spes.strftime('%Y-%m')
                paie = self.env['hr.payslip'].search(
                    [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                
                b = source['K7']
                for line in paie.worked_days_line_ids:
                    if line.work_entry_type_id.code == 'WORK100':
                        b.value = line.number_of_days
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            d = source['AE7']
                            d.value = total_ac
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            d = source['AO7']
                            d.value = total_cd

                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1

                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                    a = source['A8']
                    a.value = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    b = source['K8']
                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            b.value = line.number_of_days
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            d = source['AE8']
                            d.value = total_ac
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            d = source['AO8']
                            d.value = total_cd

                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1

                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    a = source['A9']
                    a.value = str(date_fin_year) + "-" + str(date_fin_month)
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                    
                    b = source['K9']
                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            b.value = line.number_of_days
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            d = source['AE9']
                            d.value = total_ac
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            d = source['AO9']
                            d.value = total_cd
                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1

                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    a = source['A10']
                    a.value = str(date_fin_year) + "-" + str(date_fin_month)
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                    
                    b = source['K10']
                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            b.value = line.number_of_days
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            d = source['AE10']
                            d.value = total_ac
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            d = source['AO10']
                            d.value = total_cd
                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1

                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    a = source['A11']
                    a.value = str(date_fin_year) + "-" + str(date_fin_month)
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                    
                    b = source['K11']
                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            b.value = line.number_of_days
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            d = source['AE11']
                            d.value = total_ac
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            d = source['AO11']
                            d.value = total_cd
                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1

                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    a = source['A12']
                    a.value = str(date_fin_year) + "-" + str(date_fin_month)
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                    
                    b = source['K12']
                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            b.value = line.number_of_days
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            d = source['AE12']
                            d.value = total_ac
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            d = source['AO12']
                            d.value = total_cd
                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1

                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    a = source['A13']
                    a.value = str(date_fin_year) + "-" + str(date_fin_month)
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                    
                    b = source['K13']
                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            b.value = line.number_of_days
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            d = source['AE13']
                            d.value = total_ac
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            d = source['AO13']
                            d.value = total_cd

                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1

                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    a = source['A14']
                    a.value = str(date_fin_year) + "-" + str(date_fin_month)
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                    
                    b = source['K14']
                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            b.value = line.number_of_days
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            d = source['AE14']
                            d.value = total_ac
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            d = source['AO14']
                            d.value = total_cd

                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1

                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    a = source['A15']
                    a.value = str(date_fin_year) + "-" + str(date_fin_month)
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                    
                    b = source['K15']
                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            b.value = line.number_of_days
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            d = source['AE15']
                            d.value = total_ac
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            d = source['AO15']
                            d.value = total_cd
                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1

                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    a = source['A16']
                    a.value = str(date_fin_year) + "-" + str(date_fin_month)
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                    
                    b = source['K16']
                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            b.value = line.number_of_days
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            d = source['AE16']
                            d.value = total_ac
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            d = source['AO16']
                            d.value = total_cd

                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1

                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    a = source['A17']
                    a.value = str(date_fin_year) + "-" + str(date_fin_month)
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                    
                    b = source['K17']
                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            b.value = line.number_of_days
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            d = source['AE17']
                            d.value = total_ac
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            d = source['AO17']
                            d.value = total_cd

                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1

                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    a = source['A18']
                    a.value = str(date_fin_year) + "-" + str(date_fin_month)
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                    
                    b = source['K18']
                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            b.value = line.number_of_days
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            d = source['AE18']
                            d.value = total_ac
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            d = source['AO18']
                            d.value = total_cd
                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1

                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    a = source['A19']
                    a.value = str(date_fin_year) + "-" + str(date_fin_month)
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])
                    
                    b = source['K19']
                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            b.value = line.number_of_days
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            d = source['AE19']
                            d.value = total_ac
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            d = source['AO19']
                            d.value = total_cd


        wb_obj.save("/home/odoo/exportation/ats.xlsx")

        os.system("start  /home/odoo/exportation/ats.xlsx")

    @api.model
    def def_ats_pdf(self):
        # paie = self.env['hr.payslip'].search(
        #     [('date_from', 'like', self.field_year), ('employee_id.id', '=', self.id_emp.id)])

        data_dict = {
            'untitled1':self.id_emp.company_id.name,
            'untitled3': self.id_emp.company_id.street,
            'untitled4':self.id_emp.company_id.company_registry,
            'untitled5': self.id_emp.name,
            'untitled6': self.id_emp.registration_number,
            'untitled7': self.id_emp.birthday,
            'untitled8': self.id_emp.birth_commune_id.name,
            'untitled10': self.id_emp.street,
            'untitled11':self.id_emp.job_id.name,
            'untitled12': self.id_emp.first_contract_date
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
            '/home/odoo/exportation/ats_verso_merged.pdf',
            data_dict
        )

        if self.type_date_fin == 'date_fin':
            employee = self.env['hr.contract'].search([('employee_id.id', '=', self.id_emp.id)])
            date_fin = employee.date_end
            date_fin_year = date_fin.strftime('%Y')
            date_fin_month = date_fin.strftime('%m')
            date_fin_year = int(date_fin_year)
            date_fin_month = int(date_fin_month)
            if date_fin_month == 1:
                date_fin_month = 12
                date_fin_year -= 1
            else:
                date_fin_month -= 1
            self.mois -= 1
            
            var = str(date_fin_year) + "-" + str(date_fin_month)
            data_dict = {
                'untitled13': employee.date_end,
                'untitled62': var
            }

            fillpdfs.write_fillable_pdf(
                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                '/home/odoo/exportation/ats_verso_merged.pdf',
                data_dict
            )
            date_spes = str(date_fin_year) + "-" + str(date_fin_month)
            
            date_spes = datetime.strptime(date_spes, '%Y-%m')
            
            test = date_spes.strftime('%Y-%m')
            paie = self.env['hr.payslip'].search(
                [('date_from', 'like', test), ('employee_id.id', '=', self.id_emp.id)])
            

            for line in paie.worked_days_line_ids:
                if line.work_entry_type_id.code == 'WORK100':
                    data_dict = {
                        'untitled38': line.number_of_days
                    }

                    fillpdfs.write_fillable_pdf(
                        '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                        '/home/odoo/exportation/ats_verso_merged.pdf',
                        data_dict
                    )
                    break
            for line in paie.line_ids:
                if line.code == 'GROSS':
                    total_ac = line.total
                    data_dict = {
                        'untitled133': total_ac
                    }
                    fillpdfs.write_fillable_pdf(
                        '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                        '/home/odoo/exportation/ats_verso_merged.pdf',
                        data_dict
                    )
                if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                    total_cd = line.total + total_ac
                    data_dict = {
                        'untitled1000': total_cd
                    }
                    fillpdfs.write_fillable_pdf(
                        '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                        '/home/odoo/exportation/ats_verso_merged.pdf',
                        data_dict
                    )
            if self.mois > 0:

                if date_fin_month == 1:
                    date_fin_month = 12
                    date_fin_year -= 1
                else:
                    date_fin_month -= 1
                self.mois -= 1
                date_spes = str(date_fin_year) + "-" + str(date_fin_month)

                date_spes = datetime.strptime(date_spes, '%Y-%m')
                date_spes = date_spes.strftime('%Y-%m')



                paie = self.env['hr.payslip'].search(
                    [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                for line in paie.worked_days_line_ids:
                    if line.work_entry_type_id.code == 'WORK100':
                        data_dict = {
                            'untitled61': str(date_fin_year) + "-" + str(date_fin_month),
                            'untitled39': line.number_of_days
                        }
                        fillpdfs.write_fillable_pdf(
                        '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                        '/home/odoo/exportation/ats_verso_merged.pdf',
                        data_dict
                    )

                    break
                for line in paie.line_ids:
                    if line.code == 'GROSS':
                        total_ac = line.total
                        data_dict = {
                            'untitled144': total_ac
                        }
                        fillpdfs.write_fillable_pdf(
                        '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                        '/home/odoo/exportation/ats_verso_merged.pdf',
                        data_dict
                    )
                    if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                        total_cd = line.total + total_ac
                        data_dict = {
                            'untitled10001': total_cd
                        }
                        fillpdfs.write_fillable_pdf(
                        '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                        '/home/odoo/exportation/ats_verso_merged.pdf',
                        data_dict
                    )
            if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month=12
                        date_fin_year-=1

                    else :
                        date_fin_month -=1
                    self.mois-=1
                    date_spes=str(date_fin_year)+"-"+str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes,'%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code== 'WORK100':
                            data_dict = {
                                'untitled40': var,
                                'untitled27': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled155': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1002': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
            if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month=12
                        date_fin_year-=1
                    else :
                        date_fin_month -=1
                    self.mois-=1
                    date_spes=str(date_fin_year)+"-"+str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes,'%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code== 'WORK100':
                            data_dict = {
                                'untitled41': var,
                                'untitled53': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled166': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1003': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )

            if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month=12
                        date_fin_year-=1
                    else :
                        date_fin_month -=1
                    self.mois-=1
                    date_spes=str(date_fin_year)+"-"+str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes,'%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code== 'WORK100':
                            data_dict = {
                                'untitled42': var,
                                'untitled54': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled177': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1004': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
            if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month=12
                        date_fin_year-=1
                    else :
                        date_fin_month -=1
                    self.mois-=1
                    date_spes=str(date_fin_year)+"-"+str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes,'%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code== 'WORK100':
                            data_dict = {
                                'untitled44': var,
                                'untitled59': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled188': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1005': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
            if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month=12
                        date_fin_year-=1
                    else :
                        date_fin_month -=1
                    self.mois-=1
                    date_spes=str(date_fin_year)+"-"+str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes,'%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code== 'WORK100':
                            data_dict = {
                                'untitled45': var,
                                'untitled55': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled199': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1006': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
            if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month=12
                        date_fin_year-=1
                    else :
                        date_fin_month -=1
                    self.mois-=1
                    date_spes=str(date_fin_year)+"-"+str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes,'%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code== 'WORK100':
                            data_dict = {
                                'untitled46': var,
                                'untitled58': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled1111': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1007': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
            if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month=12
                        date_fin_year-=1
                    else :
                        date_fin_month -=1
                    self.mois-=1
                    date_spes=str(date_fin_year)+"-"+str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes,'%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code== 'WORK100':
                            data_dict = {
                                'untitled47': var,
                                'untitled57': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled10009': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1008': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
            if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month=12
                        date_fin_year-=1
                    else :
                        date_fin_month -=1
                    self.mois-=1
                    date_spes=str(date_fin_year)+"-"+str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes,'%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code== 'WORK100':
                            data_dict = {
                                'untitled48': var,
                                'untitled56': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled10010': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1009': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
            if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month=12
                        date_fin_year-=1
                    else :
                        date_fin_month -=1
                    self.mois-=1
                    date_spes=str(date_fin_year)+"-"+str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes,'%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code== 'WORK100':
                            data_dict = {
                                'untitled49': var,
                                'untitled43': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled1115': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1010': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
            if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month=12
                        date_fin_year-=1
                    else :
                        date_fin_month -=1
                    self.mois-=1
                    date_spes=str(date_fin_year)+"-"+str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes,'%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code== 'WORK100':
                            data_dict = {
                                'untitled50': var,
                                'untitled51': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled1116': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1011': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                                data_dict
                            )
            data_dict = {
                'somme': '  8 heures  ',
                'date2':  self.your_date_field,
                'date4':  self.id_signataire.name,
                'date3': self.id_emp.work_location_id.name,
            }
            fillpdfs.write_fillable_pdf(
                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                '/home/odoo/exportation/ats_verso_merged.pdf',
                data_dict
            )
        else:
            if self.type_date_fin == 'autre':
                date_fin = self.date_fin
                date_fin_year = date_fin.strftime('%Y')
                date_fin_month = date_fin.strftime('%m')
                date_fin_year=int(date_fin_year)
                date_fin_month=int(date_fin_month)
                if date_fin_month == 1:
                    date_fin_month=12
                    date_fin_year-=1
                else :
                    date_fin_month -=1
                self.mois-=1
                

                data_dict = {
                    'untitled13': self.date_fin,
                    'untitled14':self.date_reprise,
                }
                fillpdfs.write_fillable_pdf(
                    'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                    'C:/Program Files/Odoo 15.0.20220418/server/odoo/addons_report/atlas_house/report/ats_verso_merged.pdf',
                    data_dict
                )
                date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                
                date_spes = datetime.strptime(date_spes, '%Y-%m')
                
                test = date_spes.strftime('%Y-%m')
                paie = self.env['hr.payslip'].search(
                    [('date_from', 'like', test), ('employee_id.id', '=', self.id_emp.id)])
                
                var = str(date_fin_year) + "-" + str(date_fin_month)
                for line in paie.worked_days_line_ids:
                    if line.work_entry_type_id.code == 'WORK100':
                        data_dict = {
                            'untitled62': var,
                            'untitled38': line.number_of_days
                        }
                        fillpdfs.write_fillable_pdf(
                        '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                        '/home/odoo/exportation/ats_verso_merged.pdf',
                        data_dict
                        )
                        break
                for line in paie.line_ids:
                    if line.code == 'GROSS':
                        total_ac = line.total
                        data_dict = {
                            'untitled133': total_ac
                        }
                        fillpdfs.write_fillable_pdf(
                        '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                        '/home/odoo/exportation/ats_verso_merged.pdf',
                        data_dict
                        )
                    if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                        total_cd = line.total + total_ac
                        data_dict = {
                            'untitled1000': total_cd
                        }
                        fillpdfs.write_fillable_pdf(
                        '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                        '/home/odoo/exportation/ats_verso_merged.pdf',
                        data_dict
                        )
                if self.mois > 0:

                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1
                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)

                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    date_spes = date_spes.strftime('%Y-%m')

                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            data_dict = {
                                'untitled61': str(date_fin_year) + "-" + str(date_fin_month),
                                'untitled39': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )

                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled144': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled10001': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1

                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            data_dict = {
                                'untitled40': var,
                                'untitled27': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled155': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1002': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1
                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            data_dict = {
                                'untitled41': var,
                                'untitled53': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled166': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1003': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1
                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            data_dict = {
                                'untitled42': var,
                                'untitled54': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled177': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1004': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1
                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            data_dict = {
                                'untitled44': var,
                                'untitled59': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled188': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1005': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1
                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            data_dict = {
                                'untitled45': var,
                                'untitled55': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled199': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1006': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1
                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            data_dict = {
                                'untitled46': var,
                                'untitled58': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled1111': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1007': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1
                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            data_dict = {
                                'untitled47': var,
                                'untitled57': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled10009': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1008': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1
                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            data_dict = {
                                'untitled48': var,
                                'untitled56': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled10010': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1009': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1
                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                    

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            data_dict = {
                                'untitled49': var,
                                'untitled43': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled1115': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1010': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                if self.mois > 0:
                    if date_fin_month == 1:
                        date_fin_month = 12
                        date_fin_year -= 1
                    else:
                        date_fin_month -= 1
                    self.mois -= 1
                    date_spes = str(date_fin_year) + "-" + str(date_fin_month)
                    
                    date_spes = datetime.strptime(date_spes, '%Y-%m')
                    
                    date_spes = date_spes.strftime('%Y-%m')
                    paie = self.env['hr.payslip'].search(
                        [('date_from', 'like', date_spes), ('employee_id.id', '=', self.id_emp.id)])

                    var = str(date_fin_year) + "-" + str(date_fin_month)

                 

                    for line in paie.worked_days_line_ids:
                        if line.work_entry_type_id.code == 'WORK100':
                            data_dict = {
                                'untitled50': var,
                                'untitled51': line.number_of_days
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        break
                    for line in paie.line_ids:
                        if line.code == 'GROSS':
                            total_ac = line.total
                            data_dict = {
                                'untitled1116': total_ac
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                        if line.code == 'R401' or line.code == 'R407' or line.code == 'R403':
                            total_cd = line.total + total_ac
                            data_dict = {
                                'untitled1011': total_cd
                            }
                            fillpdfs.write_fillable_pdf(
                                '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                                '/home/odoo/exportation/ats_verso_merged.pdf',
                                data_dict
                            )
                data_dict = {
                    'somme': '  8 heures  ',
                    'date2': self.your_date_field,
                    'date4': self.id_signataire.name,
                    'date3': self.id_emp.work_location_id.name,
                }
                fillpdfs.write_fillable_pdf(
                    '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
                    '/home/odoo/exportation/ats_verso_merged.pdf',
                    data_dict
                )
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/l10n_dz_payroll/report/ats_verso_merged.pdf',
            '/home/odoo/exportation/ats_verso_merged.pdf',
            data_dict
        )

        file = open("/home/odoo/exportation/ats_verso_merged.pdf",
                    "rb")
        out = file.read()
        file.close()
        self.document = base64.b64encode(out)




    def init_ats_excel(self):
        self.def_ats_excel()


    def init_ats_pdf(self):
        self.def_ats_pdf()


