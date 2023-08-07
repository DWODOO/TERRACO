# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA
import re

from odoo.exceptions import ValidationError

# Import Odoo libs
from odoo import _, api, fields, models

RULE_FIELD_PREFIX = "x_smartest_"
BASE_RANGE = {'min': 0, 'max': 40}
CONTRIBUTION_RANGE = {'min': 60, 'max': 160}
TAXABLE_RANGE = {'min': 200, 'max': 300}
NCNI_RANGE = {'min': 350, 'max': 450}
NET_RANGE = {'min': 500, 'max': 550}
PrcntgeAbat = 40
RoundParam = 2
IEPOutMax = 16


class SmartestHrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    def _default_code_prefix(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'hr_payroll.smartest_code_prefix')

    def _default_padding_code(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'hr_payroll.smartest_padding_code')

    smartest_rule_create_auto = fields.Selection(string="Rule Creation Auto",
                                                 selection=[("other", "Other...")])
    smartest_rule_type = fields.Selection(string="Rule Type",
                                          selection=[("contribution", "Contribution"),
                                                     ("taxable", "Taxable"),
                                                     ("regul_cot", "Contributory regularization"),
                                                     ("regul_lmp", "Taxable regularization"),
                                                     ("regul_base", "Basic regularization")
                                                     ])
    smartest_rule_val = fields.Selection(string="Rule Value",
                                         selection=[("gain", "Gain (+)"),
                                                    ("deduction", "Return (-)"),
                                                    ("rate", "rate")])
    smartest_rule_amount_type = fields.Selection(string="Amount Type",
                                                 selection=[("fixe", "Fix Amount"),
                                                            ("variable", "Variable Amount")])
    smartest_amount_value_type = fields.Selection(string="Amount Value",
                                                  selection=[("month", "Monthly amount"),
                                                             ("day", "Daily amount")])
    smartest_regul_type = fields.Selection(string="Regul Type",
                                           selection=[("gain", "Gain (+)"),
                                                      ("deduction", "Return (-)")])
    smartest_name_var = fields.Char(string="Variable Name")
    smartest_code_prefix = fields.Char(string="Prefix",
                                       default=_default_code_prefix)
    smartest_padding_code = fields.Integer(string="Code Lenght",
                                           default=_default_padding_code)
    smartest_amount_fixe_rule = fields.Float(string="Amount")
    smartest_rate_rule = fields.Float(string="rate")
    smartest_is_regul = fields.Boolean(string="Is Regularization", default=False)
    smartest_is_leave = fields.Boolean(string="Is Leave", default=False)
    smartest_is_irg = fields.Boolean(string="Is IRG", default=False)
    smartest_is_ss = fields.Boolean(string="Is SS", default=False)
    smartest_perfect_depends = fields.Selection(string="Depends on perfect",
                                                compute="_compute_perfect_depends",
                                                store="True",
                                                selection=[("perfect_depends", "Appartieent au cas parfait"),
                                                           ("perfect_not_in_dependency",
                                                            "N'appartient pas au cas parfait")])
    smartest_is_absence = fields.Boolean(string="Is Absence", default=False)
    smartest_attendance_depends = fields.Boolean(string="Depends on Attendancy")
    smartest_leave_depends = fields.Boolean(string="Depends on Leave")
    code = fields.Char(store=True, readonly=False, compute="_compute_code")
    smartest_date_from = fields.Date(string='From',
                                     default=fields.Date.context_today)
    smartest_date_to = fields.Date(string='To')
    smartest_field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string="Field",
        domain=[('model_id', '=', "hr.contract"), ('name', 'ilike', RULE_FIELD_PREFIX)]
    )
    struct_id = fields.Many2many(
        comodel_name='hr.payroll.structure',
        relation='smartest_rule_struct_rel',
        column1='rule_id',
        column2='struct_id',
        string="Salary Structure",
        required=True
    )

    # _sql_constraints = [
    #     ('sequence_unique', 'unique (sequence)', _('The sequence assigned to a rule must be unique!')),
    #     ('code_rule_unique', 'unique (code)', _("Rule's Code must be unique!")),
    # ]
    #
    # @api.constrains('sequence')
    # def _check_range_sequence(self):
    #     for record in self:
    #         if record.category_id:
    #             if not (record.category_id.smartest_range_min <= record.sequence < record.category_id.smartest_range_max):
    #                 raise ValidationError(
    #                     _('The sequence must be included between (%d) and (%d) !', record.category_id.smartest_range_min,
    #                       record.category_id.smartest_range_max))

    # @api.constrains('smartest_padding_code')
    # def _check_smartest_padding_code(self):
    #     if any(record.smartest_padding_code <= 0 for record in self):
    #         raise ValidationError(
    #             _('Code lenght Must Be greater than 0.!')
    #         )

    @api.constrains('smartest_date_from', 'smartest_date_to')
    def _check_date_validity(self):
        if any(
                record.smartest_date_to and record.smartest_date_from and record.smartest_date_to < record.smartest_date_from
                for record in self):
            raise ValidationError(
                _('Date Rom Must Be Lower than Date To!')
            )

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            self.name = re.sub(" +", ' ', self.name)

    # This Method allows the user to create a field/fields that a rule depends on in a Contract
    def action_creation_custom_variable(self):
        model_id = self.env.ref('hr_contract.model_hr_contract')
        IrModelField = self.env['ir.model.fields']
        contract_fields = IrModelField.filtered(lambda f: f.name.startswith(RULE_FIELD_PREFIX))
        fields_vals_list = []

        for rule in self:
            if not rule.smartest_name_var:
                raise ValidationError(_('Variable Name MUST BE given!'))

            name = RULE_FIELD_PREFIX + (rule.smartest_name_var.replace(" ", "_")).lower()
            if name in contract_fields:
                raise ValidationError(_('This Variable Already Exists!'))

            fields_vals_list.append(rule._prepare_field_values(name, model_id))

        fields = IrModelField.sudo().create(fields_vals_list)
        self._add_customizable_field(fields)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    # This Method allows to prepare fields to create
    def _prepare_field_values(self, name, model):
        self.ensure_one()
        return {
            'name': name,
            'field_description': self.smartest_name_var,
            'model_id': model.id,
            'ttype': 'float'
        }

    # This Method allows to show fields in the custom form view of the Hr.Contract
    def _add_customizable_field(self, fields):
        form_view = self.env.ref('smartest_hr_payroll.smartest_hr_contract_view_form_customizable')
        arch_base = form_view.arch_base.split('<group name="customizable_rule_fields" position="inside">')
        field_dict = '<group name="customizable_rule_fields" position="inside">\n'

        # TODO: Add field as last element on <group name='customizable_rule_fields'/>
        for field in fields:
            field_dict += '<field name="%s"/>\n' % field.name
        form_view.sudo().update({"arch_base": arch_base[0] + field_dict + arch_base[1]})

    @api.depends('smartest_code_prefix', 'smartest_padding_code', 'sequence')
    def _compute_code(self):
        for record in self:
            code = ""
            if record.smartest_code_prefix:
                code += record.smartest_code_prefix.replace(" ", "")
            if record.smartest_padding_code:
                code += str(record.sequence).zfill(record.smartest_padding_code)
            record.code = code

    @api.depends('smartest_is_regul', 'smartest_is_leave', 'smartest_is_absence', 'smartest_attendance_depends',
                 'smartest_leave_depends')
    def _compute_perfect_depends(self):
        for record in self:
            if record.smartest_is_regul or record.smartest_is_leave or record.smartest_is_absence:
                perfect_depends = "perfect_not_in_dependency"
            else:
                perfect_depends = "perfect_depends"
            record.smartest_perfect_depends = perfect_depends

    # This Method is used to return contribution Category
    def _return_contribution_category(self):
        Category = self.env['hr.salary.rule.category'].sudo()
        category_id = Category.search([('smartest_category_type', '=', "contribution")], limit=1)
        if not category_id:
            category_id = Category.create(
                {
                    "name": "contribution",
                    "code": "contribution",
                    "smartest_range_min": CONTRIBUTION_RANGE['min'],
                    "smartest_range_max": CONTRIBUTION_RANGE['max'],
                    "smartest_category_type": "contribution",
                }
            )
        return category_id

    # This Method is used to return taxable Category
    def _return_taxable_category(self):
        Category = self.env['hr.salary.rule.category'].sudo()
        category_id = Category.search([('smartest_category_type', '=', "taxable")], limit=1)
        if not category_id:
            category_id = Category.create({
                "name": "taxable",
                "code": "taxable",
                "smartest_range_min": TAXABLE_RANGE['min'],
                "smartest_range_max": TAXABLE_RANGE['max'],
                "smartest_category_type": "taxable",
            }

            )
        return category_id

    # This Method is used to return Base Category
    def _return_base_category(self):
        Category = self.env['hr.salary.rule.category'].sudo()
        category_id = Category.search([('smartest_category_type', '=', "contribution")], limit=1)
        if not category_id:
            category_id = Category.create(
                {
                    "name": "Base",
                    "code": "BASIC",
                    "smartest_range_min": BASE_RANGE['min'],
                    "smartest_range_max": BASE_RANGE['max'],
                    "smartest_category_type": "base",
                }
            )
        return category_id

    def _generate_amount_python_compute_fixe(self, rule_val, amount_type, amount_fixe):
        amount_python_compute = ''
        if rule_val == "deduction":
            amount_sign = "-"
        else:
            amount_sign = '+'

        if amount_type == "day":
            amount_python_compute = "result = " + amount_sign + " ( contract.days_per_month * abs( " + str(
                +amount_fixe) + ") )"
        elif amount_type == "month":

            amount_python_compute = "result = " + amount_sign + " abs( " + str(
                amount_fixe) + ")"
        return amount_python_compute

    # This Method is used to create Amount Fixe Rule
    def create_fix_amount_rule(self, rule_val, amount_type, amount_fixe):
        return {
            'condition_select': "none",
            'amount_select': "code",
            'amount_python_compute': self._generate_amount_python_compute_fixe(rule_val, amount_type,
                                                                               amount_fixe)
        }

    def _return_input_for_regul(self, input_name, struct_id):

        InputType = self.env['hr.payslip.input.type'].sudo()
        input_id = InputType.search([('name', '=', input_name)], limit=1)
        if not input_id:
            input_id = InputType.create(
                {
                    "name": input_name,
                }
            )
        return input_id

    def create_regul(self, input_name, struct_id, regul_type):
        input_id = self._return_input_for_regul(input_name, struct_id)
        self.smartest_is_regul = True
        if regul_type == "deduction":
            signe_montant = "-"
        else:
            signe_montant = '+'
        return {'condition_select': "python",
                'condition_python': "result = ( inputs." + input_id.code + " and inputs." + input_id.code + ".amount)",
                'amount_select': "code",
                'amount_python_compute': "result =" + signe_montant + " abs( inputs." + input_id.code + ".amount)"}

    @api.model
    def create(self, vals):
        is_regul = False
        if 'smartest_rule_create_auto' in vals and vals['smartest_rule_create_auto'] == "other":
            if 'smartest_rule_type' in vals:
                if vals['smartest_rule_type'] == "contribution":
                    category_id = self._return_contribution_category()
                elif vals['smartest_rule_type'] == "taxable":
                    category_id = self._return_taxable_category()
                elif vals['smartest_rule_type'] == "regul_cot":
                    category_id = self._return_contribution_category()
                    is_regul = True
                elif vals['smartest_rule_type'] == "regul_lmp":
                    category_id = self._return_taxable_category()
                    is_regul = True

                vals['category_id'] = category_id.id
            if not vals['category_id']:
                raise ValidationError(
                    _('You must select a Category!')
                )
            if not is_regul and vals['smartest_rule_amount_type'] == "fixe":
                dict_general_config_fixe = self.create_fix_amount_rule(vals['smartest_rule_val'],
                                                                       vals['smartest_amount_value_type'],
                                                                       vals['smartest_amount_fixe_rule'])
                vals['condition_select'] = dict_general_config_fixe['condition_select']
                vals['amount_select'] = dict_general_config_fixe['amount_select']
                vals['amount_python_compute'] = dict_general_config_fixe['amount_python_compute']
            elif is_regul:
                dict_general_config_regul = self.create_regul(vals['name'], vals['struct_id'],
                                                              vals['smartest_regul_type'])
                vals['condition_select'] = dict_general_config_regul['condition_select']
                vals['condition_python'] = dict_general_config_regul['condition_python']
                vals['amount_select'] = dict_general_config_regul['amount_select']
                vals['amount_python_compute'] = dict_general_config_regul['amount_python_compute']

        return super(SmartestHrSalaryRule, self).create(vals)

    def write(self, vals):
        res = super(SmartestHrSalaryRule, self).write(vals)
        is_regul = False
        if 'smartest_rule_create_auto' in vals or 'smartest_rule_type' in vals or 'smartest_rule_amount_type' in vals or 'smartest_rule_val' in vals or 'smartest_amount_value_type' in vals or 'smartest_amount_fixe_rule' in vals or 'name' in vals or 'struct_id' in vals or 'smartest_regul_type' in vals:

            if self.smartest_rule_create_auto == "other":
                if self.smartest_rule_type == "contribution":
                    category_id = self._return_contribution_category()
                elif self.smartest_rule_type == "taxable":
                    category_id = self._return_taxable_category()
                elif self.smartest_rule_type == "regul_cot":
                    category_id = self._return_contribution_category()
                    is_regul = True
                elif self.smartest_rule_type == "regul_lmp":
                    category_id = self._return_taxable_category()
                    is_regul = True
                elif self.smartest_rule_type == "regul_base":
                    category_id = self._return_base_category()
                    is_regul = True
                self.category_id = category_id.id
                self.smartest_is_regul = is_regul
                if not self.category_id:
                    raise ValidationError(
                        _('You must select a Category!')
                    )
                if not self.struct_id:
                    raise ValidationError(
                        _('You must select a structure!')
                    )
                if not is_regul and self.smartest_rule_amount_type == "fixe":
                    dict_general_config_fixe = self.create_fix_amount_rule(self.smartest_rule_val,
                                                                           self.smartest_amount_value_type,
                                                                           self.smartest_amount_fixe_rule)
                    self.condition_select = dict_general_config_fixe['condition_select']
                    self.amount_select = dict_general_config_fixe['amount_select']
                    self.amount_python_compute = dict_general_config_fixe['amount_python_compute']
                elif is_regul:
                    dict_general_config_regul = self.create_regul(self.name, self.struct_id.id,
                                                                  self.smartest_regul_type)
                    self.condition_select = dict_general_config_regul['condition_select']
                    self.condition_python = dict_general_config_regul['condition_python']
                    self.amount_select = dict_general_config_regul['amount_select']
                    self.amount_python_compute = dict_general_config_regul['amount_python_compute']
        return res

    def _calculate_abbatement_irg(self, irg, pourcentage):
        abtmnt = irg * pourcentage / 100
        if abtmnt < 1000:
            return 1000
        elif abtmnt > 1500:
            return 1500

        else:
            return abtmnt

    def _calculate_abbatement_supp(self, R501, ab_irg, inf_bound, sup_bound):
        irg_abat_supp = ab_irg
        if inf_bound <= R501 < sup_bound:
            #  general case
            irg_abat_supp = ab_irg * 137 / 51 - 27925 / 8
        return irg_abat_supp

    def calculate_irg(self, R501, date_to):
        R501 = int(int(round(R501, 2)) / 10) * 10

        bareme = self.env['hr.bareme.irg'].sudo().search([
            ('smartest_active', '=', True),
            ('smartest_date_from', '<=', date_to),
            ('smartest_bound_to', '>=', R501),
            ('smartest_bound_from', '<=', R501)
        ], limit=1)

        if not bareme and R501 > 0:
            raise ValidationError(_(
                "You may need to review/setup your IRG Plan. If it doesn't make sens to you, "
                "please contact your administrator."
            ))

        irg = (
                      R501 - bareme.smartest_amount_deducted) * bareme.smartest_rate / 100 + bareme.smartest_amount_cumul
        ab_irg = 0

        if irg:
            ab_irg = abs(irg - self._calculate_abbatement_irg(irg, PrcntgeAbat))
            ab_irg = self._calculate_abbatement_supp(R501, ab_irg, 30000, 35000)

        return -(int(round(ab_irg, 2) * 10) / 10)

    def calculate_irg_abs(self, payslip, R501):
        payslip_id = self.env['hr.payslip'].browse(payslip)
        context = self.env.context
        smartest_case_perfect = context.get('smartest_case_perfect', False)

        if smartest_case_perfect:
            return self.calculate_irg(R501, payslip_id.date_to)

        R501_perfect = round(payslip_id.smartest_amount_imposable_perfect, RoundParam)

        if not R501_perfect:
            return 0.0

        irg_perfect = self.calculate_irg(int(int(R501_perfect) / 10) * 10, payslip_id.date_to)
        return round(R501 * irg_perfect / R501_perfect, RoundParam)

    def function_calculate(self, payslip, variable_name, number_days, number_hours, is_percentage, percentage,
                           percentage_base, attendance_dependency, calendar_paid):

        context = self.env.context

        smartest_case_perfect = context.get('smartest_case_perfect', False)

        payslip_id = self.env['hr.payslip'].browse(payslip)

        contract_id = payslip_id.contract_id
        pourcentage = int(percentage) / 100
        smartest_theoretic_worked_days = payslip_id.smartest_theoretic_worked_days

        smartest_worked_days = payslip_id.smartest_worked_days

        smartest_weekend_days = payslip_id.smartest_weekend_days

        paid_hourly_attendance = contract_id.paid_hourly_attendance

        smartest_theoretic_worked_hours = payslip_id.smartest_theoretic_worked_hours

        smartest_worked_hours = payslip_id.smartest_worked_hours

        hours_per_day = contract_id.resource_calendar_id.hours_per_day

        perfect_amount = contract_id[variable_name] if not is_percentage else percentage_base * contract_id[
            variable_name] / 100 * pourcentage
        amount = perfect_amount / smartest_theoretic_worked_hours * number_hours

        if smartest_case_perfect or not attendance_dependency:
            return perfect_amount

        if calendar_paid and not paid_hourly_attendance:
            return (perfect_amount / 30 * (
                    30 - smartest_theoretic_worked_days + smartest_worked_days - smartest_weekend_days + number_days)) + amount

        if paid_hourly_attendance:
            return (perfect_amount / smartest_theoretic_worked_hours * (
                    smartest_worked_hours + number_days * hours_per_day)) + amount

        if not paid_hourly_attendance:
            return (perfect_amount / smartest_theoretic_worked_days * (
                    smartest_worked_days + number_days)) + amount
        return 0

    def function_calculate_meal_transport(self, payslip, variable_name, number_days, number_hours, per_day,
                                          attendance_dependency, calendar_paid):

        context = self.env.context

        smartest_case_perfect = context.get('smartest_case_perfect', False)

        payslip_id = self.env['hr.payslip'].browse(payslip)

        contract_id = payslip_id.contract_id

        smartest_theoretic_worked_days = payslip_id.smartest_theoretic_worked_days

        smartest_worked_days = payslip_id.smartest_worked_days

        smartest_weekend_days = payslip_id.smartest_weekend_days

        paid_hourly_attendance = contract_id.paid_hourly_attendance

        smartest_theoretic_worked_hours = payslip_id.smartest_theoretic_worked_hours

        smartest_worked_hours = payslip_id.smartest_worked_hours

        hours_per_day = contract_id.resource_calendar_id.hours_per_day

        total_days = 30 if calendar_paid else smartest_theoretic_worked_days

        perfect_amount = total_days * contract_id[variable_name] if per_day else contract_id[variable_name]
        amount = perfect_amount / smartest_theoretic_worked_hours * number_hours

        if smartest_case_perfect or not attendance_dependency:
            return perfect_amount

        if calendar_paid and not paid_hourly_attendance:
            return (perfect_amount / 30 * (
                    30 - smartest_theoretic_worked_days + smartest_worked_days - smartest_weekend_days + number_days)) + amount

        if paid_hourly_attendance:
            return (perfect_amount / smartest_theoretic_worked_hours * (
                    smartest_worked_hours + number_days * hours_per_day)) + amount

        if not paid_hourly_attendance:
            return (perfect_amount / smartest_theoretic_worked_days * (
                    smartest_worked_days + number_days)) + amount
        return 0

    def calculate_iep_matrix(self, payslip, iep_base, iep_in, amount):
        payslip_id = self.env['hr.payslip'].browse(payslip)
        contract_id = payslip_id.contract_id
        if not iep_in:
            exp = contract_id.allowance_out_iep
        else:
            exp = contract_id.allowance_in_iep
        context = self.env.context
        smartest_case_perfect = context.get('smartest_case_perfect', False)
        if smartest_case_perfect:
            return exp / 100 * contract_id.wage
        taux_journalier = iep_base / 30
        abs_days = payslip_id.smartest_theoretic_worked_days - payslip_id.smartest_worked_days - payslip_id.smartest_weekend_days
        return exp / 100 * (iep_base + amount - (taux_journalier * abs_days))

    def _satisfy_condition(self, localdict):
        self.ensure_one()
        context = self.env.context
        smartest_case_perfect = context.get('smartest_case_perfect', False)
        if smartest_case_perfect and self.smartest_perfect_depends == "perfect_not_in_dependency":
            return False
        else:
                    return super(SmartestHrSalaryRule, self)._satisfy_condition(localdict)
