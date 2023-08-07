# -*- coding: utf-8 -*-

# Import Odoo libs
from odoo import _, api, fields, models


class SmartestHrAppraisalFactorCategory(models.Model):
    _name = 'hr.appraisal.factor.category'
    _description = "Employee Performance Factor Category"
    _order = 'sequence'

    name = fields.Char(
        'Name',
        required=True,
        index=True,
        translate=True
    )
    sequence = fields.Integer(
        'Sequence',
        default=10
    )
    description = fields.Text(
        'Description',
        translate=True
    )
    factor_ids = fields.One2many(
        'hr.appraisal.factor',
        'category_id'
    )
    factor_count = fields.Integer(
        'Number of factors',
        compute='_compute_factor_count'
    )
    active = fields.Boolean(
        'Active',
        default=True
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _('The category name must be unique'))
    ]

    @api.depends('factor_ids')
    def _compute_factor_count(self):
        for category in self:
            category.factor_count = len(category.factor_ids)

    def action_view_factors(self):
        self.ensure_one()

        # If no factor is related to this category then do nothing
        if not self.factor_ids:
            return

        # Build action
        action = {
            'name': _('Category Factors'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.appraisal.factor',
        }

        # Get factor views
        form_view = self.env.ref('smartest_hr_appraisal.view_hr_appraisal_factor_form', False)
        tree_view = self.env.ref('smartest_hr_appraisal.view_hr_appraisal_factor_tree', False)

        # If only one factor then open its form view. Otherwise open the list view
        if len(self.factor_ids) == 1:
            action['views'] = [(form_view.id, 'form')]
            action['res_id'] = self.factor_ids.id
            action['view_mode'] = 'form'
        else:
            action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]
            action['domain'] = [('id', 'in', self.factor_ids.ids)]

        # Return Action
        return action
