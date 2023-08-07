# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    members_emails = fields.Char(
        compute='_compute_members_emails'
    )

    @api.depends('member_ids')
    def _compute_members_emails(self):
        for team in self:
            team.members_emails = ','.join(team.mapped('member_ids.login'))
