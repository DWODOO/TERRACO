import datetime

from odoo import api, fields, models, _


class ContractAmendmentWizard(models.TransientModel):
    _name = 'hr.contract.amendment.wizard'

    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    contract_id = fields.Many2one(
        'hr.contract'
    )
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)
    company_currency = fields.Many2one('res.currency',
                                       string='Currency',
                                       related='company_id.currency_id',
                                       )
    # Administration
    # date_start = fields.Date('Start Date',  help="Start date of the contract.")
    date_end = fields.Date('End Date', help="End date of the contract (if it's a fixed-term contract).")
    trial_date_end = fields.Date('End of Trial Period', help="End date of the trial period (if there is one).")
    structure_type_id = fields.Many2one('hr.payroll.structure.type', string="Salary Structure Type")
    department_id = fields.Many2one('hr.department',
                                    domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                    string="Department")
    job_id = fields.Many2one('hr.job',
                             domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                             string='Job Position')
    contract_type_id = fields.Many2one('hr.contract.type', "Contract Type")

    # Payroll
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
    leave_notice = fields.Integer(
        'Leave notice',
    )

    def action_submit(self):
        vals = {}
        for field in self._fields:
            if self[field] and field not in ['id', '__last_update', 'display_name', 'contract_id'] and self[field] != 0:
                try:
                    vals[field] = self[field].id
                except:
                    vals[field] = self[field]
        vals['state'] = 'open'
        vals['nature'] = 'amendment'
        vals['parent_contract_id'] = self.contract_id.id

        if vals.get('job_id'):
            self.employee_id.resume_line_ids.filtered(lambda o: o if not o.date_end else None).write(
                {
                    'date_end': datetime.date.today()
                })
            self.env['hr.resume.line'].create({
                'name': self.job_id.name+" "+self.company_id.name,
                'display_type': 'classic',
                'employee_id': self.employee_id.id,
                'date_start': datetime.date.today(),
                'line_type_id': 1
            })

        self.contract_id.state = 'amendment'
        res = self.contract_id.sudo().copy(vals)

        action = {
            'name': _('Employee Contract'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.contract',
            'res_id': res.id,
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': False,
            'target': 'current',
        }

        return action
