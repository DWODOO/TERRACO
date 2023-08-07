# -*- coding: utf-8 -*-

from odoo import models, fields, _, api


class SmartestTrainingPlan(models.Model):
    _name = 'plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Training Plan'
    _rec_name = 'smartest_name'

    smartest_plan_id = fields.Char(string="Plan ID", readonly=True, index=True, default=lambda self: _('New'))
    smartest_name = fields.Char("Name", required="1")
    smartest_start_date = fields.Date("Start Date")
    smartest_end_date = fields.Date("End Date")
    smartest_color = fields.Integer(default=0)
    smartest_status = fields.Selection(
        [('draft', 'Draft'), ('active', 'Active'), ('done', 'Done'), ('cancel', 'Cancel')],
        string='Status', default='draft')
    smartest_company_id = fields.Many2one('res.company', string='Company',
                                          default=lambda self: self.env.user.company_id)
    smartest_start_formation_plan = fields.One2many('formation.start','smartest_plan_parent_id')


    def create_formations(self):
        return  {
            'type': 'ir.actions.act_window',
            'res_model': 'formation.start',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': False,
            'target': 'current',
            'context': {
                'default_smartest_plan_parent_id': self.id
            }
        }

    def create_formations_smart_button(self):
        return  {
            'name' : "Formations Planifiées",
            'type': 'ir.actions.act_window',
            'res_model': 'formation.start',
            'view_mode': 'tree,form',
            'view_type': 'tree,form',
            'view_id': False,
            'domain' : [('smartest_plan_parent_id','=',self.id)],
            'target': 'current',
        }

    def action_active(self):
        self.smartest_status = 'active'

    def action_complete(self):
        self.smartest_status = 'done'

    def action_cancel(self):
        self.smartest_status = 'cancelled'

    @api.model
    def create(self, values):
        if values.get('smartest_plan_id', _('New') == _('New')):
            values['smartest_plan_id'] = self.env['ir.sequence'].next_by_code('smartest.plan.seq') or _('New')
        result = super(SmartestTrainingPlan, self).create(values)
        return result
