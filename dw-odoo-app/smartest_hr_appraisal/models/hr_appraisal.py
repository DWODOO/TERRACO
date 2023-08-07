# -*- coding: utf-8 -*-

# Import Odoo libs
import pdb

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class SmartestHrAppraisalLine(models.Model):
    _name = 'hr.appraisal.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Performance Assessment'
    _order = 'appraisal_id,factor_id'

    appraisal_id = fields.Many2one(
        'hr.appraisal',
        'Appraisal',
        required=True,
        index=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        related='appraisal_id.employee_id',
        store=True
    )
    appraisal_employee_id = fields.Many2one(
        'hr.employee',
        'Appraisal Employee',
        required=True,
        index=True,
        copy=False,
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
    )
    factor_id = fields.Many2one(
        'hr.appraisal.factor',
        'Appraisal Factor',
        required=True,
        index=True,
    )
    factor_category_id = fields.Many2one(
        'hr.appraisal.factor.category',
        'Category',
        related='factor_id.category_id',
        store=True,
        index=True,
    )
    level_id = fields.Many2one(
        'hr.appraisal.level',
        'Appraisal Level',
        required=False,
        readonly=True,
        store=True,
        compute='_compute_level_id',
    )
    factor_description = fields.Text(
        related='factor_id.description'
    )
    score = fields.Float(
        'Score',
    )
    comment_count = fields.Integer(
        '# Comments',
        compute='_compute_comment_count'
    )

    _sql_constraints = [
        (
            'factor_evaluation_uniq',
            'unique(factor_id, appraisal_employee_id, appraisal_id)',
            _('Only single evaluation by factor is possible')
        )
    ]

    @api.depends('score')
    def _compute_level_id(self):
        AppraisalLevel = self.env['hr.appraisal.level']

        for line in self:
            # Search the level that holds the score value
            level_id = AppraisalLevel.search([
                ('score_interval_min', '<=', line.score),
                ('score_interval_max', '>=', line.score),
            ], limit=1)

            # Setup level
            line.level_id = level_id

    @api.depends('message_ids')
    def _compute_comment_count(self):
        for line in self:
            line.comment_count = len(line.message_ids)

    def do_comment(self):
        self.ensure_one()

        # Get Comment Form View
        comment_form = self.env.ref('smartest_hr_appraisal.view_hr_appraisal_comment_wizard_form', False)

        # If the form view is not found then do nothing
        if not comment_form:
            return

        # Build context
        context = dict(self._context, default_appraisal_line_id=self.id)

        # Return Action to open Comment Form
        return {
            'name': _('Post your comment'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.appraisal.comment.wizard',
            'view_id': comment_form.id,
            'target': 'new',
            'context': context
        }

    @api.model_create_multi
    def create(self, vals_list):
        # Patch mail_create_nolog to context to avoid creating tracking messages
        context = dict(self._context, mail_create_nolog=True)

        # Call super
        return super(SmartestHrAppraisalLine, self.with_context(context)).create(vals_list)

    def write(self, vals):
        # Patch tracking_disable to context to avoid creating tracking messages
        context = dict(self._context, tracking_disable=True)

        # Limitation:  Don't allow scores modification if the current_user is not an evaluator or module admin
        appraisal = self.env['hr.appraisal'].browse(vals.get('appraisal_id')) or self.appraisal_id
        managers = appraisal.manager_ids.mapped('user_id')
        collaborators = appraisal.collaborators_ids.mapped('user_id')
        # colleagues = appraisal.colleagues_ids.mapped('user_id')
        validator = appraisal.validator_id.mapped('user_id')
        state = appraisal.state
        uid = self.env.user
        is_appraisal_admin = self.env.user.has_group('hr_appraisal.group_hr_appraisal_manager')
        if ((uid in managers) or (uid == validator) or (uid in collaborators) or (uid in colleagues) or ('message_ids' in vals)\
                or is_appraisal_admin) and state == 'pending':
            return super(SmartestHrAppraisalLine, self.with_context(context)).write(vals)
        if (uid == validator) and state == 'done':
            return super(SmartestHrAppraisalLine, self.with_context(context)).write(vals)
        raise UserError(_('Updating fields is not allowed.'))


class SmartestHrAppraisal(models.Model):
    _inherit = "hr.appraisal"

    def _get_lines_domain(self):
        # Initialize variables
        current_user = self.env.user

        # Build domain
        domain = [(1, '=', 1)]
        # domain = [
        #     '|'
        #     ('employee_id.user_id', '=', current_user.id),
        #     ('appraisal_employee_id.user_id', '=', current_user.id)
        # ]

        # Return
        return domain

    def _get_employee_domain(self):
        # Initialize variables
        HrEmployee = self.env['hr.employee']
        user = self.env.user
        company_id = user.company_id
        domain = [('company_id', 'in', (False, company_id.id))]
        employee = HrEmployee.search([('user_id', '=', user.id)], limit=1)

        if not employee:
            return domain

        # Get employees that the current users is allowed to evaluate
        employee_ids = HrEmployee.search(domain).filtered(
            lambda e: employee.id in (e.appraisal_manager_ids.ids if e.appraisal_by_manager else []) +
                      (e.appraisal_collaborators_ids.ids if e.appraisal_by_collaborators else []) +
                      (e.appraisal_colleagues_ids.ids if e.appraisal_by_colleagues else [])
        )

        # Update domain
        domain.append(('id', 'in', employee_ids.ids))

        # Return domain
        return domain

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self = self.sudo()  # fields are not on the employee public
        if self.employee_id:
            self.company_id = self.employee_id.company_id
            self.manager_appraisal = self.employee_id.appraisal_by_manager
            self.manager_ids = self.employee_id.appraisal_manager_ids
            self.colleagues_appraisal = self.employee_id.appraisal_by_colleagues
            self.colleagues_ids = self.employee_id.appraisal_colleagues_ids
            self.employee_appraisal = self.employee_id.appraisal_self
            self.collaborators_appraisal = self.employee_id.appraisal_by_collaborators
            self.collaborators_ids = self.employee_id.appraisal_collaborators_ids
            self.validator_id = self.employee_id.appraisal_validator_id

    validator_id = fields.Many2one('hr.employee', string='Validator')

    appraisal_line_ids = fields.One2many(
        'hr.appraisal.line',
        'appraisal_id',
        readonly=False,
        states={'done': [('readonly', False)], 'cancel': [('readonly', True)]},
        # domain=_get_lines_domain
    )
    objective_rating_ids = fields.One2many(
        'hr.appraisal.objective.rating',
        'appraisal_id',
        readonly=False,
        states={'done': [('readonly', False)], 'cancel': [('readonly', True)]},
        # domain=_get_lines_domain,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        domain=_get_employee_domain
    )
    appraisal_validator_id = fields.Many2one(
        'hr.employee',
        related='employee_id.appraisal_validator_id'
    )
    current_user_id = fields.Many2one(
        'res.users',
        string='Current usrr',
        compute='_compute_current_user_id',
        default=lambda self: self.env.user
    )
    show_appraisal_employee = fields.Boolean(
        compute='_compute_show_appraisal_employee'
    )
    overall_rating = fields.Selection([
        ('1', 'Development needed'),
        ('2', 'Meeting Expectations'),
        ('3', 'Exceed Expectations'),
        ('4', 'Outstanding'),
    ],
        string='Overall Rating',
        compute='_compute_overall_rating',
        store=True,
        readonly=False,
        inverse='_inverse_overall_rating'
    )
    employee_comment = fields.Text(
        'Employee comment'
    )
    evaluator_comment = fields.Text(
        'Evaluator comment'
    )
    evaluator_responsible_comment = fields.Text(
        'Evaluator Responsible comment'
    )
    total_score = fields.Float(
        'Final Mark',
        compute='_compute_total_score',
        store=True
    )
    user_can_unlock = fields.Boolean(
        compute='_compute_user_can_unlock',
        compute_sudo=True
    )

    @api.depends('appraisal_line_ids.score', 'total_score')
    def _compute_overall_rating(self):
        # Compute the total of all factor scores
        total_score_sum = sum(self.env['hr.appraisal.factor'].search([]).mapped('score'))

        if not total_score_sum:
            self.update({
                'overall_rating': False
            })
        else:
            for appraisal in self:
                # Compute the percent of the total mark
                result = appraisal.total_score / total_score_sum * 100

                if result <= 25:
                    appraisal.overall_rating = '1'
                elif result <= 50:
                    appraisal.overall_rating = '2'
                elif result <= 75:
                    appraisal.overall_rating = '3'
                else:
                    appraisal.overall_rating = '4'

    @api.depends('appraisal_line_ids.score')
    def _compute_total_score(self):
        for appraisal in self:
            # Compute the sum of all score in lines
            score_sum = sum(appraisal.mapped('appraisal_line_ids.score'))

            # Setup the total score
            appraisal.total_score = score_sum

    @api.depends('employee_id')
    def _compute_show_appraisal_employee(self):
        current_user = self.env.user
        for appraisal in self:
            appraisal.show_appraisal_employee = current_user == appraisal.employee_id.user_id

    @api.depends('state')
    def _compute_user_can_unlock(self):
        current_user = self.env.user
        for appraisal in self:
            appraisal.user_can_unlock = appraisal.state == 'done' \
                                          and current_user == appraisal.appraisal_validator_id.user_id

    def _compute_current_user_id(self):
        current_user = self.env.user
        for appraisal in self:
            appraisal.current_user_id = current_user

    def _inverse_overall_rating(self):
        pass

    def button_send_appraisal(self):
        self.ensure_one()

        # Search for the current employee (Evaluator)
        current_user = self.env.user
        current_employee = self.env['hr.employee'].search([('user_id', '=', current_user.id)])

        # Get employee objectives + general objectives
        objectives = self.employee_id.objective_ids + self.env['hr.appraisal.objective'].search([
            ('employee_ids', '=', False)
        ])

        # Append Objectives (by default)
        line_values = [(0, 0, {'objective_id': o.id, 'appraisal_employee_id': current_employee.id}) for o in objectives]
        objective_rating_ids = [(5, 0)] + line_values

        # Search for all factors that are not yet evaluated
        factors = self.env['hr.appraisal.factor'].search([])

        # Append appraisal lines (by default)
        line_values = [(0, 0, {'factor_id': f.id, 'appraisal_employee_id': current_employee.id}) for f in factors]
        appraisal_line_ids = [(5, 0)] + line_values

        # Update fields
        self.write({
            'objective_rating_ids': objective_rating_ids,
            'appraisal_line_ids': appraisal_line_ids,
        })

        # return super
        return super(SmartestHrAppraisal, self).button_send_appraisal()

    def button_unlock(self):
        # Raise error if any appraisal in self is not in pending state
        if self.filtered(lambda appraisal: not appraisal.user_can_unlock):
            raise ValidationError(
                _('You can not unlock this Appraisal.')
            )

        self.write({
            'state': 'pending'
        })

    def _read(self, fields):
        context = dict(self.env.context, smartest_bypass=True)
        return super(SmartestHrAppraisal, self.with_context(context))._read(fields)

    @api.model_create_multi
    def create(self, vals_list):
        context = dict(self.env.context, smartest_bypass=True)
        return super(SmartestHrAppraisal, self.with_context(context)).create(vals_list)

    def write(self, vals):
        context = dict(self.env.context, smartest_bypass=True)
        return super(SmartestHrAppraisal, self.with_context(context)).write(vals)
