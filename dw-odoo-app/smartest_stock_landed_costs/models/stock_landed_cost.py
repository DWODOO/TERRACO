# -*- coding: utf-8 -*-

# Import Odoo libs
from collections import defaultdict

from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero

from odoo import api, fields, models, tools, _
from . import SPLIT_METHOD


class SmartestStockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    smartest_product_ids = fields.Many2many(
        'product.product',
        string='Products',
        states={'done': [('readonly', True)]},
    )
    vendor_bill_id = fields.Many2one(
        'account.move',
        states={'done': [('readonly', True)]},
    )
    smartest_new_devise_rate = fields.Float(
        'Currency Rate', digits=(8, 4),
        states={'done': [('readonly', True)]},
    )
    split_method = fields.Selection(
        SPLIT_METHOD
    )

    @api.onchange('picking_ids')
    def _onchange_picking_ids(self):
        # Get all move lines from Pickings
        products = self.mapped('picking_ids.move_ids.product_id').ids

        # Remove all content then append new values
        self.smartest_product_ids = [(5, 0)] + [(4, p) for p in products]

        return {
            'domain': {
                'smartest_product_ids': [('id', 'in', products)]
            }
        }

    def get_valuation_lines(self):
        # Initialize variables
        lines = []
        all_move_lines = self.mapped('picking_ids').mapped('move_ids')
        moves = all_move_lines.filtered(lambda m: m.product_id in self.mapped('smartest_product_ids'))

        for move in moves:
            # it doesn't make sense to make a landed cost for a product that isn't set as being valuated in real time at real cost
            if move.product_id.valuation != 'real_time' or move.product_id.cost_method not in (
                    'fifo', 'average') or move.state == 'cancel':
                continue

            # Build valuation line values
            vals = {
                'product_id': move.product_id.id,
                'move_id': move.id,
                'quantity': move.product_qty,
                'former_cost': sum(move.stock_valuation_layer_ids.mapped('value')),
                'weight': move.product_id.weight * move.product_qty,
                'volume': move.product_id.volume * move.product_qty
            }

            # Append values
            lines.append(vals)

        # Raise error if no automated valuation method is used
        if not lines and self.mapped('picking_ids'):
            raise UserError(_(
                "You cannot apply landed costs on the chosen transfer(s). Landed costs can only be applied for "
                "products with automated inventory valuation and FIFO or average costing method."
            ))

        # Return lines (values)
        return lines

    def compute_landed_cost(self):
        # Initialize variables
        AdjustementLines = self.env['stock.valuation.adjustment.lines']
        total_hs_percentage = 0.0
        digits = self.env['decimal.precision'].precision_get('Product Price')
        towrite_dict = {}

        # Unlink Old lines
        AdjustementLines.search([('cost_id', 'in', self.ids)]).unlink()

        for cost in self.filtered(lambda cost: cost._get_targeted_move_ids()):
            total_qty = 0.0
            total_cost = 0.0
            total_weight = 0.0
            total_volume = 0.0
            total_line = 0.0
            all_val_line_values = cost.get_valuation_lines()
            for val_line_values in all_val_line_values:
                for cost_line in cost.cost_lines:
                    val_line_values.update({'cost_id': cost.id, 'cost_line_id': cost_line.id})
                    self.env['stock.valuation.adjustment.lines'].create(val_line_values)
                total_qty += val_line_values.get('quantity', 0.0)
                total_weight += val_line_values.get('weight', 0.0)
                total_volume += val_line_values.get('volume', 0.0)
                former_cost = val_line_values.get('former_cost', 0.0)
                # round this because former_cost on the valuation lines is also rounded
                total_cost += tools.float_round(former_cost, precision_digits=digits) if digits else former_cost

                total_line += 1
            # n = 0
            p = 0
            for val in self.smartest_product_ids:
                total_hs_percentage += val.hs_code_id.percentage
            for line in cost.cost_lines:
                value_split = 0.0
                lenth = len(cost.valuation_adjustment_lines)
                for valuation in cost.valuation_adjustment_lines:
                    value = 0.0
                    if valuation.cost_line_id and valuation.cost_line_id.id == line.id:
                        if line.split_method == 'by_quantity' and total_qty:
                            per_unit = (line.price_unit / total_qty)
                            value = valuation.quantity * per_unit
                        elif line.split_method == 'by_weight' and total_weight:
                            per_unit = (line.price_unit / total_weight)
                            value = valuation.weight * per_unit
                        elif line.split_method == 'by_volume' and total_volume:
                            per_unit = (line.price_unit / total_volume)
                            value = valuation.volume * per_unit
                        elif line.split_method == 'equal':
                            value = (line.price_unit / total_line)
                        elif line.split_method == 'by_current_cost_price' and total_cost:
                            per_unit = (line.price_unit / total_cost)
                            value = valuation.former_cost * per_unit
                            value = round(value, digits + 1)
                        elif line.split_method == 'hs_code':
                            valuation_layers = self.mapped(
                                'picking_ids.move_ids_without_package.stock_valuation_layer_ids'
                            )
                            r = valuation_layers.filtered(
                                lambda x: x.stock_move_id == valuation.move_id and x.product_id == valuation.product_id
                                          and not x.stock_landed_cost_id
                            )
                            if len(r) > 0:
                                r = r[-1]

                            if self.smartest_new_devise_rate != 0.0:
                                po_id = r.stock_move_id.purchase_line_id.order_id
                                purchase_value = r.stock_move_id.purchase_line_id.price_subtotal
                                old_exchange_rate = po_id.currency_rate_import_purchase
                                if r.product_id.hs_code_id:
                                    hs_code_rate = r.product_id.hs_code_rate / 100
                                else:
                                    hs_code_rate = r.product_id.categ_id.hs_code_rate / 100

                                value = purchase_value * self.smartest_new_devise_rate * hs_code_rate

                            else:
                                if r.product_id.hs_code_id:
                                    value = r.value * r.product_id.hs_code_id.percentage / 100
                                else:
                                    value = r.value * r.product_id.categ_id.hs_code_rate / 100
                        else:
                            value = (line.price_unit / total_line)

                        if digits:
                            value = tools.float_round(value, precision_digits=digits)
                            if line.split_method != 'hs_code':
                                fnc = min if line.price_unit > 0 else max
                                value = fnc(value, line.price_unit - value_split)
                            value_split += value

                        if valuation.id not in towrite_dict:
                            towrite_dict[valuation.id] = value
                        else:
                            towrite_dict[valuation.id] += value
        for key, value in towrite_dict.items():
            AdjustementLines.browse(key).write({'additional_landed_cost': value})
        return True

    # didn't find a way to inherit the function without overwriting it all

    def _check_sum(self):
        if any(line.split_method == 'hs_code' for line in self.mapped('cost_lines')):
            return True
        return super(SmartestStockLandedCost, self)._check_sum()

    def cancel_and_reset(self):
        # for rec in self:
        #     valuation_layer = self.env['stock.valuation.layer'].search([('stock_landed_cost_id','=',self.id)]).sudo().unlink()
        #     rec.state = 'draft'

        cost_without_adjusment_lines = self.filtered(lambda c: not c.valuation_adjustment_lines)
        for cost in self:
            cost = cost.with_company(cost.company_id)
            valuation_layer_ids = []
            cost_to_add_byproduct = defaultdict(lambda: 0.0)
            for line in cost.valuation_adjustment_lines.filtered(lambda line: line.move_id):
                remaining_qty = sum(line.move_id.stock_valuation_layer_ids.mapped('remaining_qty'))
                linked_layer = line.move_id.stock_valuation_layer_ids[:1]

                # Prorate the value at what's still in stock
                if line.move_id.product_qty:
                    cost_to_add = -(remaining_qty / line.move_id.product_qty) * line.additional_landed_cost
                else:
                    cost_to_add = 0
                if not cost.company_id.currency_id.is_zero(cost_to_add):
                    valuation_layer = self.env['stock.valuation.layer'].create({
                        'value': cost_to_add,
                        'unit_cost': 0,
                        'quantity': 0,
                        'remaining_qty': 0,
                        'stock_valuation_layer_id': linked_layer.id,
                        'description': cost.name,
                        'stock_move_id': line.move_id.id,
                        'product_id': line.move_id.product_id.id,
                        'stock_landed_cost_id': cost.id,
                        'company_id': cost.company_id.id,
                    })
                    linked_layer.remaining_value += cost_to_add
                    valuation_layer_ids.append(valuation_layer.id)
                # Update the AVCO
                product = line.move_id.product_id
                if product.cost_method == 'average':
                    cost_to_add_byproduct[product] += cost_to_add
                # `remaining_qty` is negative if the move is out and delivered proudcts that were not
                # in stock.
                qty_out = 0

            # batch standard price computation avoid recompute quantity_svl at each iteration
            products = self.env['product.product'].browse(p.id for p in cost_to_add_byproduct.keys())
            for product in products:  # iterate on recordset to prefetch efficiently quantity_svl
                if not float_is_zero(product.quantity_svl, precision_rounding=product.uom_id.rounding):
                    product.with_company(cost.company_id).sudo().with_context(disable_auto_svl=True).standard_price += \
                        cost_to_add_byproduct[product] / product.quantity_svl

            cost.write({'state': 'draft'})

        return True

    def button_validate(self):
        self._check_can_validate()
        cost_without_adjusment_lines = self.filtered(lambda c: not c.valuation_adjustment_lines)
        if cost_without_adjusment_lines:
            cost_without_adjusment_lines.compute_landed_cost()

        for cost in self:
            cost = cost.with_company(cost.company_id)
            move = self.env['account.move']
            move_vals = {
                'journal_id': cost.account_journal_id.id,
                'date': cost.date,
                'ref': cost.name,
                'line_ids': [],
                'move_type': 'entry',
            }
            valuation_layer_ids = []
            cost_to_add_byproduct = defaultdict(lambda: 0.0)
            for line in cost.valuation_adjustment_lines.filtered(lambda line: line.move_id):
                remaining_qty = sum(line.move_id.stock_valuation_layer_ids.mapped('remaining_qty'))
                linked_layer = line.move_id.stock_valuation_layer_ids[:1]

                # Prorate the value at what's still in stock
                if line.move_id.product_qty:
                    cost_to_add = (remaining_qty / line.move_id.product_qty) * line.additional_landed_cost
                else:
                    cost_to_add = 0
                if not cost.company_id.currency_id.is_zero(cost_to_add):
                    # valuation_layer = self.env['stock.valuation.layer'].create({
                    #     'value': cost_to_add,
                    #     'unit_cost': 0,
                    #     'quantity': 0,
                    #     'remaining_qty': 0,
                    #     'stock_valuation_layer_id': linked_layer.id,
                    #     'description': cost.name,
                    #     'stock_move_id': line.move_id.id,
                    #     'product_id': line.move_id.product_id.id,
                    #     'stock_landed_cost_id': cost.id,
                    #     'company_id': cost.company_id.id,
                    # })
                    linked_layer.remaining_value += cost_to_add
                    # valuation_layer_ids.append(valuation_layer.id)
                # Update the AVCO
                product = line.move_id.product_id
                if product.cost_method == 'average':
                    cost_to_add_byproduct[product] += cost_to_add
                # `remaining_qty` is negative if the move is out and delivered proudcts that were not
                # in stock.
                qty_out = 0
                if line.move_id._is_in():
                    qty_out = line.move_id.product_qty - remaining_qty
                elif line.move_id._is_out():
                    qty_out = line.move_id.product_qty
                move_vals['line_ids'] += line._create_accounting_entries(move, qty_out)
                for rec in self:
                    last_picking = self.env['stock.move'].search(
                        [('product_id', '=', line.move_id.stock_valuation_layer_ids.product_id.id)], limit=1,
                        order="id desc").picking_id
                xx = line.move_id.picking_id
                smartest_picking = line.move_id.picking_id
                if smartest_picking == last_picking:
                    if remaining_qty:
                        new_cost = linked_layer.remaining_value / remaining_qty
                    else:
                        new_cost = 0
                    line.move_id.stock_valuation_layer_ids.product_id.smartest_product_last_cost = new_cost

            return super(SmartestStockLandedCost, self).button_validate()


class SmartestStockLandedCostLines(models.Model):
    _inherit = 'stock.landed.cost.lines'

    split_method = fields.Selection(
        SPLIT_METHOD
    )
