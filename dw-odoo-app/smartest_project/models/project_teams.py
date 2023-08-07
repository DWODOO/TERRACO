# -*- coding: utf-8 -*-

# Import Odoo libs
from odoo import api, fields, models, SUPERUSER_ID, _


class SmartestTeams(models.Model):
    _name = 'project.teams'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Project Team'

    name = fields.Char(
        string='Team Name',
        tracking=True,
        required=True,
        index=True,
    )
    code = fields.Char(
        string='Code',
        tracking=True,
        required=True,
        index=True,
    )
    reference = fields.Char(
        string='Reference',
        required=True,
        readonly=True,
        default=_('New')
    )
    project_ids = fields.One2many(
        comodel_name='project.project',
        inverse_name='smartest_team_id',
        ondelete='restrict',
    )
    task_ids = fields.One2many(
        comodel_name='project.task',
        inverse_name='team_id',
        ondelete='restrict',
    )
    sprint_ids = fields.One2many(
        comodel_name='project.sprint',
        inverse_name='team_id',
    )
    ongoing_sprint_id = fields.Many2one(
        comodel_name='project.sprint',
        string='ongoing Sprint',
        compute='_compute_ongoing_sprint_id'
    )
    sprint_count = fields.Integer(
        compute='_compute_sprint_count'
    )
    task_count = fields.Integer(
        compute='_compute_task_count'
    )
    project_count = fields.Integer(
        compute='_compute_project_count'
    )
    department_id = fields.Many2one(
        comodel_name='hr.department',
        required=True,
        tracking=True
    )
    responsible_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        required=True,
    )
    planning_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Planing Responsible',
        required=True,
    )
    user_ids = fields.Many2many(
        comodel_name='res.users',
        ondelete="cascade",
        tracking=True,
        required=True
    )
    description = fields.Html(
        string='Description'
    )
    sprint_sequence_id = fields.Many2one(
        comodel_name='ir.sequence',
        string='Sprint Reference',
    )
    sprint_auto_close = fields.Boolean(
        string='Automatically close sprint?',
        default=True
    )
    sprint_period = fields.Integer(
        string='Sprint Period',
        default=15,
    )

    _sql_constraints = [
        ('code_unique', 'unique (code)', 'The team code is already used. Please choose another one.'),
        ('sprint_period_positive', 'check (sprint_period > 0)', 'The sprint period must be a strict positive value.'),
    ]

    @api.onchange('responsible_user_id')
    def _onchange_responsible_user_id(self):
        if self.responsible_user_id:
            self.planning_user_id = self.responsible_user_id

    @api.depends('sprint_ids')
    def _compute_sprint_count(self):
        for team in self:
            team.sprint_count = len(team.sprint_ids)

    @api.depends('task_ids')
    def _compute_task_count(self):
        for team in self:
            team.task_count = len(team.task_ids)

    @api.depends('project_ids')
    def _compute_project_count(self):
        for team in self:
            team.project_count = len(team.project_ids)

    @api.depends('sprint_ids')
    def _compute_ongoing_sprint_id(self):
        for team in self:
            ongoing_sprints = self.sprint_ids.filtered(lambda s: s.state == 'ongoing')
            team.ongoing_sprint_id = ongoing_sprints[0] if len(ongoing_sprints) > 1 else ongoing_sprints

    def action_view_sprints(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _("Sprints"),
            'res_model': 'project.sprint',
            'view_mode': 'tree,form',
            'domain': [('team_id', 'in', self.ids)],
            'context': {'default_team_id': self.ids[0]},
        }

    def action_view_ongoing_sprint(self):
        action = self.action_view_tasks()
        domain = action.get('domain', [])
        domain.append(('sprint_ids.state', '=', 'ongoing'))
        action['domain'] = domain
        return action
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': _("Ongoing Sprints"),
        #     'res_model': 'project.sprint',
        #     'view_mode': 'tree,form',
        #     'domain': [('team_id', 'in', self.ids), ('state', '=', 'ongoing')],
        #     'context': {'default_team_id': self.ids[0]},
        # }

    def action_view_tasks(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Tasks"),
            'res_model': 'project.task',
            'view_mode': 'kanban,tree,form',
            'domain': [('team_id', 'in', self.ids)],
            'context': {'default_team_id': self.ids[0]},
        }

    def action_view_projects(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _("Projects"),
            'res_model': 'project.project',
            'view_mode': 'tree,kanban,form',
            'domain': [('smartest_team_id', 'in', self.ids)],
            'context': {'default_smartest_team_id': self.ids[0], 'default_search_groupby_stage': 1},
        }

    def _generate_sprint_sequence(self):
        self.ensure_one()
        return self.env['ir.sequence'].create({
            'name': 'SPRINT - %s' % self.name,
            'code': self.code,
            'prefix': (self.code or 'SPRINT') + '/%(y)sW%(woy)s/',
            'padding': 3,
        })

    @api.model
    def create(self, vals):
        team = super(SmartestTeams, self).create(vals)
        if not team.sprint_sequence_id:
            sprint_sequence = team._generate_sprint_sequence()
            if sprint_sequence:
                team.write({'sprint_sequence_id': sprint_sequence.id})
        return team
