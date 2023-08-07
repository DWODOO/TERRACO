from datetime import timedelta
import datetime
import time
from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_conforme = fields.Boolean(string='Bon Conforme')

    def button_validate(self):
        for picking in self:
            if not picking.is_conforme and picking.picking_type_code == 'incoming':
                raise ValidationError(_('Merci de verifier que le Bon est conforme!.'))
            return super(StockPicking, self).button_validate()