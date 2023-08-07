# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command
from datetime import datetime
from odoo.exceptions import UserError



class SaleDetails(models.TransientModel):
    _name = 'sale.details'
    _description = 'sale.details'

    user_id = fields.Many2one('res.users', string="User")
    partner_id = fields.Many2one("res.partner", string="Customer", domain="[('is_customer', '=', True)]")
    date = fields.Datetime("Date", default=fields.datetime.now())
    transaction_type = fields.Selection([
        ('sale', 'Sale'),
        ('payment', 'Payment'),
        ('return', 'Return'),
    ], string='Type', ondelete='cascade',
        copy=False, default='', tracking=True, )
    price_list_id = fields.Many2one('product.pricelist', string="Price List")
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')], default='draft')
    sale_order_id = fields.Many2one('sale.order')
    stock_picking_id = fields.Many2one('stock.picking')
    move_id = fields.Many2one('account.move')
    line_ids = fields.One2many('sale.details.line', 'sale_detail_id', string="Lines")

    def action_open_sale(self):
        result = {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "domain": [('id', '=', self.sale_order_id.id)],
            "context": {"create": False},
            "name": "Sale Order",
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
        }
        return result

    def action_open_invoice(self):
        result = {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "domain": [('id', '=', self.move_id.id)],
            "context": {"create": False},
            "name": "Invoice",
            'view_mode': 'form',
            'res_id': self.move_id.id,
        }
        return result

    def action_open_picking(self):
        result = {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "domain": [('id', '=', self.stock_picking_id.id)],
            "context": {"create": False},
            "name": "Stock Picking",
            'view_mode': 'form',
            'res_id': self.stock_picking_id.id,
        }
        return result

    def action_print_sale_order_report(self):
        for order in self:
            return self.env.ref('sale.action_report_saleorder').report_action(order.sale_order_id.id)

    def action_print_picking(self):
        for order in self:
            return self.env.ref('stock.action_report_delivery').report_action(order.stock_picking_id.id)

    def action_print_invoice_ticket(self):
        for order in self:
            return

    @api.onchange('user_id','transaction_type')
    def _get_user_warehouse(self):
        for this in self:
            if this.user_id.stock_warehouse_ids:
                this.warehouse_id = this.user_id.stock_warehouse_ids[0].id
            else:
                this.warehouse_id = False

    @api.onchange('partner_id')
    def get_partner_pricelist(self):
        for sale in self:
            if sale.partner_id:
                sale.price_list_id = sale.partner_id.property_product_pricelist.id if sale.partner_id.property_product_pricelist else False

    def open_barcode_scanner(self):
        for this in self:
            action = {
                'name': _("Product Scanner"),
                'type': 'ir.actions.client',
                'tag': 'smartest_sale_details_main_menu',
                'context': {
                           'model'  : 'sale.details',
                           'res_id' : this.id,
                           'data' : {
                                'default_user_id': this.user_id.id,
                                'default_partner_id': this.partner_id.id,
                                'default_date': this.date,
                                'default_transaction_type': this.transaction_type,
                           },
                           },
                'target': 'fullscreen',
            }
            return action

    def action_register_sale_order(self):
        for order in self:
            order.transaction_type = 'sale'
            return order.action_reload_wizard(order)

    def action_register_payment(self):
        for payment in self:
            payment.transaction_type = 'payment'
            action = {
                'name': _("Register Payment"),
                'type': 'ir.actions.act_window',
                'res_model': 'account.payment',
                'view_mode': 'form',
                'context': {
                           'default_partner_id'  : payment.partner_id.id,
                           'default_date'  : payment.date,
                           'default_journal_id'  : False,

                           },
                'target': 'new',
            }

            return action

    def action_register_return(self):
        for order in self:
            order.transaction_type = 'return'
            return order.action_reload_wizard(order)

    def action_reload_wizard(self,this):
        action = {
            'name': _("Sale Details"),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.details',
            'view_mode': 'form',
            'context': {
                'default_user_id': this.user_id.id,
                'default_partner_id': this.partner_id.id,
                'default_date': this.date,
                'default_transaction_type': this.transaction_type,
                'default_warehouse_id': this.warehouse_id.id,
            },
            'target': 'new',
        }

        return action

    def create_sale_order(self):
        for order in self:
            order_lines = []
            for line in order.line_ids:
                order_lines.append((0,0,{
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_id.uom_id.id,
                    'price_unit': line.unit_price,
                    'tax_id': False,
                }))
            order.sale_order_id = self.env['sale.order'].create({
                'partner_id' : order.partner_id.id,
                'date_order' : order.date,
                'pricelist_id' : order.price_list_id.id,
                'warehouse_id': order.warehouse_id.id,
                'order_line': order_lines,
            })
            order.sale_order_id.action_confirm()
            pick = order.sale_order_id.picking_ids.filtered(lambda self: self.state not in ['done','cancel'])
            for index, line in enumerate(order.line_ids) :
                pick.move_ids_without_package[index].move_line_ids.lot_id = line.lot_id.id
                pick.move_ids_without_package[index].move_line_ids.product_uom_qty = line.quantity
                pick.move_ids_without_package[index].move_line_ids.qty_done = line.quantity
                pick.move_ids_without_package[index].move_line_ids.location_id = line.location_id.id
            order.sale_order_id.picking_ids.filtered(lambda self: self.state not in ['done', 'cancel']).button_validate()
            order.stock_picking_id = order.sale_order_id.picking_ids[0]
            order.move_id = order.sale_order_id._create_invoices()
            order.move_id.action_post()

    def create_bl_return(self):
        for order in self:
            order_lines = []
            picking_type = self.env['stock.picking.type'].search([('warehouse_id','=',order.warehouse_id.id),('code','=','incoming'),('return_picking_type_id','=',False)])
            for line in order.line_ids:
                order_lines.append((0,0,{
                    'product_id': line.product_id.id,
                    'qty_done': line.quantity,
                    'product_uom_id': line.product_id.uom_id.id,
                    'lot_id': line.lot_id.id,
                    'location_dest_id': picking_type[0].default_location_dest_id.id if picking_type else False,
                    'location_id': self.env.ref('stock.stock_location_customers').id,
                }))
            order.stock_picking_id = self.env['stock.picking'].create({
                'partner_id' : order.partner_id.id,
                'scheduled_date' : order.date,
                'location_id': self.env.ref('stock.stock_location_customers').id,
                'location_dest_id': picking_type[0].default_location_dest_id.id if picking_type else False,
                'picking_type_id' : picking_type[0].id if picking_type else False,
                'move_line_ids_without_package': order_lines,
            })
            order.stock_picking_id.action_confirm()
            order.stock_picking_id.button_validate()

    def create_out_refund_invoice(self):
        for order in self:
            order_lines = []
            for line in order.line_ids:
                order_lines.append((0, 0, {
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'product_uom_id': line.product_id.uom_id.id,
                    # 'price_unit': line.unit_price,
                    'account_id': line.product_id.categ_id.property_account_income_categ_id.id,
                    'tax_ids': False,
                }))
            move = self.env['account.move'].with_context(check_move_validity=False).create({
                'partner_id': order.partner_id.id,
                'invoice_date': order.date,
                'move_type': 'out_refund',
                'journal_id': self.env['account.journal'].search([('type','=','sale')],limit=1).id,
                'invoice_line_ids': order_lines,
            })
            for index, line in enumerate(order.line_ids) :
                move.filtered(lambda self: self.state not in ['posted','cancel']).invoice_line_ids[index].price_unit = line.unit_price
            move.with_context(check_move_validity=False)._move_autocomplete_invoice_lines_values()
            move._recompute_payment_terms_lines()

    def action_make_done(self):
        for this in self:
            this.check_product_tracking()
            if this.transaction_type == 'payment':
                return
            elif this.transaction_type == 'sale':
                this.create_sale_order()
            elif this.transaction_type == 'return':
                this.create_out_refund_invoice()
                this.create_bl_return()
            this.state = 'done'
            action = {
                    'name': _("Sale Details"),
                    'type': 'ir.actions.act_window',
                    'res_model': 'sale.details',
                    'view_mode': 'form',
                    'context': {
                        'edit': False,
                        'default_user_id': this.user_id.id,
                        'default_partner_id': this.partner_id.id,
                        'default_date': this.date,
                        'default_sale_order_id': this.sale_order_id.id,
                        'default_stock_picking_id': this.stock_picking_id.id,
                        'default_move_id': this.move_id.id,
                        'default_transaction_type': this.transaction_type,
                        'default_warehouse_id': this.warehouse_id.id,
                        'default_state': this.state,
                        'default_line_ids': this.line_ids.ids,
                    },
                    'target': 'current',
                }

            return action

    def check_product_tracking(self):
        for line in self.line_ids :
            if line.product_id.tracking != 'none' and not line.lot_id and line.sale_detail_id.transaction_type == 'sale':
                raise UserError(
                    _(f'The product {line.product_id.name} is tracked by {line.product_id.tracking}, Please choose a {line.product_id.tracking}'))


