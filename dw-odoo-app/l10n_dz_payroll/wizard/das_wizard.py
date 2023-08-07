import pdb
from datetime import datetime, date
import logging
import base64
import calendar

from odoo import api, models, fields, _

_logger = logging.getLogger(__name__)


def get_correct_value(value, length_value):
    """This function has been used like this in order t optimize the code"""
    if len(value) == length_value:
        return value
    elif len(value) > length_value:
        return value[:length_value]
    else:
        i = len(value)
        while i < length_value:
            value = value + ' '
            i += 1
        return value


def get_correct_date(dates):
    return str(dates.strftime("%d%m%Y"))


def get_trimesters(year_reference):

    first_trimester_dates = [
        date.today().replace(day=1, month=1, year=year_reference),
        date.today().replace(day=1, month=2, year=year_reference),
        date.today().replace(day=1, month=3, year=year_reference),
    ]
    second_trimester_dates = [
        date.today().replace(day=1, month=4, year=year_reference),
        date.today().replace(day=1, month=5, year=year_reference),
        date.today().replace(day=1, month=6, year=year_reference),
    ]
    third_trimester_dates = [
        date.today().replace(day=1, month=7, year=year_reference),
        date.today().replace(day=1, month=8, year=year_reference),
        date.today().replace(day=1, month=9, year=year_reference),
    ]
    fourth_trimester_dates = [
        date.today().replace(day=1, month=10, year=year_reference),
        date.today().replace(day=1, month=11, year=year_reference),
        date.today().replace(day=1, month=12, year=year_reference),
    ]
    fifth_trimester_dates = [
        date.today().replace(day=1, month=1, year=year_reference+1),
        date.today().replace(day=1, month=2, year=year_reference+1),
        date.today().replace(day=1, month=3, year=year_reference+1),
    ]
    return first_trimester_dates, second_trimester_dates, third_trimester_dates, fourth_trimester_dates, fifth_trimester_dates


