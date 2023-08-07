# -*- coding:utf-8 -*-
from odoo import api, fields, models, _


class Payment(models.Model):
    _name = 'hr.employee.typepayment'
    _description = 'Payment Type'
    _order = 'sequence, id'

    name = fields.Char(string='Payment Type', required=False)
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Contact.", default=10)


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    departure_reason = fields.Selection(
        [
            ('contract_end', 'Fin de contract'),
            ('trial_period', 'Période d\'éssaie non concluante'),
        ])
    type_payment_id = fields.Many2one(
        'hr.employee.typepayment',
        string="Payment type",
        required=False
    )
    last_name = fields.Char(
        'Last name',
        # track_visibility='onchange'
    )
    first_name = fields.Char(
        'First name',
        # track_visibility='onchange'
    )
    name = fields.Char(
        'Complete Name',
        related='resource_id.name',
        store=True,
        readonly=False
    )
    work_location = fields.Many2one(
        'res.country.state',
        string='Work location',
        groups="hr.group_hr_user",
        # track_visibility='onchange'
    )
    place_of_birth = fields.Char(
        string='State of Birth',
    )
    registration_number = fields.Char(
        'Registration number',
        readonly=False,
        store=True,
        # track_visibility='onchange'
    )
    housewife = fields.Boolean(
        'Housewife?',
        # track_visibility='onchange'
    )
    spouse_complete_name = fields.Char(
        string="Spouse's Name",
        groups="hr.group_hr_user",
        # track_visibility='onchange'
    )
    maiden_name = fields.Char(
        'Maiden name',
        # track_visibility='onchange'
    )
    presume = fields.Boolean(
        'Presumed?',
        # track_visibility='onchange'
    )
    cnas_affiliated = fields.Boolean(
        'CNAS Affiliated?',
        default=True,
        # track_visibility='onchange'
    )
    social_security_number = fields.Char(
        'Social Security N°',
        size=13,
        # track_visibility='onchange'
    )
    cnas_registration_start_date = fields.Date(
        'Registered in CNAS from',
        # track_visibility='onchange'
    )
    cnas_salary_contribution = fields.Float(
        'CNAS: Salary contribution (%)',
        default=9,
        digits=(12, 3)
        # track_visibility='onchange'
    )
    cnas_patronage_contribution = fields.Float(
        'CNAS: Patronage contribution (%)',
        default=26,
        digits=(12, 3)
        # track_visibility='onchange'
    )
    cnas_social_services_funds_contribution = fields.Float(
        'CNAS: Social Services Fund contribution (%)',
        default=0.5,
        digits=(12, 3)
        # track_visibility='onchange'
    )
    cacobatph_affiliated = fields.Boolean(
        'CACOBATPH Affiliated?',
        # track_visibility='onchange'
    )
    cacobatph_patronage_contribution = fields.Float(
        'CACOBATPH: Patronage contribution (%)',
        default=0.375,
        digits=(12, 3)
        # track_visibility='onchange'
    )
    cacobatph_services_funds_contribution = fields.Float(
        'CACOBATPH: Social Services Fund contribution (%)',
        default=0.375,
        digits=(12, 3)
        # track_visibility='onchange'
    )
    use_employee_sequence = fields.Boolean(
        related='company_id.use_employee_sequence'
    )
    zip = fields.Char(
        change_default=True
    )
    state_id = fields.Many2one(
        "res.country.state",
        string='State',
        ondelete='restrict',
        domain="[('country_id', '=?', country_id)]"
    )
    country_id = fields.Many2one(
        'res.country',
        string='Country',
        ondelete='restrict'
    )
    commune_id = fields.Many2one(
        'res.commune',
        string='Commune'
    )
    birth_commune_id = fields.Many2one(
        'res.commune',
        string='Birth Commune'
    )
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    last_report_sequence = fields.Char(
        'Last Sequence',
    )



