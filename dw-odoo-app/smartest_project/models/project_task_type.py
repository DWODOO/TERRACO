# -*- coding: utf-8 -*-

# Import Odoo libs
from odoo import fields, models


class SmartestProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    smartest_use_by_default = fields.Boolean(
        string='Use by default on new projects'
    )
    smartest_dashboard_state = fields.Selection([
        ('backlog', 'Backlog'),
        ('ongoing', 'Ongoing'),
        ('done', 'Done'),
        ('rejected', 'Rejected'),
    ],
        string="Dashboard State",
        default='ongoing',
        required=True,
        index=True
    )
