# -*- coding:utf-8 -*-

from odoo import fields, models


class SmartetMessageReason(models.Model):
    _name = "smartest.message.reason"
    _description = "Validation/Reject Reason"

    name = fields.Char('Reason')
    smartest_is_reject = fields.Boolean("Is Reject Reason")
