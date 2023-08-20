
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError



class SmartestSaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery = fields.Boolean(
        String="possibility of delivery",
        store=True,
        compute="_compute_delivery_invoice"
    )

    @api.depends("invoice_ids.delivery")
    def _compute_delivery_invoice(self):
        livraison = False
        for rec in self:
            if rec.invoice_ids:
                for invoice in rec.invoice_ids:
                    if invoice.delivery == True:
                        livraison = True
            rec.delivery = livraison


class SmartestSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('discount')
    def discount_check_per_vendor(self):
        for line in self:
            if line.discount > line.order_id.user_id.discount_limit:
                raise ValidationError(_('You have exceed the discount limit for vendor!. {}'.format(
                    line.order_id.user_id.discount_limit)))


class SmartestAtlasHouseResUsers(models.Model):
    _inherit = 'res.users'

    discount_limit = fields.Float('Discount Limit')