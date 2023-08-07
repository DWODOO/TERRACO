from odoo import api, fields, models, _


class ContractDecisionsType(models.Model):
    _name = 'hr.contract.decisions.type'

    name = fields.Char(
        "Name"
    )
    description = fields.Text(
        "Description"
    )


class ContractDecisions(models.Model):
    _name = 'hr.contract.decisions'
    _description = "Contract Decisions"
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        "Name"
    )
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    decision_type_id = fields.Many2one(
        'hr.contract.decisions.type',
        "Type",
    )
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

                                       tracking=True
                                       )
    # transfer
    department_id = fields.Many2one('hr.department', store=True,
                                    domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                    string="Department")
    # job_assignment
    job_id = fields.Many2one('hr.job', store=True,
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

        tracking=True
    )
    allowance_clothing = fields.Monetary(
        'Clothing Allowance',
        currency_field="company_currency",

        tracking=True
    )
    allowance_cash = fields.Monetary(
        'Cash Allowance',
        currency_field="company_currency",

        tracking=True
    )
    allowance_isp = fields.Float(
        'P.S.A',
        help='Permanent Service Allowance',

        tracking=True
    )
    allowance_in_iep = fields.Float(
        'P.E.A (In company)',
        help='Professional Experience Allowance within the company',

        tracking=True
    )
    allowance_out_iep = fields.Float(
        'P.E.A (Out of company)',
        help='Professional Experience Allowance out of the company',

        tracking=True
    )
    allowance_pri = fields.Monetary(
        'Individual Performance Allowance',
        currency_field="company_currency",

        tracking=True
    )
    allowance_icr = fields.Monetary(
        'S.I.A',
        help='Supplementary Income Allowance',
        currency_field="company_currency",

        tracking=True
    )
    allowance_technicality = fields.Monetary(
        'Technicality Allowance',
        currency_field="company_currency",

        tracking=True
    )
    allowance_isolated_area = fields.Monetary(
        'Isolated Area Allowance',
        currency_field="company_currency",

        tracking=True
    )
    allowance_nuisance = fields.Float(
        'Nuisance Allowance',

        tracking=True
    )
    allowance_availability = fields.Monetary(
        'Availability Allowance',
        currency_field="company_currency",

        tracking=True
    )
    allowance_soiling = fields.Monetary(
        'Performance Allowance',
        currency_field="company_currency",

        tracking=True
    )
    allowance_meal = fields.Monetary(
        'Meal Allowance',
        currency_field="company_currency",

        tracking=True
    )
    allowance_meal_type = fields.Selection(
        [
            ('day', 'Day'),
            ('month', 'Month'),
        ],
        'Meal allowance type',
        tracking=True
    )
    allowance_transportation = fields.Monetary(
        'Transportation Allowance',
        currency_field="company_currency",

        tracking=True
    )
    allowance_vehicle = fields.Monetary(
        'Vehicle Allowance',
        currency_field="company_currency",

        tracking=True
    )
    allowance_travel = fields.Monetary(
        'Travel Allowance',
        currency_field="company_currency",

        tracking=True
    )
    allowance_rent = fields.Monetary(
        'Rent Allowance',
        currency_field="company_currency",

        tracking=True
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
        tracking=True
    )

    allowance_phone = fields.Monetary(
        'Phone Allowance',
        currency_field="company_currency",

        tracking=True
    )
    allowance_unique_salary = fields.Monetary(
        'Unique Salary Allowance',
        currency_field="company_currency",

        tracking=True
    )
    allowance_pop = fields.Monetary(
        'P.O.P',
        currency_field="company_currency",

        tracking=True
    )
    allowance_pap = fields.Monetary(
        'P.A.P',
        currency_field="company_currency",

        tracking=True
    )
    allowance_hse = fields.Monetary(
        'H.S.E',
        currency_field="company_currency",

        tracking=True
    )
    allowance_iff = fields.Monetary(
        'I.F.F',
        currency_field="company_currency",

        tracking=True
    )
    allowance_ifsp = fields.Monetary(
        'I.F.S.P',
        currency_field="company_currency",

        tracking=True
    )
    allowance_itp = fields.Monetary(
        'I.T.P',
        currency_field="company_currency",

        tracking=True
    )
    description = fields.Html()

    @api.model
    def create(self, values):
        if not values.get('name', False):
            sequence = self.env.ref('l10n_dz_hr.sequence_hr_employee_contract_decision')
            values['name'] = sequence.next_by_id()
        return super(ContractDecisions, self).create(values)

    def name_get(self):
        return [(record.id, "[%s] %s" % (record.contract_id.display_name, record.employee_id.display_name)) for record
                in self]