class DasCnas(models.TransientModel):
    _name = "l10n_dz_payroll.das.cnas.wizard"

    @api.model
    def get_year_references(self):
        year = datetime.today().year
        year -= 30
        return [(str(year + i), str(year + i)) for i in range(300)]

    end_date = fields.Date(
        "Last year date",
        default=datetime.now().replace(month=12, day=31)
    )
    company_cnas_ids = fields.Many2one(
        'res.company.cnas',
        'Employer Number',
        default=lambda self: self.env.company.company_cnas_ids
    )
    declaration_type = fields.Selection(
        [('n', 'N'), ('c', 'C')],
        default='n'
    )
    year_reference = fields.Selection(
        selection='get_year_references',
        default=str(datetime.today().year)
    )
    payer_center = fields.Char(
        'Payer Center',
        compute='_compute_payer_center'
    )
    employer_number = fields.Char(
        'Employer Number',
        compute='_compute_payer_center',
        default='get_default_company_cnas_ids()'
    )
    nomination = fields.Char()
    rs = fields.Char()
    address = fields.Char()

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, required=True)
    total_amount_first_trimester = fields.Monetary(currency_field='currency_id')
    total_amount_second_trimester = fields.Monetary(currency_field='currency_id')
    total_amount_third_trimester = fields.Monetary(currency_field='currency_id')
    total_amount_fourth_trimester = fields.Monetary(currency_field='currency_id')
    total_annual_salaries = fields.Monetary(currency_field='currency_id')
    amount_number_employee = fields.Integer()
    das_header = fields.Html()
    das_lines = fields.Html()
    no_fourth_trimester = fields.Boolean(
        "No Fourth trimester?",
        default=False
    )

    @api.onchange('no_fourth_trimester')
    def onchange_no_fourth_trimester(self):
        self.action_prepare_values()

    @api.depends('company_cnas_ids')
    def _compute_payer_center(self):
        for rec in self:
            if rec.company_cnas_ids:
                rec.employer_number = rec.company_cnas_ids.employer_number
                rec.payer_center = rec.company_cnas_ids.payer_center
            else:
                rec.employer_number = False
                rec.payer_center = False

    def get_amount_by_trimesters(self):

        payslips = self.env['hr.payslip']

        # get trimesters based on the year reference
        first_trimester_dates, second_trimester_dates, third_trimester_dates, fourth_trimester_dates, fifth_trimester_dates = \
            get_trimesters(int(self.year_reference))

        # #total_amount_first_trimester
        self.total_amount_first_trimester = sum_trimester1 = round(
            # sum(payslips.search([('date_from', 'in', first_trimester_dates)]).mapped('post_salary')), 2)
            sum(payslips.search([('date_to', '<', second_trimester_dates[0]), ('date_from', '>=', first_trimester_dates[0])]).mapped('post_salary')), 2)
        # #total_amount_second_trimester
        self.total_amount_second_trimester = sum_trimester2 = round(
            # sum(payslips.search([('date_from', 'in', second_trimester_dates)]).mapped('post_salary')), 2)
            sum(payslips.search([('date_to', '<', third_trimester_dates[0]), ('date_from', '>=', second_trimester_dates[0])]).mapped('post_salary')), 2)
        # #total_amount_third_trimester
        self.total_amount_third_trimester = sum_trimester3 = round(
            # sum(payslips.search([('date_from', 'in', third_trimester_dates)]).mapped('post_salary')), 2)
            sum(payslips.search([('date_to', '<', fourth_trimester_dates[0]), ('date_from', '>=', third_trimester_dates[0])]).mapped('post_salary')), 2)

        # #total_annual_salaries
        if self.no_fourth_trimester:
            self.total_annual_salaries = round(sum([sum_trimester1, sum_trimester2, sum_trimester3]), 2)
        else:
            # #total_amount_fourth_trimester
            self.total_amount_fourth_trimester = sum_trimester4 = round(
                sum(payslips.search([('date_to', '<', fifth_trimester_dates[0]), ('date_from', '>=', fourth_trimester_dates[0])]).mapped('post_salary')), 2)
            self.total_annual_salaries = round(sum([sum_trimester1, sum_trimester2, sum_trimester3, sum_trimester4]), 2)

    def get_value_in_cents(self, value):
        return round(value*100)

    @api.onchange('year_reference')
    def onchange_year_reference(self):
        self.action_prepare_values()

    def get_header(self, path):
        """
            This function returns the header needed for cnas, it'll we be the resumed declaration of the company
            that the lines would need to match.
        """
        header_details = get_correct_value(str(self.employer_number) if self.employer_number else '', 10) + \
             get_correct_value(str(self.declaration_type).upper() if self.declaration_type else '', 1) + \
             get_correct_value(str(self.year_reference) if self.year_reference else '', 4) + \
             get_correct_value(str(self.payer_center) if self.payer_center else '', 5) + \
             get_correct_value(str(self.nomination) if self.nomination else '', 30) + \
             get_correct_value(str(self.rs) if self.rs else '', 30) + \
             get_correct_value(str(self.address) if self.address else '', 50) + \
             get_correct_value(
                 str(self.get_value_in_cents(self.total_amount_first_trimester))
                 if self.total_amount_first_trimester else '', 16) + \
             get_correct_value(
                 str(self.get_value_in_cents(self.total_amount_second_trimester))
                 if self.total_amount_second_trimester else '', 16) + \
             get_correct_value(
                 str(self.get_value_in_cents(self.total_amount_third_trimester))
                 if self.total_amount_third_trimester else '', 16)

        if self.no_fourth_trimester:
            header_details = header_details + get_correct_value('0', 16)
        else:
            header_details = header_details + get_correct_value(
                str(self.get_value_in_cents(self.total_amount_fourth_trimester))
                if self.total_amount_fourth_trimester else '', 16)

        header_details = header_details + get_correct_value(
                str(self.get_value_in_cents(self.total_annual_salaries)) if self.total_annual_salaries else '', 16) + \
            get_correct_value(str(self.amount_number_employee) if self.amount_number_employee else '', 6)

        self.das_header = header_details

    def get_worked_time_by_trimester(self, payslips, employee_id, trimester, next_trimester):

        employee_payslips = payslips.filtered(lambda o: o if o.employee_id == employee_id else [])
        # attendance_id = self.env.ref('l10n_be_hr_payroll.work_entry_type_attendance').id
        employee_trimester = employee_payslips.filtered(
            lambda o: o if o.date_to <= next_trimester[0] and o.date_from >= trimester[0] else None)
        if len(employee_trimester.worked_days_line_ids) == 1:
            res = sum(employee_trimester.mapped('worked_days_line_ids.number_of_hours'))
        else:
            absence_id = self.env.ref('l10n_dz_payroll.hr_absence_work_entry').id
            legal_leave_id = self.env.ref('hr_work_entry_contract.work_entry_type_legal_leave').id
            sick_leave_id = self.env.ref('hr_work_entry_contract.work_entry_type_sick_leave').id
            attendance_id = self.env.ref('hr_work_entry.work_entry_type_attendance').id

            payslip_worked_days = self.env['hr.payslip.worked_days'].search([('payslip_id', 'in', employee_trimester.ids
                                                                              )])
            attendance_hours = payslip_worked_days.filtered(lambda o: o if o.work_entry_type_id.id == attendance_id else
            None)
            absence_hours = payslip_worked_days.filtered(lambda o: o if o.work_entry_type_id.id == absence_id else None)
            sick_leave_hours = payslip_worked_days.filtered(lambda o: o if o.work_entry_type_id.id == sick_leave_id else
                                        None)
            legal_leave_hours = payslip_worked_days.filtered(lambda o: o if o.work_entry_type_id.id == legal_leave_id
            else None)

            res = sum(attendance_hours.mapped('number_of_hours')) - sum(absence_hours.mapped(
                'number_of_hours')) - sum(legal_leave_hours.mapped('number_of_hours')) - sum(sick_leave_hours.mapped(
                'number_of_hours'))

        return int(round(res)) if res else 0

    def get_average_paid_amount_by_trimester(self, payslips, employee_id, trimester, next_trimester):

        employee_payslips = payslips.filtered(lambda o: o if o.employee_id == employee_id else [])
        employee_trimester = employee_payslips.filtered(
            lambda o: o if o.date_to < next_trimester[0] and o.date_from >= trimester[0] else None
        )
        suming = sum(employee_trimester.mapped('post_salary'))
        res = self.get_value_in_cents(suming)
        return res

    def get_leave_date(self, employee_id):
        employee_contract = self.env['hr.contract'].search([('employee_id', '=', employee_id.id), ('leave', '=', True),
                                                            ('leave_date', '<=', datetime.now().date().replace
                                                            (month=12, day=1, year=int(self.year_reference))),
                                                            ('leave_date', '>=', datetime.now().date().replace
                                                            (month=1, day=1, year=int(self.year_reference)))])
        return employee_contract.leave_date if len(employee_contract) == 1 else employee_contract[:-1].leave_date

    def get_lines(self, path):
        """
            This function returns a list of all employees that been working for the company in that year,
            to do so we'll be using the payslips to distingue employees
        """

        payslips = self.env['hr.payslip'].search([('date_to', '<=', datetime.now().replace(day=31, month=12, year=int(
            self.year_reference))), ('date_from', '>=', datetime.now().replace(day=1, month=1, year=int(self.
                                                                                                        year_reference))
                                     )], order='employee_id')

        first_trimester_dates, second_trimester_dates, third_trimester_dates, fourth_trimester_dates, fifth_trimester_dates = \
            get_trimesters(int(self.year_reference))

        line_details = ""
        i = 0
        all_amount = 0
        last_employee = None
        for payslip in payslips:
            employee_id = payslip.employee_id
            annual_amount = 0
            if last_employee and last_employee != employee_id or last_employee == None:

                amount_first_trimester = self.get_average_paid_amount_by_trimester(
                        payslips, employee_id, first_trimester_dates, second_trimester_dates)
                amount_second_trimester = self.get_average_paid_amount_by_trimester(
                    payslips, employee_id, second_trimester_dates, third_trimester_dates)
                amount_third_trimester = self.get_average_paid_amount_by_trimester(
                    payslips, employee_id, third_trimester_dates, fourth_trimester_dates)
                amount_fourth_trimester = self.get_average_paid_amount_by_trimester(
                    payslips, employee_id, fourth_trimester_dates, fifth_trimester_dates)

                i += 1
                line_details += "\n" + \
                    get_correct_value(str(self.employer_number)
                                      if self.employer_number else '', 10) + \
                    get_correct_value(str(self.year_reference)
                                      if self.year_reference else '', 4) + \
                    get_correct_value(str(i), 6) + \
                    get_correct_value(str(employee_id.social_security_number)
                                      if employee_id.social_security_number else '', 12) + \
                    get_correct_value(str(employee_id.last_name)
                                      if employee_id.last_name else '', 25) + \
                    get_correct_value(str(employee_id.first_name)
                                      if employee_id.first_name else '', 25) + \
                    get_correct_value(get_correct_date(employee_id.birthday)
                                      if employee_id.birthday else '', 8) + \
                    get_correct_value(str(self.get_worked_time_by_trimester(
                        payslips, employee_id, first_trimester_dates, second_trimester_dates)), 3) + "H" + \
                    get_correct_value(str(amount_first_trimester), 10) + \
                    get_correct_value(str(self.get_worked_time_by_trimester(
                        payslips, employee_id, second_trimester_dates, third_trimester_dates)), 3) + "H" + \
                    get_correct_value(str(amount_second_trimester), 10) + \
                    get_correct_value(str(self.get_worked_time_by_trimester(
                        payslips, employee_id, third_trimester_dates, fourth_trimester_dates)), 3) + "H" + \
                    get_correct_value(str(amount_third_trimester), 10)

                annual_amount = amount_first_trimester + amount_second_trimester + amount_third_trimester
                if self.no_fourth_trimester:
                    line_details += get_correct_value('0', 3) + "H" + get_correct_value('0', 10)
                else:
                    line_details += get_correct_value(str(self.get_worked_time_by_trimester(
                        payslips, employee_id, fourth_trimester_dates, fifth_trimester_dates)), 3) + "H" +\
                                    get_correct_value(str(amount_fourth_trimester), 10)
                    annual_amount = \
                        amount_first_trimester + amount_second_trimester + amount_third_trimester + \
                        amount_fourth_trimester

                line_details += get_correct_value(str(annual_amount), 12) + \
                    get_correct_value(get_correct_date(employee_id.recruitment_date)
                                      if employee_id.recruitment_date else '', 8) + \
                    get_correct_value(get_correct_date(self.get_leave_date(employee_id))
                                      if self.get_leave_date(employee_id) else '', 8) + \
                    get_correct_value(str(employee_id.job_id.name)
                                      if employee_id.job_id.name else '', 20)
                last_employee = employee_id
        print(all_amount)
        self.amount_number_employee = i
        self.das_lines = line_details

    def action_prepare_values(self):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value

        company = self.env.company

        # total_amount_by_trimester
        self.get_amount_by_trimesters()

        # nomination
        self.nomination = company.name

        # rs
        self.rs = company.company_registry

        # address
        self.address = company.street if company.street else "" + company.street2 \
            if company.street2 else "" + company.state_id.name if company.state_id.name else ""

        # get lines
        self.get_lines(path)

        # get header
        self.get_header(path)

    def action_export_header(self):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value

        header_title = "D" + str(self.year_reference)[2:] + "E" + str(self.employer_number) + ".txt"

        header_path = path + header_title

        f_read = open(header_path, 'w')

        f_read.write(u'' + self.das_header[3:-4])
        f_read.close()

        f_read = open(header_path)
        file_data = f_read.read()
        f_read.close()
        # Pass your text file data using encoding.

        values = {
            'name': header_title,
            # TODO: old field datas_fname got removed, check if store_fname is correct and write migration
            'store_fname': header_path,
            'res_model': 'ir.ui.view',
            'res_id': False,
            'type': 'binary',
            'public': True,
            'datas': base64.b64encode(open(header_path, 'rb').read())
        }

        # Using your data create as attachment
        attachment_id = self.env['ir.attachment'].sudo().create(values)

        # Return  so it will download in your system
        action = {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=ir.attachment&id=" + str(attachment_id.id) +
                   "&filename_field=name&field=datas&download=true&name=" + attachment_id.name,
            'target': 'self'
        }
        return action

    def action_export_lines(self):
        path = self.env.ref('smartest_base.smartest_files_path').sudo().value

        line_title = "D" + str(self.year_reference)[2:] + "S" + str(self.employer_number) + ".txt"

        line_path = path + line_title

        f_read = open(line_path, 'w')

        f_read.write(u'' + self.das_lines[3:-4])
        f_read.close()

        f_read = open(line_path)
        file_data = f_read.read()
        f_read.close()
        # Pass your text file data using encoding.

        values = {
            'name': line_title,
            # TODO: old field datas_fname got removed, check if store_fname is correct and write migration
            'store_fname': line_path,
            'res_model': 'ir.ui.view',
            'res_id': False,
            'type': 'binary',
            'public': True,
            'datas': base64.b64encode(open(line_path, 'rb').read())  # file_data.encode('utf8')  # .encode('base64'),
        }

        # Using your data create as attachment
        attachment_id = self.env['ir.attachment'].sudo().create(values)

        # Return  so it will download in your system
        action = {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=ir.attachment&id=" + str(attachment_id.id) +
                   "&filename_field=name&field=datas&download=true&name=" + attachment_id.name,
            'target': 'self'
        }
        return action
