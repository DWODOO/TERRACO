# -*- coding:utf-8 -*-

from odoo import models, api, fields


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    leave_allowance = fields.Float(
        'Leave allowance',
        readonly=True,
        store=True,
    )
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    year_reference = fields.Integer()
