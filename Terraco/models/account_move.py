from odoo import models,fields,api,_
from odoo.exceptions import ValidationError

class AccountMove(models.Model):

    _inherit = 'account.move'

    restourne = fields.Boolean(
        String="Restourne",
        domain="[('move_type', '=', 'out_refund')]"
    )
    delivery = fields.Boolean(
        String="possibility of delivery",
        store=True,
        compute="_compute_delivery"
    )
    @api.depends("payment_state")
    def _compute_delivery(self):
        for rec in self:
            if rec.payment_state == 'paid':
                rec.delivery = True