class SaleDetailsLine(models.TransientModel):
    _name = 'sale.details.line'
    _description = 'sale.details.line'

    product_id = fields.Many2one('product.product', domain="[('sale_ok', '=', True)]", required=True)
    lot_id = fields.Many2one('stock.production.lot')
    sale_detail_id = fields.Many2one('sale.details', string="Sale Detail")
    unit_price = fields.Monetary(string="Price Unit", currency_field='company_currency_id')
    quantity = fields.Integer(string="Quantity", default="1")
    company_currency_id = fields.Many2one(string='Company Currency', readonly=True,
                                          related='company_id.currency_id')
    location_id = fields.Many2one('stock.location')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.onchange('lot_id','quantity')
    def compute_location_id(self):
        for this in self:
            if this.lot_id and this.sale_detail_id.transaction_type == 'sale':
                locations = this.lot_id.quant_ids.filtered(lambda x: x.location_id.warehouse_id == this.sale_detail_id.warehouse_id and x.location_id.usage == 'internal')
                if not locations:
                    raise UserError(_(f'There is no avaiable quantity in {this.sale_detail_id.warehouse_id.name} for product {this.product_id.name} lot {this.lot_id.name}'))
                this.location_id = locations[0].location_id.id

    @api.onchange('product_id','quantity')
    def compute_unit_price(self):
        for line in self:
            if line.product_id:
                line.unit_price = False
                for price in line.sale_detail_id.price_list_id.item_ids.filtered(lambda self: self.product_id == line.product_id) :
                    line.unit_price = price.fixed_price
                    break

    @api.onchange('product_id')
    def compute_lot_id_domain(self):
        for this in self:
            if this.product_id :
                if this.sale_detail_id.transaction_type == 'sale':
                    lot_ids = self.env['stock.quant'].search(
                        [('product_id','=',this.product_id.id),('on_hand','=',True),('quantity','>',0),('location_id.usage','=','internal')]
                    ).filtered(lambda x: x.location_id.warehouse_id == this.sale_detail_id.warehouse_id).mapped('lot_id')
                elif this.sale_detail_id.transaction_type == 'return':
                    lot_ids = self.env['stock.production.lot'].search(
                        [('product_id','=',this.product_id.id)]
                    )
                return {
                    'domain': {
                        'lot_id': [('id', 'in', lot_ids.mapped('id'))]
                    }
                }

    @api.model
    def create_lines_from_front(self,data):
        barcode = data.get('barcode')
        res_id = data.get('res_id')
        serial_number_id = self.env['stock.production.lot'].search([('name','=',barcode),('product_id.sale_ok','=',True)], limit=1)
        sale_details_line = self.env['sale.details'].search([('id','=',res_id)], limit=1).line_ids
        if serial_number_id:
            if sale_details_line:
                for this in sale_details_line :
                    if serial_number_id == this.lot_id and serial_number_id.product_id == this.product_id:
                        this.quantity += 1
                    else:
                        self.create_sale_details_line(serial_number_id,res_id)
            else:
                self.create_sale_details_line(serial_number_id, res_id)
            return True
        else :
            return False,"No Serial found, Please rescan"

    def create_sale_details_line(self,serial_number_id,res_id):
        line = self.env['sale.details.line']
        rec = line.create({
            'lot_id': serial_number_id.id,
            'product_id': serial_number_id.product_id.id,
            'sale_detail_id': res_id,
        })
        rec.compute_unit_price()
        rec.compute_location_id()