class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    departure_reason = fields.Selection(
        [
            ('contract_end', 'Fin de contract'),
            ('trial_period', 'Période d\'éssaie non concluante'),
        ])

    type_payment_id = fields.Many2one(
        'hr.employee.typepayment',
        string="Payment type",
        required=False
    )

    gender = fields.Selection(
        [
            ('male', 'Male'),
            ('female', 'Female')
        ],
        groups="hr.group_hr_user",
        default="male",
        # track_visibility='onchange'
    )
    last_name = fields.Char(
        'Last name',
        # track_visibility='onchange'
    )
    first_name = fields.Char(
        'First name',
        # track_visibility='onchange'
    )
    name = fields.Char(
        'Complete Name',
        related='resource_id.name',
        store=True,
        readonly=False
    )
    work_location = fields.Many2one(
        'res.country.state',
        string='Work location',
        groups="hr.group_hr_user",
        # track_visibility='onchange'
    )
    place_of_birth = fields.Char(
        string='State of Birth',
        groups="hr.group_hr_user",
        # track_visibility='onchange'
    )
    registration_number = fields.Char(
        'Registration number',
        readonly=False,
        store=True,
        # track_visibility='onchange'
    )
    housewife = fields.Boolean(
        'Housewife?',
        # track_visibility='onchange'
    )
    spouse_complete_name = fields.Char(
        string="Spouse's Name",
        groups="hr.group_hr_user",
        # track_visibility='onchange'
    )
    maiden_name = fields.Char(
        'Maiden name',
        # track_visibility='onchange'
    )
    presume = fields.Boolean(
        'Presumed?',
        # track_visibility='onchange'
    )
    cnas_affiliated = fields.Boolean(
        'CNAS Affiliated?',
        default=True,
        # track_visibility='onchange'
    )
    social_security_number = fields.Char(
        'Social Security N°',
        size=13,
        # track_visibility='onchange'
    )
    cnas_registration_start_date = fields.Date(
        'Registered in CNAS from',
        # track_visibility='onchange'
    )
    cnas_salary_contribution = fields.Float(
        'CNAS: Salary contribution (%)',
        default=9,
        digits=(12, 3)
        # track_visibility='onchange'
    )
    cnas_patronage_contribution = fields.Float(
        'CNAS: Patronage contribution (%)',
        default=26,
        digits=(12, 3)
        # track_visibility='onchange'
    )
    cnas_social_services_funds_contribution = fields.Float(
        'CNAS: Social Services Fund contribution (%)',
        default=0.5,
        digits=(12, 3)
        # track_visibility='onchange'
    )
    cacobatph_affiliated = fields.Boolean(
        'CACOBATPH Affiliated?',
        # track_visibility='onchange'
    )
    cacobatph_patronage_contribution = fields.Float(
        'CACOBATPH: Patronage contribution (%)',
        default=0.375,
        digits=(12, 3)
        # track_visibility='onchange'
    )
    cacobatph_services_funds_contribution = fields.Float(
        'CACOBATPH: Social Services Fund contribution (%)',
        default=0.375,
        digits=(12, 3)
        # track_visibility='onchange'
    )
    use_employee_sequence = fields.Boolean(
        related='company_id.use_employee_sequence'
    )
    zip = fields.Char(
        change_default=True
    )
    state_id = fields.Many2one(
        "res.country.state",
        string='State',
        ondelete='restrict',
        domain="[('country_id', '=?', country_id)]"
    )
    country_id = fields.Many2one(
        'res.country',
        string='Country',
        ondelete='restrict'
    )
    commune_id = fields.Many2one(
        'res.commune',
        string='Commune'
    )
    birth_commune_id = fields.Many2one(
        'res.commune',
        string='Birth Commune'
    )
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    last_report_sequence = fields.Char(
        'Last Sequence',
    )
    children_ids = fields.One2many('hr.employee.children', 'employee_id')
    children_ids_count = fields.Integer(compute='_compute_children_count')

    contract_decisions_ids = fields.One2many(
        'hr.contract.decisions',
        'employee_id'
    )
    contract_decisions_ids_count = fields.Integer(compute='_compute_contract_decisions_ids_count')

    _sql_constraints = [
        ('unique_reg_num', 'unique(registration_number)', _('The registration number must be unique per employee.'))
    ]

    @api.depends('contract_ids')
    def get_leave_date(self):
        for employee in self:
            last_contract = employee.contract_ids.filtered(lambda o: o if o.leave else False)
            return last_contract.leave_date.strftime('%d/%m/%Y')

    @api.onchange('place_of_birth')
    def on_place_of_birth_change(self):
        if self.place_of_birth:
            self.country_of_birth = self.place_of_birth.country_id

    @api.model
    def create(self, values):
        if not values.get('name'):
            values['name'] = '%s %s' % (values.get('first_name') or '', values.get('last_name') or '')
        company = self.env.user.company_id
        if company.use_employee_sequence:
            values['registration_number'] = company.employee_sequence_id.next_by_id()
        return super(HrEmployee, self).create(values)

    def write(self, values):
        if values.get('first_name', False) or values.get('last_name', False):
            for employee in self:
                values['name'] = '%s %s' % (
                    values.get('first_name', False) or employee.first_name or '',
                    values.get('last_name', False) or employee.last_name or '',
                )
                super(HrEmployee, employee).write(values)
        else:
            super(HrEmployee, self).write(values)

    def get_work_certificate_sequence(self):
        # sequence = self.env.ref('l10n_dz_hr.sequence_hr_employment_certificate').next_by_id()
        sequence = self.env.ref('l10n_dz_hr.sequence_hr_employee_documents').next_by_id()
        return sequence

    def get_work_attestation_sequence(self):
        # sequence = self.env.ref('l10n_dz_hr.sequence_hr_employment_attestation').next_by_id()
        sequence = self.env.ref('l10n_dz_hr.sequence_hr_employee_documents').next_by_id()
        return sequence

    def action_view_employee_children(self):
        for employee in self:
            tree_view = self.env.ref('l10n_dz_hr.action_employee_children')
            action = {
                'name': _('Employee Children'),
                'type': 'ir.actions.act_window',
                'res_model': 'hr.employee.children',
                'view_mode': 'tree',
                'context': {'default_employee_id': [(4, employee.id)]}
            }

            action['domain'] = [('id', 'in', employee.mapped('children_ids.id'))]
            return action

    def action_open_contract_decisions(self):
        for employee in self:
            tree_view = self.env.ref('l10n_dz_hr.view_contract_decisions_tree')
            form_view = self.env.ref('l10n_dz_hr.view_contract_decisions_form')
            action = {
                'name': _('Employee Contract decisions'),
                'type': 'ir.actions.act_window',
                'res_model': 'hr.contract.decisions',
                'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
                'view_mode': 'tree, form',
                'context': {'default_employee_id': [(4, employee.id)]}
            }

            action['domain'] = [('id', 'in', employee.mapped('contract_decisions_ids.id'))]
            return action

    @api.depends("children_ids_count")
    def _compute_children_count(self):
        for employee in self:
            employee.children_ids_count = len(employee.mapped("children_ids"))

    @api.depends("contract_decisions_ids_count")
    def _compute_contract_decisions_ids_count(self):
        for employee in self:
            employee.contract_decisions_ids_count = len(employee.mapped("contract_decisions_ids"))


class EmployeeChildren(models.Model):
    _name = 'hr.employee.children'
    _description = 'Employee Children'

    employee_id = fields.Many2one('hr.employee', string='Parent')
    first_name = fields.Char('First name')
    school_level = fields.Selection([
        ('primaire', 'Primaire'),
        ('cem', 'CEM'),
        ('lycee', 'Lycee')
        ],
        string='School Level'
    )
    school_year = fields.Selection([
        ('1st_elementary', '1st Elementary'),
        ('2nd_elementary', '2nd Elementary'),
        ('3rd_elementary', '3rd Elementary'),
        ('4rd_elementary', '4th Elementary'),
        ('5th_elementary', '5th Elementary'),
        ('1st_secondary', '1st Secondary'),
        ('2nd_secondary', '2nd Secondary'),
        ('3rd_secondary', '3rd Secondary'),
        ('4rd_secondary', '4th Secondary'),
        ('1st_lycee', '1st Lycee'),
        ('2st_lycee', '2nd Lycee'),
        ('3st_lycee', '3rd Lycee')
    ], string='School Year')
