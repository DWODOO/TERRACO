# -*- coding: utf-8 -*-
import pdb

from odoo import api, Command, models, fields, tools, _


class PriceListCoefficient(models.Model):
    _name = 'pricelist.coefficient'

    price_list_id = fields.Many2one(
        'product.pricelist',
    )
    coefficient = fields.Float(
        'Coefficient',
    )
    paricelist_margin_id = fields.Many2one(
        'pricelist.margin'
    )
    add_articles = fields.Boolean(
        'New Article',
        help="By checking this, we can add a product from the selection below that doesn't exist in the price list"
    )


class PriceListMargin(models.Model):
    _name = 'pricelist.margin'

    name = fields.Char(
        'Reception'
    )
    pricelist_coefficient_ids = fields.One2many(
        'pricelist.coefficient',
        'paricelist_margin_id',
        states={'done': [('readonly', True)]},
    )
    picking_ids = fields.Selection(
        selection=lambda self: self.dynamic_selection(),
    )
    pricelist_margin_line_ids = fields.One2many(
        'pricelist.margin.line',
        'product_line_id',
        string='Lines',
        states={'done': [('readonly', True)]},
    )
    state = fields.Selection([
        ('draft', 'draft'),
        ('confirmed', 'Confirmed'),
        ('validation', 'Validation'),
        ('done', 'done'),
    ],
        string="State",
        default="draft"
    )
    use_highest_cost = fields.Boolean(
        'Highest All',
        help="Compute based on the highest cost for all lines"
    )
    landed_cost = fields.Boolean(
        'Consider Landed Costs',
    )
    operation_type = fields.Selection([
        ('reception', 'By Reception'),
        ('product', 'By Products'),
        ('category', 'By Category')
    ],
        'Operation Type',
        required=True,
    )
    product_category_ids = fields.Many2many(
        'product.category',
        'product_category_pricelist_margin_rel',
        'category_id',
        'margin_id',
        'Categories'
    )
    use_product_sale_price = fields.Boolean()

    def dynamic_selection(self):
        result = self.env['stock.picking'].search([('picking_type_code', '=', 'incoming'), ('state', '=', 'done')],
                                                  order="id desc")
        select = []
        for rec in result:
            select = select + [(rec['name'], rec['name'])]
        return select

    def get_landed_costs(self, move, rec):
        cost_without_landed = self.env['stock.valuation.layer'].search(
            [('product_id', '=', move.product_id.id),
             ('stock_landed_cost_id', '=', False),
             ('stock_move_id.picking_id.name', '=', rec.picking_ids)],
            limit=1
        )

        # for multiple_product in product_valuation_layer:
        cost_with_landed = self.env['stock.valuation.layer'].search(
            [('product_id', '=', move.product_id.id),
             ('stock_landed_cost_id', '!=', False),
             ('stock_valuation_layer_id', '=', cost_without_landed.id),
             ('stock_move_id.picking_id.name', '=', rec.picking_ids)]
        )

        summing = cost_without_landed.value

        for landed in cost_with_landed:
            summing = summing + landed.value

        return summing / cost_without_landed.quantity

    def get_all_product(self):
        """
        This function will capture the stock reception, then get all its lines in order to pass throw each one and
        extract its costs, by considering whether there is or not landed costs applied to it.
        :return:
        """
        for rec in self:
            name = "Prices calculation for "
            values = []

            if rec.operation_type == 'reception':
                lines = rec.env['stock.picking'].search([('name', '=', rec.picking_ids)]).move_ids_without_package
                name = name + "Reception (" + rec.picking_ids + ")"
            elif rec.operation_type == 'category':
                templates = rec.env['product.template'].search([('categ_id', 'in', rec.product_category_ids.ids)])
                lines = rec.env['product.product'].search([('product_tmpl_id', 'in', templates.ids)])
                name = name + "by Category"
            else:
                templates = rec.env['product.template'].search([('sale_ok', '=', True)])
                lines = rec.env['product.product'].search([('product_tmpl_id', 'in', templates.ids)])
                name = name + "by Products"

            for line in lines:

                # If import purchase then considering landed costs
                if rec.landed_cost:
                    with_landed_costs = rec.get_landed_costs(line, rec)
                else:
                    with_landed_costs = 0

                if rec.operation_type == 'reception':
                    val = {
                        'product_id': line.product_id.id,
                        'purchase_price': line.product_id.standard_price,
                        'last_cost': line.product_id.product_tmpl_id.smartest_product_last_cost if not rec.landed_cost
                        else with_landed_costs,
                        'product_line_id': rec.id,
                        'use_product_sale_price': rec.use_product_sale_price,
                        'use_highest_cost': rec.use_highest_cost,
                        'highest_cost': line.product_id.product_tmpl_id.highest_cost if not rec.landed_cost and
                        line.product_id.product_tmpl_id.highest_cost > with_landed_costs else with_landed_costs
                    }
                else:
                    val = {
                        'product_id': line.id,
                        'purchase_price': line.product_tmpl_id.standard_price,
                        'last_cost': line.product_tmpl_id.smartest_product_last_cost if not rec.landed_cost
                        else with_landed_costs,
                        'highest_cost': line.product_tmpl_id.highest_cost if not rec.landed_cost and line.
                        product_tmpl_id.highest_cost > with_landed_costs else with_landed_costs,
                        'product_line_id': rec.id,
                        'use_product_sale_price': rec.use_product_sale_price,
                        'use_highest_cost': rec.use_highest_cost,
                    }
                for pricelist_coefficient_id in rec.pricelist_coefficient_ids:
                    val.update({
                        'add_articles': pricelist_coefficient_id.add_articles,
                        'pricelist_coefficient_id': pricelist_coefficient_id.id,
                        'coefficient': pricelist_coefficient_id.coefficient,
                    })

                values.append(Command.create(val))

            rec.write({
                'state': 'confirmed',
                'pricelist_margin_line_ids': values,
                'name': name,
            })

    def calculate_new_price(self):
        """
        This function will calculate the price based on the declared costs to be used
        :return:
        """
        self.state = 'validation'
        self.pricelist_margin_line_ids.state = 'validation'
        for rec in self.pricelist_margin_line_ids:
            if rec.use_highest_cost:
                rec.product_new_price = rec.highest_cost + (rec.highest_cost * rec.coefficient)
            else:
                rec.product_new_price = rec.last_cost + (rec.last_cost * rec.coefficient)

    @api.onchange('pricelist_margin_line_ids')
    def onchange_coefficient(self):
        """
        This function will edit the new price base on the changes made on the costs
        :return:
        """
        if self.state == 'validation':
            for rec in self.pricelist_margin_line_ids:
                if rec.use_highest_cost:
                    rec.product_new_price = rec.highest_cost + (
                                rec.highest_cost * rec.pricelist_coefficient_id.coefficient)
                else:
                    rec.product_new_price = rec.last_cost + (rec.last_cost * rec.pricelist_coefficient_id.coefficient)

    def validate_new_price(self):
        """
        This function will post the calculated amounts to the selected price lists by either creating the product,
         if doesn't exist in it or updating it
        :return:
        """
        self.state = 'done'
        self.pricelist_margin_line_ids.state = 'done'
        for rec in self.pricelist_margin_line_ids:
            if not rec.use_product_sale_price:
                items = self.env['product.pricelist.item'].search(
                    [('product_tmpl_id', '=', rec.product_id.product_tmpl_id.id)])
                price_list = self.env['product.pricelist'].search([])

                if not items and rec.add_articles:
                    for pricelist in price_list:
                        if pricelist == rec.pricelist_coefficient_id.price_list_id:
                            items.create({
                                'applied_on': '1_product',
                                'pricelist_id': pricelist.id,
                                'product_id': rec.product_id.id,
                                'product_tmpl_id': rec.product_id.product_tmpl_id.id,
                                'fixed_price': rec.product_new_price,
                            })
                else:
                    for item in items:
                        if item.pricelist_id == rec.pricelist_coefficient_id.price_list_id:
                            item.fixed_price = rec.product_new_price
            else:
                rec.product_id.product_tmpl_id.list_price = rec.product_new_price

    @api.model
    def create(self, vals):
        if not vals.get('name') == _('New'):
            vals['name'] = self.env["ir.sequence"].next_by_code("pricelist.margin") or _('/')
        request = super(PriceListMargin, self).create(vals)
        return request
