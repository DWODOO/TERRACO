# -*- coding: utf-8 -*-

# Import Python libs
import datetime

# Import Odoo libs
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

QUARTERS = {
    '1': {'start': '01/01/', 'end': '31/03/'},
    '2': {'start': '01/04/', 'end': '30/06/'},
    '3': {'start': '01/07/', 'end': '30/09/'},
    '4': {'start': '01/10/', 'end': '31/12/'},
}
DATE_FORMAT = "%d/%m/%Y"


class SmartestHrAppraisalObjectiveType(models.Model):
    _name = 'hr.appraisal.objective.type'
    _description = 'Employee Objective Type'
    _order = 'sequence'

    name = fields.Char(
        'name',
        required=True,
        index=True
    )
    sequence = fields.Integer(
        'Sequence',
        default=10
    )
    description = fields.Text(
        'Description'
    )
    score = fields.Integer(
        'Score',
        default=10,
    )
    active = fields.Boolean(
        'Active',
        default=True
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _('The type name must be unique'))
    ]


class SmartestHrAppraisalObjective(models.Model):
    _name = 'hr.appraisal.objective'
    _description = 'Employee Objective'
    _order = 'type_id'
    _rec_name = 'description'

    employee_ids = fields.Many2many(
        'hr.employee',
        'objective_employee_rel',
        'objective_id',
        'employee_id',
        string='Employees'
    )
    appraisal_employee_id = fields.Many2one(
        'hr.employee',
        'Appraisal Employee',
        required=True,
        index=True,
        copy=False,
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
    )
    type_id = fields.Many2one(
        'hr.appraisal.objective.type',
        'Type',
        required=True,
        index=True,
    )
    total_score = fields.Integer(
        related='type_id.score',
        string='Total Score'
    )
    score = fields.Integer(
        'Score',
        default=0,
    )
    date_start = fields.Date(
        'Start Date',
        required=True
    )
    date_end = fields.Date(
        'Deadline',
        required=True
    )
    quarter = fields.Selection([
        ('1', 'First Quarter'),
        ('2', 'Second Quarter'),
        ('3', 'Third Quarter'),
        ('4', 'Forth Quarter'),
    ],
        string='Quarter',
        default='1'
    )
    description = fields.Text(
        "Description",
        required=True
    )
    active = fields.Boolean(
        'Active',
        default=True
    )

    @api.constrains('score', 'type_id')
    def _check_score(self):
        # The objective score must be always less than the total type score
        if self.filtered(lambda objective: objective.score > objective.type_id.score):
            raise ValidationError(
                _('The objective score must be less than the total type score')
            )
        # The objective score must be always positive
        if self.filtered(lambda objective: objective.score < 0):
            raise ValidationError(
                _('The objective score must be positive')
            )

    @api.onchange('quarter')
    def _onchange_quarter(self):
        if self.quarter:
            quarter = QUARTERS[self.quarter]
            current_year = str(fields.date.today().year)
            start = quarter['start'] + current_year
            end = quarter['end'] + current_year
            self.date_start = datetime.datetime.strptime(start, DATE_FORMAT)
            self.date_end = datetime.datetime.strptime(end, DATE_FORMAT)


class SmartestHrAppraisalObjectiveRating(models.Model):
    _name = 'hr.appraisal.objective.rating'
    _description = 'Employee Objective Rating'
    _order = 'objective_id'
    _rec_name = 'objective_id'

    appraisal_id = fields.Many2one(
        'hr.appraisal',
        'Appraisal',
        required=False,
        index=True,
    )
    objective_id = fields.Many2one(
        'hr.appraisal.objective',
        required=False,
        index=True,
    )
    appraisal_employee_id = fields.Many2one(
        'hr.employee',
        'Appraisal Employee',
        required=True,
        index=True,
        copy=False,
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
    )
    employee_id = fields.Many2one(
        'hr.employee',
        related='appraisal_id.employee_id',
        store=True,
        index=True,
    )
    objective_type_id = fields.Many2one(
        'hr.appraisal.objective.type',
        related='objective_id.type_id',
        store=True,
        index=True,
    )
    objective_score = fields.Integer(
        'Objective Score',
        related='objective_id.score'
    )
    rating = fields.Integer(
        'Rating',
        default=0,
    )
    progress = fields.Integer(
        'Progress',
        default=0,
        compute='_compute_progress',
        store=True
    )
    employee_comment = fields.Html(
        'Employee Comments'
    )
    appraisal_employee_comment = fields.Html(
        'Appraisal Employee Comments'
    )

    @api.constrains('objective_score', 'rating')
    def _check_rating(self):
        # The rating must be always less than the objective score
        if self.filtered(lambda objective: objective.rating > objective.objective_score):
            raise ValidationError(
                _('The objective score must be less than the total type score')
            )

        # The objective rating must be always positive
        if self.filtered(lambda objective: objective.rating < 0):
            raise ValidationError(
                _('The objective rating must be positive')
            )

    @api.depends('objective_score', 'rating')
    def _compute_progress(self):
        """
        Compute the progress as a Percent (Rating/Score) to use it as a progressbar
        """
        for objective in self:
            if objective.rating <= objective.objective_score and objective.objective_score > 0:
                objective.progress = int(objective.rating / objective.objective_score * 100)
            else:
                objective.progress = 100

    def do_comment(self):
        """
        Open 'hr.appraisal.objective.rating' comment view and allow employee/appraisal employee to post comments
        :return: Action - hr.appraisal.objective.rating Form View
        """
        self.ensure_one()

        # Get Comment Form View
        comment_form = self.env.ref('smartest_hr_appraisal.view_hr_appraisal_objective_rating_comment_form', False)

        # If the form view is not found then do nothing
        if not comment_form:
            return

        # Build context
        context = dict(self._context, self_comment=self.env.user == self.employee_id.user_id)

        # Return Action to open Comment Form
        return {
            'name': _('Additional Comments'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.appraisal.objective.rating',
            'view_id': comment_form.id,
            'target': 'new',
            'res_id': self.id,
            'context': context
        }
