# -*- coding: utf-8 -*-

# Import Odoo libs
from odoo import api, Command, fields, models, tools, SUPERUSER_ID, _


class SmartestProjectProject(models.Model):
    _inherit = 'project.project'

    def _default_team(self):
        return self.env['project.teams'].search([
            ('user_ids', 'in', self.env.user.ids),
        ], limit=1)

    smartest_task_sequence_id = fields.Many2one(
        comodel_name='ir.sequence',
        string='Task Sequence',
    )
    smartest_team_id = fields.Many2one(
        comodel_name='project.teams',
        string='Team',
        default=_default_team
    )
    smartest_task_assign_mode = fields.Selection([
        ('all', 'Assign any user'),
        ('followers', 'Only Allow assigning followers'),
        ('team', 'Only Allow assigning team members'),
        ('followers_and_team', 'Only Allow assigning followers and team members'),
    ],
        default='all',
        string='Task assign mode'
    )
    smartest_use_sprint = fields.Boolean(
        string='Use sprints ?',
        default=True
    )

    def _get_default_stage_ids(self):
        return self.env['project.task.type'].search([('smartest_use_by_default', '=', True)]).ids

    type_ids = fields.Many2many(
        'project.task.type',
        string='Project stages',
        default=_get_default_stage_ids
    )

    @api.model
    def create(self, vals):
        project = super(SmartestProjectProject, self).create(vals)
        if project.smartest_team_id:
            project.message_subscribe(partner_ids=project.mapped('smartest_team_id.user_ids.partner_id').ids)
        return project