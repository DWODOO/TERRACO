from odoo import api, fields, models, _
from fillpdf import fillpdfs
from odoo.exceptions import ValidationError
import time
import PyPDF2
from datetime import datetime
import webbrowser as wb


import base64

cnt=10
list1=[]
for i in range(2010,datetime.today().year+1):
         list1.append((str(cnt),str(i)))
         cnt=cnt+1
print(list1)

class ResultFiscallist(models.Model):
    _name = 'smartest_bilan.resultat_fis'
    _description = 'Import Export Mat'
    rec_name = 'name_seq'

    @api.model
    def create(self, vals):
        if vals.get('name_seq', 'New') == 'New':
            vals['name_seq'] = self.env['ir.sequence'].next_by_code(
                'smartest.bilan.resultat.fis.sequence') or 'New'
            print(vals['name_seq'])
        result = super(ResultFiscallist, self).create(vals)
        return result

    name_fis = fields.Char(
        string="Name"
    )
    name = fields.Char(
    )


    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env['res.company'].search([],limit=1))
    company_name = fields.Char(
        related="company_id.name"
    )
    def set_company(self, company_name, Des_entreprise):
        data_dict = {
            Des_entreprise: (f'{int(company_name):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    date_year_id = fields.Selection(list1,
                            required=True, store=True, string="Exercice", tracking=True)

    date_char= fields.Char(
        compute="_def_date",
        store=True
    )
    date_int_1 = fields.Integer(
        compute="_def_date",
        store=True
    )
    date_str_1 = fields.Char(
        compute="_def_date",
        store=True
    )
    date_int_2 = fields.Integer(
        compute="_def_date",
        store=True
    )
    date_str_2 = fields.Char(
        compute="_def_date",
        store=True
    )
    date_int_3 = fields.Integer(
        compute="_def_date",
        store=True
    )
    date_str_3 = fields.Char()
    date_int_4 = fields.Integer(
        compute="_def_date",
        store=True
    )
    date_str_4 = fields.Char(
        compute="_def_date",
        store=True
    )

    # @api.onchange("date_year_id")
    def _get_def_date(self):
        for this in self:
            this.date_char = dict(this._fields['date_year_id'].selection).get(this.date_year_id)
            return this.date_char

    @api.onchange("date_year_id")
    def _def_date(self):
        for rec in self:
            date_1= int(rec._get_def_date())
            date_1-=2001
            date_str = str(date_1)
            if len(date_str)==2:
                self.date_str_1 = date_str
                print(self.date_str_1)
            else:
                if len(date_str)==1:
                    date_st='0'+date_str
                    print(date_st)
                    self.date_str_1 = date_st
                    print(self.date_str_1)
            date_2 = int(rec._get_def_date())
            date_2 -= 2002
            date_s = str(date_2)
            if len(date_s)==2:
                self.date_str_2 = date_s
                print(self.date_str_2)
            else:
                if len(date_s)==1:
                    date_st_with='0'+date_s
                    print(date_st_with)
                    self.date_str_2 = date_st_with
                    print(self.date_str_2)
            date_3 = int(rec._get_def_date())
            date_3 -= 2003
            date_var = str(date_3)
            if len(date_var) == 2:
                self.date_str_3 = date_var
                print(self.date_str_3)
            else:
                if len(date_var) == 1:
                    date_st_with_0 = '0' + date_var
                    print(date_st_with_0)
                    self.date_str_3 = date_st_with_0
                    print(self.date_str_3)
            date_4 = int(rec._get_def_date())
            date_4 -= 2004
            date_var_1 = str(date_4)
            if len(date_var_1) == 2:
                self.date_str_4 = date_var_1
                print(self.date_str_4)
            else:
                if len(date_var_1) == 1:
                    date_st_with_0_ = '0' + date_var_1
                    print(date_st_with_0_)
                    self.date_str_4 = date_st_with_0_
                    print(self.date_str_4)

            data_dict = {
                'an1':self.date_str_4,
                'an2':self.date_str_3,
                'an3': self.date_str_2,
                'an4': self.date_str_1,
            }
            fillpdfs.write_fillable_pdf(
                '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
                '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
                data_dict)


    document = fields.Binary(string="Document", readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('count', 'Counted'),
        ('cancel', 'Rejected')
    ], default='draft', string="State", readonly=True, tracking=True)

    name_seq = fields.Char(string="Reference", required=True, copy=False, readonly=True, index=True,
                           default='NEW')


    resultfiscal_ids = fields.One2many('smartest_bilan.resultat_fiscal',  'resultfiscal_id' ,ondelet="cascade")

    total_reintegration = fields.Integer(
        string="Total reinstatements",
         compute="_total_reintegration",
         store="True"
    )
    total_deduction = fields.Integer(
        string="Total deductions",
        compute="_total_deduc",
        store="True"
    )
    total_deficit = fields.Integer(
        string="Total deficits to be deducted",
        compute="_total_deficit",
        store="True"
    )
    total_ben = fields.Integer(
        compute="_total_benifice_profits",
        store="True"
    )
    total_perte = fields.Integer(
        compute="_total_perte",
        store="True"
    )
    total_benefice = fields.Integer(
        string="Profits",
        compute="_total_benef_deficit",
        store="True"
    )
    total_déficit_fis = fields.Integer(
        string="Deficits",
        compute="_total_benef_deficit",
        store="True"
    )




    @api.onchange('resultfiscal_ids')
    def _total_reintegration(self):
        for record in self:
            record.total_reintegration = 0
            i=0
            for line in record.resultfiscal_ids:
                i+=1
                if line.catego == "Reintegration":
                        record.total_reintegration += line.total
                else:
                    if i==19:
                        break

    @api.onchange('resultfiscal_ids')
    def _total_deduc(self):
        for record in self:
            record.total_deduction = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if line.catego == "Déduction" and i > 18:
                    record.total_deduction += line.total
                if i == 26:
                    break

    @api.onchange('resultfiscal_ids')
    def _total_deficit(self):
        for record in self:
            record.total_deficit=0
            i=0
            for line in record.resultfiscal_ids:
                i+=1
                if line.catego == "Deficit anterieur" and i>25:
                    record.total_deficit += line.total
                if i==30:
                    break

    @api.onchange('resultfiscal_ids')
    def _total_benifice_profits(self):
        for record in self:
            record.total_ben = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i==1:
                    record.total_ben += line.total
                    break

    @api.onchange('resultfiscal_ids')
    def _total_perte(self):
        for record in self:
            record.total_perte = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 2:
                    record.total_perte += line.total
                    print(record.total_perte)
                    break

    def set_total_perte(self, total_perte, RR2):
        data_dict = {
            RR2: (f'{int(total_perte):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    @api.onchange('total_deficit','total_deduction','total_reintegration','total_ben')
    def _total_benef_deficit(self):
        for record in self:
            total = 0
            total = total + record.total_ben + record.total_reintegration - record.total_deduction - record.total_deficit
            if total > 0:
                record.total_benefice = total
                record.total_déficit_fis =0
            else:
                if total < 0:
                    record.total_déficit_fis = total
                    record.total_benefice=0


    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
    def action_count(self):
        for record in self:
            record.state = "count"

    _sql_constraints = [
        (
            'year_unique',
            'UNIQUE(date_year_id)',
            'date exists !'
        ),
    ]

    def name_get(self):
        result = []
        for field in self:
            result.append((field.id, field.name_seq))
        return result
    @api.model
    def default_get(self, fields_list):
        # var_check = fields.Boolean(default="false")
        res = super(ResultFiscallist, self).default_get(fields_list)
        resultfiscal_ids = []
        resultat_rec = self.env['smartest_bilan.resultat_fiscal'].search([])
        for result in resultat_rec:
            line = (0, 0,
                    {'name': result.name,
                     'catego': result.catego}
                    )
            if len(resultfiscal_ids) == 29:
                break
            print(len(resultfiscal_ids))
            resultfiscal_ids.append(line)
        res.update({'resultfiscal_ids': resultfiscal_ids})
        return res
    def set_date_du(self, date_year_id,Exercice ):
        data_dict = {
            'Exercice': '01/01/20'+date_year_id,
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    def set_date_au(self, date_year_id, au):
        data_dict = {
            'au': '31/12/20'+date_year_id,
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    def set_total_déficit(self, total_deficit, Total_DD):
        data_dict = {
            Total_DD: (f'{int(total_deficit):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)
    def set_total_deduction(self, total_deduction, Total_D):
        data_dict = {
            Total_D: (f'{int(total_deduction):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    def set_total_reintegration(self, total_reintegration, Total_R):
        data_dict = {
            Total_R: (f'{int(total_reintegration):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    def set_total_benefice(self,total_benefice , Ben10):
        data_dict = {
            Ben10: (f'{int(total_benefice):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)
    def set_total_defici_fis(self,total_déficit_fis , Def10):
        data_dict = {
            Def10: (f'{int(total_déficit_fis):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    def set_result_benifice(self, total_ben, RR1):
            data_dict = {
                RR1: (f'{int(total_ben):,}').replace(",", " "),
            }
            fillpdfs.write_fillable_pdf(
                '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
                '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
                data_dict)



    total_3 = fields.Integer(
        compute="_def_total_3",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_3(self):
        for record in self:
            record.total_3 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i+=1
                if i==3:
                    record.total_3 += line.total
                    break

    def set_result_r1(self, total_3, R1):
        data_dict = {
            R1: (f'{int(total_3):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)


    total_4 = fields.Integer(
        compute="_def_total_4",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_4(self):
        for record in self:
            record.total_4 = 0
            i=0
            for line in record.resultfiscal_ids:
                i+= 1
                if i==4:
                    record.total_4 += line.total
                    break


    def set_result_r2(self,total_4, R2):
        data_dict = {
            R2: (f'{int(total_4):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_5 = fields.Integer(
        compute="_def_total_5",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_5(self):
        for record in self:
            record.total_5 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 5:
                    record.total_5 += line.total
                    break

    def set_result_r3(self, total_5, R3):
        data_dict = {
            R3: (f'{int(total_5):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_6 = fields.Integer(
        compute="_def_total_6",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_6(self):
        for record in self:
            record.total_6 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 6:
                    record.total_6 += line.total
                    break

    def set_result_r4(self, total_6, R4):
        data_dict = {
            R4: (f'{int(total_6):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_7 = fields.Integer(
        compute="_def_total_7",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_7(self):
        for record in self:
            record.total_7 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 7:
                    record.total_7 += line.total
                    break

    def set_result_r5(self, total_7, R5):
        data_dict = {
            R5: (f'{int(total_7):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_8 = fields.Integer(
        compute="_def_total_8",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_8(self):
        for record in self:
            record.total_8 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 8:
                    record.total_8 += line.total
                    break

    def set_result_r6(self, total_8, R6):
        data_dict = {
            R6: (f'{int(total_8):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_9 = fields.Integer(
        compute="_def_total_9",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_9(self):
        for record in self:
            record.total_9 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 9:
                    record.total_9 += line.total
                    break

    def set_result_r7(self, total_9, R7):
        data_dict = {
            R7: (f'{int(total_9):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_10 = fields.Integer(
        compute="_def_total_10",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_10(self):
        for record in self:
            record.total_10 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 10:
                    record.total_10 += line.total
                    break

    def set_result_r8(self, total_10, R8):
        data_dict = {
            R8: (f'{int(total_10):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_11 = fields.Integer(
        compute="_def_total_11",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_11(self):
        for record in self:
            record.total_11 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 11:
                    record.total_11 += line.total
                    break

    def set_result_r9(self, total_11, R9):
        data_dict = {
            R9: (f'{int(total_11):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_12 = fields.Integer(
        compute="_def_total_12",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_12(self):
        for record in self:
            record.total_12 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 12:
                    record.total_12 += line.total
                    break

    def set_result_r10(self, total_12, R10):
        data_dict = {
            R10: (f'{int(total_12):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_13 = fields.Integer(
        compute="_def_total_13",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_13(self):
        for record in self:
            record.total_13 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 13:
                    record.total_13 += line.total
                    break

    def set_result_r11(self, total_13, R11):
        data_dict = {
            R11: (f'{int(total_13):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_14 = fields.Integer(
        compute="_def_total_14",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_14(self):
        for record in self:
            record.total_14 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 14:
                    record.total_14 += line.total
                    break

    def set_result_r12(self, total_14, R12):
        data_dict = {
            R12: (f'{int(total_14):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_15 = fields.Integer(
        compute="_def_total_15",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_15(self):
        for record in self:
            record.total_15 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 15:
                    record.total_15 += line.total
                    break

    def set_result_r13(self, total_15, R13):
        data_dict = {
            R13: (f'{int(total_15):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_16 = fields.Integer(
        compute="_def_total_16",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_16(self):
        for record in self:
            record.total_16 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 16:
                    record.total_16 += line.total
                    break

    def set_result_r14(self, total_16, R14):
        data_dict = {
            R14: (f'{int(total_16):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_17 = fields.Integer(
        compute="_def_total_17",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_17(self):
        for record in self:
            record.total_17 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 17:
                    record.total_17 += line.total
                    break

    def set_result_r15(self, total_17, R15):
        data_dict = {
            R15: (f'{int(total_17):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_18 = fields.Integer(
        compute="_def_total_18",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_18(self):
        for record in self:
            record.total_18 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 18:
                    record.total_18 += line.total
                    break

    def set_result_r16(self, total_18, R16):
        data_dict = {
            R16: (f'{int(total_18):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_19 = fields.Integer(
        compute="_def_total_19",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_19(self):
        for record in self:
            record.total_19 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 19:
                    record.total_19 += line.total
                    break
    def set_result_d1(self, total_19, D1):
        data_dict = {
            D1: (f'{int(total_19):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_20 = fields.Integer(
        compute="_def_total_20",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_20(self):
        for record in self:
            record.total_20 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 20:
                    record.total_20 += line.total
                    break
    def set_result_d2(self, total_20, D2):
        data_dict = {
            D2: (f'{int(total_20):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_21 = fields.Integer(
        compute="_def_total_21",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_21(self):
        for record in self:
            record.total_21 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 21:
                    record.total_21 += line.total
                    break
    def set_result_d3(self, total_21, D3):
        data_dict = {
            D3: (f'{int(total_21):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_22 = fields.Integer(
        compute="_def_total_22",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_22(self):
        for record in self:
            record.total_22 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 22:
                    record.total_22 += line.total
                    break

    def set_result_d4(self, total_22, D4):
        data_dict = {
            D4: (f'{int(total_22):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_23 = fields.Integer(
        compute="_def_total_23",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_23(self):
        for record in self:
            record.total_23 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 23:
                    record.total_23 += line.total
                    break

    def set_result_d5(self, total_23, D5):
        data_dict = {
            D5: (f'{int(total_23):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_24 = fields.Integer(
        compute="_def_total_24",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_24(self):
        for record in self:
            record.total_24 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 24:
                    record.total_24 += line.total
                    break
    def set_result_d6(self, total_24, D6):
        data_dict = {
            D6: (f'{int(total_24):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_25 = fields.Integer(
        compute="_def_total_25",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_25(self):
        for record in self:
            record.total_25 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 25:
                    record.total_25 += line.total
                    break

    def set_result_d7(self, total_25, D7):
        data_dict = {
            D7: (f'{int(total_25):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_26 = fields.Integer(
        compute="_def_total_26",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_26(self):
        for record in self:
            record.total_26 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 26:
                    record.total_26 += line.total
                    break
    def set_result_D20_1(self, total_26, D20_1):
        data_dict = {
            D20_1: (f'{int(total_26):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_27 = fields.Integer(
        compute="_def_total_27",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_27(self):
        for record in self:
            record.total_27 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 27:
                    record.total_27 += line.total
                    break

    def set_result_D20_2(self, total_27, D20_2):
        data_dict = {
            D20_2: (f'{int(total_27):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_28 = fields.Integer(
        compute="_def_total_28",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_28(self):
        for record in self:
            record.total_28 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 28:
                    record.total_28 += line.total
                    break

    def set_result_D20_3(self, total_28, D20_3):
        data_dict = {
            D20_3: (f'{int(total_28):,}').replace(",", " "),
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)

    total_29 = fields.Integer(
        compute="_def_total_29",
        store="True"
    )

    @api.onchange('resultfiscal_ids')
    def _def_total_29(self):
        for record in self:
            record.total_29 = 0
            i = 0
            for line in record.resultfiscal_ids:
                i += 1
                if i == 29:
                    record.total_29 += line.total
                    break

    def set_result_D20_4(self, total_29, D20_4):
        test_sum = self.env['res.company'].search(
            [], limit=1)
        data_dict = {
            D20_4: (f'{int(total_29):,}').replace(",", ""),
            'NIF': test_sum.fiscal_identification,
            'Des_entreprise': test_sum.name,
            'Adresse': str(test_sum.street)+' '+str(test_sum.street2)+' '+str(test_sum.city),
            'Activite': test_sum.activ
        }
        fillpdfs.write_fillable_pdf(
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            '/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf',
            data_dict)


    def init_doc(self):
        self.set_total_déficit(self.total_deficit,'Total_DD')
        self.set_total_reintegration(self.total_reintegration, 'Total_R')
        self.set_total_deduction(self.total_deduction, 'Total_D')
        self.set_result_benifice(self.total_ben, 'RR1')
        self.set_result_r1(self.total_3, 'R1')
        self.set_result_r2(self.total_4, 'R2')
        self.set_result_r3(self.total_5, 'R3')
        self.set_result_r4(self.total_6, 'R4')
        self.set_result_r5(self.total_7, 'R5')
        self.set_result_r6(self.total_8, 'R6')
        self.set_result_r7(self.total_9, 'R7')
        self.set_result_r8(self.total_10, 'R8')
        self.set_result_r9(self.total_11, 'R9')
        self.set_result_r10(self.total_12, 'R10')
        self.set_result_r11(self.total_13, 'R11')
        self.set_result_r12(self.total_14, 'R12')
        self.set_result_r13(self.total_15, 'R13')
        self.set_result_r14(self.total_16, 'R14')
        self.set_result_r15(self.total_17, 'R15')
        self.set_result_r16(self.total_18, 'R16')
        self.set_result_d1(self.total_19, 'D1')
        self.set_result_d2(self.total_20, 'D2')
        self.set_result_d3(self.total_21, 'D3')
        self.set_result_d4(self.total_22, 'D4')
        self.set_result_d5(self.total_23, 'D5')
        self.set_result_d6(self.total_24, 'D6')
        self.set_result_d7(self.total_25, 'D7')
        self.set_result_D20_1(self.total_26, 'D20_1')
        self.set_result_D20_2(self.total_27, 'D20_2')
        self.set_result_D20_3(self.total_28, 'D20_3')
        self.set_result_D20_4(self.total_29,'D20_4')
        self.set_total_defici_fis(self.total_déficit_fis,'Def10')
        self.set_total_benefice(self.total_benefice,'Ben10')
        self.set_date_du(self.date_year_id,'Exercice')
        self.set_date_au(self.date_year_id, 'au')
        self.set_total_perte(self.total_perte, 'RR2')
        self._def_date()
        file = open("/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf", "rb")
        out = file.read()
        pdf= PyPDF2.PdfFileReader(file)
        file.close()
        self.document = base64.b64encode(out)

        # wb.open_new(r'/home/odoo/repositories/smartest-odoo-app/smartest_bilan_liasse/report/reportpdf.pdf')



