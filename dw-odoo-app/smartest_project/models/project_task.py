# -*- coding: utf-8 -*-
import re
import logging
from ast import literal_eval

# Import Odoo libs
from odoo import _, api, Command, fields, models
from odoo.osv import expression
from datetime import date

_logger = logging.getLogger(__name__)


class SmartestProjectTask(models.Model):
    _inherit = 'project.task'

    def _get_default_sprint(self):
        domain = [('state', '=', 'ongoing'), ('team_id.user_ids', 'in', self.env.user.id)]
        return self.env['project.sprint'].search(domain, limit=1)

    def _get_field_default_sprint(self):
        default_sprints = self.env.context.get('default_sprint_ids')
        if default_sprints:
            return default_sprints
        return self._get_default_sprint()

    smartest_dashboard_state = fields.Selection(
        related='stage_id.smartest_dashboard_state',
        store=True
    )
    type = fields.Selection([
        ('feature', 'Feature'),
        ('support', ' Support'),
        ('tache', 'Tache'),
    ],
        default='tache'
    )

    difficulty = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ],
        default='1'
    )
    user_ids_domain = fields.Char(
        compute='_compute_users_domain'
    )
    smartest_task_key = fields.Char(
        string='Task Key',
        readonly=True,
        store=True,
    )
    stage_id = fields.Many2one(
        domain="[('project_ids', '=', project_id), ('user_id', '=', False)]"
    )
    progress = fields.Float(
        string="Progress",
        store=True,
        group_operator="avg",
        help="Display progress of current task."
    )
    new_progress = fields.Integer(
        string="Progress"
    )
    sprint_ids = fields.Many2many(
        comodel_name='project.sprint',
        relation='project_sprint_project_task_rel',
        column1='project_task_id',
        column2='project_sprint_id',
        ondelete="restrict",
        domain="[('team_id', '=', team_id)]",
        oldname='sprint',
        default=_get_field_default_sprint
    )
    ongoing_sprint_id = fields.Many2one(
        comodel_name='project.sprint',
        ondelete="restrict",
        domain="[('team_id', '=', team_id)]",
        compute='_compute_ongoing_sprint_id',
        inverse='_inverse_ongoing_sprint_id',
        store=True,
        index=True,
    )
    team_id = fields.Many2one(
        comodel_name='project.teams',
        oldname='team',
        default=lambda self: self.env['project.teams'].search([('user_ids','in', self.env.user.id)], limit=1),
        compute='_compute_team_id',
        store=True,
        index=True,
    )
    smartest_use_sprint = fields.Boolean(
        related='project_id.smartest_use_sprint'
    )
    is_closed = fields.Boolean(
        related='stage_id.is_closed',
        store=True
    )

    _sql_constraints = [
        ('smartest_task_key_uniq', 'unique(smartest_task_key)', _('The task key must be unique'))
    ]

    @api.onchange('new_progress')
    def _onchange_new_progress(self):
        if self.new_progress > 100:
            self.new_progress = 100
        self.progress = self.new_progress

    @api.onchange('progress')
    def _onchange_progress(self):
        self.new_progress = int(self.progress)

    @api.onchange('user_ids_domain', 'team')
    def _onchange_user_ids_domain(self):
        base_domain = [('share', '=', False), ('active', '=', True)]
        return {
            'domain': {
                'user_ids': expression.AND([base_domain, literal_eval(str(self.user_ids_domain))])
            }
        }

    @api.onchange('stage_id')
    def _smartest_onchange_stage_id(self):
        today = date.today()
        if self.stage_id.smartest_dashboard_state == 'ongoing':
            self.planned_date_begin = today

        if self.stage_id.smartest_dashboard_state == 'done':
            self.date_deadline = today

    # @api.onchange('smartest_use_sprint', 'project_id')
    # def _onchange_smartest_use_sprint(self):
    #     sprints = [Command.clear()]
    #     default_sprint = self._get_default_sprint()
    #     if self.smartest_use_sprint and default_sprint:
    #         sprints.append(Command.link(default_sprint.id))
    #     self.sprint_ids = sprints

    @api.depends('project_id.smartest_task_assign_mode', 'project_id.message_follower_ids', 'team_id')
    def _compute_users_domain(self):
        for task in self:
            assign_mode = task.project_id.smartest_task_assign_mode
            if assign_mode == 'followers_and_team':
                task.user_ids_domain = "['|', {followers_domain}, {team_domain}]".format(
                    followers_domain="('partner_id', 'in', %s)" % task.project_id.message_follower_ids.partner_id.ids,
                    team_domain="('id', 'in', %s)" % task.team_id.user_ids.ids
                )
            elif assign_mode == 'followers':
                task.user_ids_domain = "[('partner_id', 'in', %s)]" % task.project_id.message_follower_ids.partner_id.ids
            elif assign_mode == 'team':
                task.user_ids_domain = "[('id', 'in', %s)]" % task.team_id.user_ids.ids
            else:
                task.user_ids_domain = "[('id', '!=', False)]"

    @api.depends('user_ids')
    def _compute_team_id(self):
        Team = self.env['project.teams']
        for task in self:
            if task.user_ids:
                task.team_id = Team.search([('user_ids', 'in', task.user_ids.ids)], limit=1)

    @api.depends('sprint_ids')
    def _compute_ongoing_sprint_id(self):
        for task in self:
            sprints = task.sprint_ids.filtered(lambda s: s.state == 'ongoing')
            task.ongoing_sprint_id = sprints[0] if len(sprints) > 1 else sprints

    def _inverse_ongoing_sprint_id(self):
        for task in self:
            if task.ongoing_sprint_id:
                task.sprint_ids = [Command.link(task.ongoing_sprint_id.id)]

    def name_get(self):
        result = []
        for rec in self:
            name = rec.name
            if rec.smartest_task_key:
                name = '#%s: %s' % (rec.smartest_task_key, name)
            result.append((rec.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            task_ids = []
            if operator in positive_operators:
                task_ids = list(
                    self._search([('smartest_task_key', '=', name)] + args, limit=limit,
                                 access_rights_uid=name_get_uid))
            if not task_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                task_ids = list(self._search(args + [('smartest_task_key', operator, name)], limit=limit))
                if not limit or len(task_ids) < limit:
                    limit2 = (limit - len(task_ids)) if limit else False
                    product2_ids = self._search(args + [('name', operator, name), ('id', 'not in', task_ids)],
                                                limit=limit2, access_rights_uid=name_get_uid)
                    task_ids.extend(product2_ids)
            elif not task_ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = expression.OR([
                    ['&', ('smartest_task_key', operator, name), ('name', operator, name)],
                    ['&', ('smartest_task_key', '=', False), ('name', operator, name)],
                ])
                domain = expression.AND([args, domain])
                task_ids = list(self._search(domain, limit=limit, access_rights_uid=name_get_uid))
            if not task_ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    task_ids = list(self._search([('smartest_task_key', '=', res.group(2))] + args, limit=limit,
                                                 access_rights_uid=name_get_uid))
            # still no results, partner in context: search on supplier info as last hope to find something
            if not task_ids and self._context.get('partner_id'):
                suppliers_ids = self.env['product.supplierinfo']._search([
                    ('name', '=', self._context.get('partner_id')),
                    '|',
                    ('product_code', operator, name),
                    ('product_name', operator, name)], access_rights_uid=name_get_uid)
                if suppliers_ids:
                    task_ids = self._search([('product_tmpl_id.seller_ids', 'in', suppliers_ids)], limit=limit,
                                            access_rights_uid=name_get_uid)
        else:
            task_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return task_ids

    @api.model
    def create(self, vals):
        task = super(SmartestProjectTask, self).create(vals)
        task._generate_task_key(update_old=False)
        return task

    def _generate_task_key(self, update_old=True):
        """
        Attribute Task Key for all tasks without keys
        :return:
        """
        if not update_old:
            task_to_generate = self - self.filtered('smartest_task_key')
        else:
            task_to_generate = self

        for task in task_to_generate:
            sequence = task.project_id.smartest_task_sequence_id
            if sequence:
                task.write({
                    'smartest_task_key': sequence.next_by_id()
                })

    @api.model
    def _get_default_personal_stage_create_vals(self, user_id):
        # Override to return an empty list to avoid creating personal stages
        return []

    def _populate_missing_personal_stages(self):
        try:
            super(SmartestProjectTask, self)._populate_missing_personal_stages()
        except IndexError:
            _logger.info("Bypass index error on personal stage.")
