# -*- coding: utf-8 -*-

from datetime import datetime
import pytz

# Import Odoo libs
from odoo import api, Command, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class SmartestSprint(models.Model):
    _name = 'project.sprint'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Project Sprint'
    _order = 'date_begin asc, team_id'

    name = fields.Char(
        string='Reference',
        index=True,
        readonly=True,
        oldname='reference'
    )
    user_ids = fields.Many2many(
        comodel_name='res.users',
        ondelete="cascade",
        states={'draft': [('readonly', False)]},
        readonly=True,
        tracking=True
    )
    team_id = fields.Many2one(
        comodel_name='project.teams',
        states={'draft': [('readonly', False)]},
        readonly=True,
        required=True
    )
    date_begin = fields.Datetime(
        string='Start Date',
        tracking=True,
        states={'draft': [('readonly', False)]},
        readonly=True,
        required=True,
        compute='_compute_date_begin'
    )
    date_end = fields.Datetime(
        string='End Date',
        tracking=True,
        states={'draft': [('readonly', False)]},
        readonly=True,
        required=True,
        store=True,
        compute='_compute_date_end'
    )
    goal = fields.Html(
        states={'draft': [('readonly', False)]},
        readonly=True,
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ongoing', 'Ongoing'),
        ('closed', 'Closed')
    ],
        string='State',
        default='draft',
        required=True,
        index=True,
    )
    task_ids = fields.Many2many(
        comodel_name='project.task',
        relation='project_sprint_project_task_rel',
        column1='project_sprint_id',
        column2='project_task_id',
        string='Tasks',
        states={'draft': [('readonly', False)]},
        readonly=True,
    )
    planned_tasks = fields.Many2many(
        comodel_name='project.task',
        relation='project_sprint_project_task_planned_rel',
        column1='project_sprint_id',
        column2='project_task_id',
        string='Planned Tasks',
        readonly=True,
    )
    tasks_count = fields.Integer(
        compute='_compute_tasks_count'
    )
    tasks_done_rate = fields.Float(
        compute='_compute_tasks_count'
    )

    # @api.constrains('state')
    # def _check_state(self):
    #     for sprint in self:
    #         if sprint.team_id.sprint_ids.filtered(lambda s: s.id != sprint.id and sprint.state == 'ongoing') - sprint:
    #             raise ValidationError(
    #                 _('You can not run a sprint while another one is already running for the same team.')
    #             )
    #     return True

    @api.onchange('team_id')
    def _onchange_team_id(self):
        self.user_ids = [Command.clear()] + [Command.link(u.id) for u in self.team_id.user_ids]
    
    @api.depends('task_ids')
    def _compute_tasks_count(self):
        for sprint in self:
            count = len(sprint.task_ids)
            sprint.tasks_count = count
            if count != 0:
                done_tasks = sprint.task_ids.filtered('stage_id.is_closed')
                sprint.tasks_done_rate = len(done_tasks) / count * 100
            else:
                sprint.tasks_done_rate = 0

    @api.depends('team_id')
    def _compute_date_begin(self):
        today = fields.Datetime.now()
        calendar = self.env.company.resource_calendar_id
        tz = self.env.user.tz
        user_pytz = pytz.timezone(tz) if tz else pytz.utc
        for sprint in self:
            date_begin = today
            if sprint.team_id:
                domain = [('team_id', '=', sprint.team_id.id),]
                if sprint.id:
                    domain.append(('id', '!=', sprint.id))
                previous_sprint = self.search(domain, order='date_end desc', limit=1)
                if previous_sprint:
                    date_begin = max(previous_sprint.date_end, today)

            date_begin = calendar._get_closest_work_time(
                (date_begin + relativedelta(days=1)).replace(hour=0, minute=0, second=0, tzinfo=user_pytz)
            )
            sprint.date_begin = date_begin and date_begin.replace(tzinfo=None) or today

    @api.depends('date_begin', 'team_id')
    def _compute_date_end(self):
        for sprint in self:
            if sprint.date_begin and sprint.team_id:
                sprint.date_end = sprint.date_begin + relativedelta(days=sprint.team_id.sprint_period)

    def button_start_sprint(self):
        self.ensure_one()
        if any(sprint.state != 'draft' for sprint in self):
            raise ValidationError(
                _('Only draft sprints can be started.')
            )

        tasks_to_run_on_this_sprint = self.env['project.task'].search([
            ('team_id', '=', self.id),
            ('stage_id.is_closed', '=', False),
        ])
        tasks_to_run_on_this_sprint.write({
            'sprint_ids': [Command.link(self.id)]
        })
        self.write({'state': 'ongoing'})
        
    def button_close_sprint(self):
        return self._action_close_sprint()
        
    def _action_close_sprint(self):
        if any(sprint.state != 'ongoing' for sprint in self):
            raise ValidationError(
                _('Only ongoing sprints can be closed.')
            )

        self.write({'state': 'closed'})

    def action_view_tasks(self):
        self.ensure_one()
        view_mode = 'kanban,tree,form'
        if self.tasks_count == 0:
            view_mode = 'tree,kanban,form'
        return {
            'type': 'ir.actions.act_window',
            'name': _("Tasks"),
            'res_model': 'project.task',
            'view_mode': view_mode,
            'domain': [('sprint_ids', '=', self.id)],
            'context': {'default_sprint_ids': [Command.link(self.id)]},
        }

    def action_view_done_tasks(self):
        action = self.action_view_tasks()
        action['view_mode'] = 'tree,kanban,form'
        domain = action.get('domain', [])
        domain.append(('stage_id.is_closed', '=', True))
        action['domain'] = domain
        return action

    @api.model
    def _cron_close_sprint(self):
        today = datetime.today()
        sprints_to_close = self.search([
            ('team_id.sprint_auto_close', '=', True),
            ('state', '=', 'ongoing'),
            ('date_end', '<=', today),
        ])
        sprints_to_close._action_close_sprint()

    @api.model
    def create(self, vals):
        sequence = False
        if vals.get('team_id'):
            team = self.env['project.teams'].browse(vals['team_id'])
            if team.sprint_sequence_id:
                sequence = team.sprint_sequence_id.next_by_id()
        if not sequence:
            sequence = self.env['ir.sequence'].next_by_code('project.sprint') or _('New')
        vals['name'] = sequence
        return super(SmartestSprint, self).create(vals)

    def unlink(self):
        if any(s.state != 'draft' for s in self):
            raise ValidationError(
                _('Only draft sprints can be deleted.')
            )
        return super(SmartestSprint, self).unlink()
