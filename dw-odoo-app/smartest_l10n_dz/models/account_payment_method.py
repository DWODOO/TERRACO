# -*- coding: utf-8 -*-
from odoo import fields, models


class PaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    apply_stamp_duty_tax = fields.Boolean(
        "Apply Stamp Duty?",
    )
