# -*- coding:utf-8 -*-
from odoo import api, fields, models

DaysInYear = 365


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    smartest_in_experience_years = fields.Integer(
        string="Experience within the company",
        help='Number of years of experience within of the company',
        compute="_compute_experience_in",
    )
    smartest_out_experience_years = fields.Integer(
        string='Experience outside the company',
        help='Number of years of experience outside of the company',
        compute="_compute_experience_out",
    )

    recruitment_date = fields.Date(
        'Recruitment  Date',
        compute='_compute_recruitment_date'
    )

    # company_cnas_id = fields.Many2one(
    #     'res.company.cnas',
    #     'Employer Number',
    # )

    @api.depends('contract_ids')
    def _compute_recruitment_date(self):
        hrContract = self.env['hr.contract']
        for employee in self:
            domain = [
                ('employee_id', '=', employee.id),
                ('state', 'in', ('open', 'close'))
            ]
            contract = hrContract.search(domain, order="date_start ASC", limit=1)
            employee.recruitment_date = contract.date_start

    @api.depends('resume_line_ids.date_end', 'resume_line_ids.date_start')
    @api.depends_context('iep_date_limit')
    def _compute_experience_out(self):
        line_type_id_experience = self.env.ref('hr_skills.resume_type_experience')
        today = fields.Date.today()
        date_limit = self.env.context.get('iep_date_limit', fields.Date.today())
        for employee in self:
            days_exp = 0
            for line in employee.resume_line_ids:
                if line.line_type_id == line_type_id_experience and line.date_start <= date_limit:
                    date_end = line.date_end if line.date_end and line.date_end <= date_limit else date_limit
                    days_exp += (date_end - line.date_start).days
            employee.smartest_out_experience_years = int(days_exp / DaysInYear)

    @api.depends('contract_ids.state', 'contract_ids.date_start', 'contract_ids.date_end')
    @api.depends_context('iep_date_limit')
    def _compute_experience_in(self):
        date_limit = self.env.context.get('iep_date_limit', fields.Date.today())
        for employee in self:
            days_exp = 0
            for contract in employee.contract_ids:
                if contract.state not in ('draft', 'cancel') and contract.date_start <= date_limit:
                    date_end = contract.date_end if contract.date_end and contract.date_end <= date_limit else date_limit
                    days_exp += ((date_end - contract.date_start).days + (contract.allowance_in_iep_in_addition * DaysInYear))
            employee.smartest_in_experience_years = int(round(days_exp / DaysInYear))

    @api.model
    def _cron_calculate_in_experience_years(self):
        self.search([])._compute_experience_in()
