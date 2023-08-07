# -*- coding: utf-8 -*-
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    cash_desk_id = fields.Many2one(
        'cash.desk',
        'Current used Cash Desk'
    )  # Regarding the user can have access to multiple cash desks, this field represent the current used desk
    # by the user
    cash_desk_ids = fields.Many2many(
        'cash.desk',
        string='Authorized Cash Desks'
    )  # This field represent the cash desks on which the user have access
    journal_id = fields.Many2one(
        related="cash_desk_id.journal_id"
    )  # Get the account.journal record from from the cash_desk_id field to facilitate access to the user
    # authorised journal.
