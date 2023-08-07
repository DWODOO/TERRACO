# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA

from odoo import models, fields, api, _
import xlwt
import io
from io import StringIO
import base64
from xlwt import easyxf
import datetime


class PayrollTransfer(models.TransientModel):
    _name = "hr.payroll.transfer"
    
    @api.model
    def _get_from_date(self):
        company = self.env.user.company_id
        current_date = datetime.date.today()
        from_date = company.compute_fiscalyear_dates(current_date)['date_from']
        return from_date
    
    date_start = fields.Date(related='payslip_run_id.date_start')
    date_end = fields.Date(related='payslip_run_id.date_end')
    transfer_file = fields.Binary('File')
    file_name = fields.Char('File Name')
    transfer_report_printed = fields.Boolean('Transfer')
    payslip_run_id = fields.Many2one('hr.payslip.run', string='Payslip Batches', required=True)

    def action_hr_payroll_transfer(self):
        workbook = xlwt.Workbook()
        column_heading_style = easyxf('font:height 200;font:bold True;')
        worksheet = workbook.add_sheet(_("Transfer"))
        worksheet.write(0, 0, _("Employee"), easyxf('font:height 200;font:bold True;'))
        worksheet.write(0, 1, _("Code"), column_heading_style)
        worksheet.write(0, 2, _("Agency"), column_heading_style)
        worksheet.write(0, 3, _("Account number"), column_heading_style)
        worksheet.write(0, 4, _("Key"), column_heading_style)
        worksheet.write(0, 5, _("Net Salary"), column_heading_style)
        worksheet.col(0).width = 8000
        worksheet.col(1).width = 4000
        worksheet.col(2).width = 4000
        worksheet.col(3).width = 4000
        worksheet.col(4).width = 2000
        worksheet.col(5).width = 4000

        row = 1
        for payslip in self.payslip_run_id.slip_ids.filtered(lambda p: p.state == 'done'):
                acc = payslip.employee_id.bank_account_id.acc_number
                worksheet.write(row, 0, payslip.employee_id.name)
                if acc:
                    worksheet.write(row, 1, acc[:3])
                    worksheet.write(row, 2, acc[3:8])
                    worksheet.write(row, 3, acc[8:18])
                    worksheet.write(row, 4, acc[-2:])
                else:
                    worksheet.write(row, 1, "")
                    worksheet.write(row, 2, "")
                    worksheet.write(row, 3, "")
                    worksheet.write(row, 4, "")

                worksheet.write(row, 5, payslip.net_salary)
                row += 1
        fp = StringIO()
        fp = io.BytesIO()
        workbook.save(fp)
        excel_file = base64.encodestring(fp.getvalue())
        self.transfer_file = excel_file
        self.file_name = _('Transfers.xls')
        self.transfer_report_printed = True
        fp.close()

        return {
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'hr.payroll.transfer',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'target': 'new'
        }