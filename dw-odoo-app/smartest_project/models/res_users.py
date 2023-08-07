from odoo import api, fields, models, tools, SUPERUSER_ID, _


class SmartestProjectUsers(models.Model):
    _inherit = 'res.users'

    sprint_id = fields.Many2many(
        comodel_name='project.sprint',
        ondelete="cascade"
    )
    team_id = fields.Many2many(
        comodel_name='project.teams',
        ondelete="cascade"
    )

