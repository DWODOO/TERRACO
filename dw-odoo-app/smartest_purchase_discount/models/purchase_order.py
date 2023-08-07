from odoo import fields, models, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # adding discount to depends
    @api.depends("discount")
    def _compute_amount(self):
        return super()._compute_amount()

    def _convert_to_tax_base_line_dict(self):
        vals = super()._convert_to_tax_base_line_dict()
        vals.update({"discount": self.discount})
        return vals

    discount = fields.Float(string="Discount (%)", digits="Discount")

    def _get_discounted_price_unit(self):
        """Inheritable method for getting the unit price after applying
        discount(s).

        :rtype: float
        :return: Unit price after discount(s).
        """
        self.ensure_one()
        if self.discount:
            return self.price_unit * (1 - self.discount / 100)
        return self.price_unit

    def _get_stock_move_price_unit(self):
        """Get correct price with discount replacing current price_unit
        value before calling super and restoring it later for assuring
        maximum inheritability.

        """
        price_unit = False
        price = self._get_discounted_price_unit()
        if price != self.price_unit:
            # Only change value if it's different
            price_unit = self.price_unit
            self.price_unit = price
        price = super()._get_stock_move_price_unit()
        if price_unit:
            self.price_unit = price_unit
        return price

    # @api.onchange("product_qty", "product_uom")
    # def _onchange_quantity(self):
    #     """
    #     Check if a discount is defined into the supplier info and if so then
    #     apply it to the current purchase order line
    #     """
    #     if self.product_id:
    #         date = None
    #         if self.order_id.date_order:
    #             date = self.order_id.date_order.date()
    #         seller = self.product_id._select_seller(
    #             partner_id=self.partner_id,
    #             quantity=self.product_qty,
    #             date=date,
    #             uom_id=self.product_uom,
    #         )
    #         self._apply_value_from_seller(seller)
    #     return

    # @api.model
    # def _apply_value_from_seller(self, seller):
    #     """
    #     Overload this function to prepare other data from seller
    #     """
    #     if not seller:
    #         return
    #     self.discount = seller.discount

    def _prepare_account_move_line(self, move=False):
        vals = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        vals["discount"] = self.discount
        return vals

    # @api.model
    # def _prepare_purchase_order_line(
    #         self, product_id, product_qty, product_uom, company_id, supplier, po
    # ):
    #     """Apply the discount to the created purchase order"""
    #     res = super()._prepare_purchase_order_line(
    #         product_id, product_qty, product_uom, company_id, supplier, po
    #     )
        # partner = supplier.partner_id
        # uom_po_qty = product_uom._compute_quantity(product_qty, product_id.uom_po_id)
        # seller = product_id.with_company(company_id)._select_seller(
        #     partner_id=partner,
        #     quantity=uom_po_qty,
        #     date=po.date_order and po.date_order.date(),
        #     uom_id=product_id.uom_po_id,
        # )
        # res.update(self._prepare_purchase_order_line_from_seller(seller))
        # return res

    # @api.model
    # def _prepare_purchase_order_line_from_seller(self, seller):
    #     """
    #     Overload this function to prepare other data from seller
    #     """
    #     if not seller:
    #         return {}
    #     return {"discount": seller.discount}

    def write(self, vals):
        res = super().write(vals)
        if "discount" in vals or "price_unit" in vals:
            for line in self.filtered(lambda l: l.order_id.state == "purchase"):
                # Avoid updating kit components' stock.move
                moves = line.move_ids.filtered(
                    lambda s: s.state not in ("cancel", "done")
                              and s.product_id == line.product_id
                )
                moves.write({"price_unit": line._get_discounted_price_unit()})
        return res
