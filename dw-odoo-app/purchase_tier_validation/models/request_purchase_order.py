from datetime import timedelta
import datetime
import time
from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError, ValidationError

class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "tier.validation"]
    _state_from = ["draft"]
    _state_to = ["purchase"]

    _tier_validation_manual_config = True