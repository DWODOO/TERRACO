import pdb
import datetime
from odoo import api, fields, models, _


class ContractDecisionsWizard(models.TransientModel):
    _name = 'hr.contract.decisions.wizard'

    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    decision_type_id = fields.Many2one(
        'hr.contract.decisions.type',
        "Type",
    )
    decision_type = fields.Char(
        related='decision_type_id.name'
    )
    # decision_type = fields.Selection(
    #     [
    #         ('rise', 'Rise'),
    #         ('transfer', 'Transfer'),
    #         ('job_assignment', 'Job Assignment'),
    #         ('promotion', 'Promotion'),
    #         ('interim_decision', 'Interim Decision'),
    #         ('disciplinary_decision', 'Disciplinary Decision')
    #     ],
    #     "Type",
    # )
    contract_history_id = fields.Many2one(
        'hr.contract.history'
    )
    contract_id = fields.Many2one(
        'hr.contract'
    )
    contract_type_id = fields.Many2one('hr.contract.type', "Contract Type")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    company_currency = fields.Many2one('res.currency',
                                       string='Currency',
                                       related='company_id.currency_id',
                                       )
    # transfer
    department_id = fields.Many2one('hr.department', readonly=False,
                                    domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                    string="Department")
    # job_assignment
    job_id = fields.Many2one('hr.job', readonly=False,
                             domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                             string='Job Position')

    # Rise
    wage = fields.Monetary(
        'Wage',
        currency_field="company_currency",

        help="Employee's monthly gross wage."
    )
    allowance_responsibility = fields.Monetary(
        'Responsibility Allowance',
        currency_field="company_currency",

    )
    allowance_clothing = fields.Monetary(
        'Clothing Allowance',
        currency_field="company_currency",

    )
    allowance_cash = fields.Monetary(
        'Cash Allowance',
        currency_field="company_currency",

    )
    allowance_isp = fields.Float(
        'P.S.A',
        help='Permanent Service Allowance',

    )
    allowance_in_iep = fields.Float(
        'P.E.A (In company)',
        help='Professional Experience Allowance within the company',

    )
    allowance_out_iep = fields.Float(
        'P.E.A (Out of company)',
        help='Professional Experience Allowance out of the company',
    )
    allowance_pri = fields.Monetary(
        'Individual Performance Allowance',
        currency_field="company_currency",
    )
    allowance_icr = fields.Monetary(
        'S.I.A',
        help='Supplementary Income Allowance',
        currency_field="company_currency",
    )
    allowance_technicality = fields.Monetary(
        'Technicality Allowance',
        currency_field="company_currency",

    )
    allowance_isolated_area = fields.Monetary(
        'Isolated Area Allowance',
        currency_field="company_currency",
    )
    allowance_nuisance = fields.Float(
        'Nuisance Allowance',
    )
    allowance_availability = fields.Monetary(
        'Availability Allowance',
        currency_field="company_currency",
    )
    allowance_soiling = fields.Monetary(
        'Performance Allowance',
        currency_field="company_currency",
    )
    allowance_meal = fields.Monetary(
        'Meal Allowance',
        currency_field="company_currency",
    )
    allowance_meal_type = fields.Selection(
        [
            ('day', 'Day'),
            ('month', 'Month'),
        ],
        'Meal allowance type',
    )
    allowance_transportation = fields.Monetary(
        'Transportation Allowance',
        currency_field="company_currency",
    )
    allowance_vehicle = fields.Monetary(
        'Vehicle Allowance',
        currency_field="company_currency",
    )
    allowance_travel = fields.Monetary(
        'Travel Allowance',
        currency_field="company_currency",
    )
    allowance_rent = fields.Monetary(
        'Rent Allowance',
        currency_field="company_currency",
    )
    allowance_refund_rent = fields.Monetary(
        'Refund Rent Allowance',
        currency_field="company_currency",

    )
    allowance_transportation_type = fields.Selection(
        [
            ('day', 'Day'),
            ('month', 'Month'),
        ],
        'Transportation allowance type',
    )

    allowance_phone = fields.Monetary(
        'Phone Allowance',
        currency_field="company_currency",

    )
    allowance_unique_salary = fields.Monetary(
        'Unique Salary Allowance',
        currency_field="company_currency",
    )
    allowance_pop = fields.Monetary(
        'P.O.P',
        currency_field="company_currency",
    )
    allowance_pap = fields.Monetary(
        'P.A.P',
        currency_field="company_currency",
    )
    allowance_hse = fields.Monetary(
        'H.S.E',
        currency_field="company_currency",
    )
    allowance_iff = fields.Monetary(
        'I.F.F',
        currency_field="company_currency",
    )
    allowance_ifsp = fields.Monetary(
        'I.F.S.P',
        currency_field="company_currency",
    )
    allowance_itp = fields.Monetary(
        'I.T.P',
        currency_field="company_currency",
    )

    # @api.onchange('decision_type')
    # def _onchange_decision_type(self):
    #     if self.decision_type:
    #         if self.decision_type == 'rise':
    #             self.decision_type_id = self.env.ref('l10n_dz_hr.salary_rise')
    #         elif self.decision_type == 'transfer':
    #             self.decision_type_id = self.env.ref('l10n_dz_hr.transfer')
    #         elif self.decision_type == 'job_assignment':
    #             self.decision_type_id = self.env.ref('l10n_dz_hr.job_assignment')
    #         elif self.decision_type == 'promotion':
    #             self.decision_type_id = self.env.ref('l10n_dz_hr.promotion')
    #         elif self.decision_type == 'interim_decision':
    #             self.decision_type_id = self.env.ref('l10n_dz_hr.interim_decision')
    #         else:
    #             self.decision_type_id = self.env.ref('l10n_dz_hr.disciplinary_decision')

    def update_employee_resume(self):
        self.employee_id.resume_line_ids.filtered(lambda o: o if not o.date_end else None).write(
            {
                'date_end': datetime.date.today()
            }
        )
        self.env['hr.resume.line'].create(
            {
                'name': self.job_id.name + " " + self.company_id.name,
                'display_type': 'classic',
                'employee_id': self.employee_id.id,
                'date_start': datetime.date.today(),
                'line_type_id': 1
            }
        )

    def action_submit(self):
        """
        In this method, we submit the changes made on the current contract based on decisions, we'll have two dicts,
        vals: a dictiionary tha contains the field to store in hr_contract_decisions
        contract_vals: a dictionary the contains the value that need to be updated in the current contract
        :return:
        """
        vals = {}
        contract_vals = {}
        message_poste = ""
        for field in self._fields:
            if self[field] and field not in ['id', '__last_update', 'display_name', 'decision_type'] and self[
                field] != 0:
                try:
                    vals[field] = self[field].id
                    if field != "contract_id" and field != "decision_type_id":
                        contract_vals[field] = self[field].id
                        message_poste = (field + ": <strong>" + self.contract_id[field].name + " &rarr; " +
                                         self[field].name + "</strong> <br/>" + message_poste) if field not in [
                            'create_date', 'write_date', 'create_uid', 'write_uid', 'company_currency', 'company_id',
                            'employee_id'] else message_poste
                except:
                    vals[field] = self[field]
                    if field != 'decision_type':
                        contract_vals[field] = self[field]
                    message_poste = (field + ": <strong>" + str(self.contract_id[field]) + " &rarr; " + str(self[field])
                                     + "</strong> <br/>" + message_poste) if field not in [
                        'create_date', 'write_date', 'create_uid', 'write_uid', 'company_currency', 'company_id',
                        'employee_id'] else message_poste

        vals['description'] = message_poste

        if vals.get('job_id'):
            self.update_employee_resume()

        self.contract_id.write(contract_vals)
        res = self.env['hr.contract.decisions'].create(vals)

        action = {
            'name': _('Employee Contract decisions'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.contract.decisions',
            'res_id': res.id,
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': False,
            'context': {'default_contract_id': [(4, self.contract_id.id)]},
            'domain': [('id', 'in', self.contract_id.mapped('contract_decisions_ids.id'))],
            'target': 'current'
        }
        return action
