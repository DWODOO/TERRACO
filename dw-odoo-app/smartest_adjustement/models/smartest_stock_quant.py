# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json


class SmartestInventoryAjustments(models.Model):
    _name = 'smartest.inventory'

    name = fields.Char(
        'Name'
    )

    form_id = fields.Integer(
        'form_id'
    )

    date = fields.Date(
        string='Counting Date'
    )

    warehouse_name = fields.Many2one('stock.warehouse', string='Warehouse', required=True)

    inventory_line_ids = fields.One2many('smartest.inventory.line', 'inventory_id', string='Lines')

    statut = fields.Selection([
        ('Start', 'Start Inventory'),
        ('First', 'First Count'),
        ('Second', 'Second Count'),
        ('Chek', 'Chek Count'),
        ('Third', 'Third Count'),
        ('End', 'End Count'),
    ], string="Status", default="Start")
    barcode_adjustment = fields.Boolean(string="Barcode")

    """_sql_constraints Ensures that the inventory adjustment name is unique"""
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Name already exists !"),
        ]

    """
    check if the barcode scanned is a real location or product  
    """
    @api.model
    def check_barcode_scanned(self, val_list):
        serial_number = val_list['serial_number']
        location_barcode = self.env['stock.location'].search([('barcode', '=', serial_number)])
        product_barcode = self.env['product.template'].search([('barcode', '=', serial_number)])
        if location_barcode:
            xx = ['location', location_barcode.display_name]
            return xx
        if product_barcode:
            xx = ['product', product_barcode.name]
            return xx

            # for rec in location_barcode:
            # if serial_number in
    """
    the create_line methode create or update a line in the inventory adjustment based on the barcodes scanned
    """
    @api.model
    def create_line(self, val_list):
        inventory = val_list['inventory_id']
        location = val_list['location_id']
        product = val_list['product_id']
        count = val_list['count_id']
        add_line = self.env['smartest.inventory'].search([('name', '=', inventory)])
        locatx = self.env['stock.location'].search([('complete_name', '=', location)])
        prodx = self.env['product.product'].search([('name', 'like', product)])


        for rec in add_line.inventory_line_ids:
            if locatx == rec.location and prodx == rec.product_id:
                if add_line.statut == 'First':
                    rec.write({'first_count': rec.first_count+float(count)})
                elif add_line.statut == 'Second':
                    rec.write({'second_count': rec.second_count + float(count)})
                elif add_line.statut == 'Third':
                    rec.write({'third_count': rec.third_count + float(count)})


        if add_line.statut == 'First':
            if locatx not in add_line.inventory_line_ids.location or prodx not in add_line.inventory_line_ids.product_id:
                self.env['smartest.inventory.line'].create({
                    'product_id': prodx.id,
                    'location': locatx.id,
                    'first_count': float(count),
                    'inventory_id': add_line.id,
                })

    @api.model
    def get_the_count_number(self, val_list):
        inventory_name = val_list['inventory_id']
        x_name = self.env['smartest.inventory'].search([('name', '=', inventory_name)])

        if x_name.statut == 'First':
            return "You Are In The First Count Please Choose Scan Method"
        elif x_name.statut == 'Second':
            return "You Are In The Second Count Please Choose Scan Method"
        elif x_name.statut == 'Third':
            return "You Are In The Third Count Please Choose Scan Method"
        elif x_name.statut == 'Chek':
            return "You Are In The check Point"
        elif x_name.statut == 'End':
            return "The Counting Is Over Please Choose Another Inventory"

    """
    the inventory_name methode allow us to get all the inventorys adjustment name
    """
    @api.model
    def inventory_name(self):
        values = {}
        json_data = {}
        test = self.env['smartest.inventory'].search([('barcode_adjustment', '=', 'True')])
        for p in test:
            value = {}
            # for op in test.inventory_line_ids:
            value[p.name] = p.mapped("warehouse_name.name")
            json_d = json.dumps(value)
            values[p.name] = json_d
            json_data = json.dumps(values)

        if json_data:
            return str(json_data)
        else:
            return

    """
    create_inventory allow us to get all the product in the warehouse selected
    """
    def create_inventory(self):
        if self.barcode_adjustment == False:
            self.statut = 'First'
            test = self.env['stock.picking'].search([('name', 'like', self.warehouse_name.code)])
            for i in range(len(test)):
                if (test[i].name[0:2] == self.warehouse_name.code or test[i].name[0:3] == self.warehouse_name.code or
                    test[i].name[0:4] == self.warehouse_name.code) \
                        and test[i].product_id.detailed_type == 'product':
                    for j in range(len(test[i].move_ids_without_package)):

                        for xx in self:
                            self.env['interm.inv.line'].create({
                                'product_id': test[i].move_ids_without_package[j].product_id.id,
                                'location': test[i].move_ids_without_package[j].location_dest_id.id,
                                'just_id': xx.id,
                            })

            self.env.cr.execute(
                "DELETE FROM interm_inv_line x USING interm_inv_line y  WHERE x.id < y.id AND x.product_id = y.product_id and x.location=y.location "
            )
            test = self.env['interm.inv.line'].search([])
            for rec in test:
                for tec in self:
                    self.env['smartest.inventory.line'].create({
                        'product_id': rec.product_id,
                        'location': rec.location,
                        'inventory_id': tec.id,
                    })
                    self.env.cr.commit()
            self.env.cr.execute(
                "delete from interm_inv_line"
            )
        else:
            self.statut = 'First'


    """
    check_count check if the first count and the second count are eqal or not and change the status based and the result
    """
    def chek_count(self):
        chek = 0
        for rec in self.inventory_line_ids:
            rec.difference_qty = abs(rec.first_count - rec.second_count)
            if rec.first_count != rec.second_count:
                self.statut = 'Third'
                rec.deff = True
                chek = 1

        if chek == 0:
            self.statut = 'End'

    """
    open the first counting sheet
    """
    def create_first_counting(self):
        return {
            'name': ('First Counting'),
            'res_model': 'smartest.inventory',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('smartest_adjustement.feuille_comptage_1').id,
            'res_id': self.id,
            # 'context': self.env.context,
            # 'views': [(False, 'form')],
            'terget': 'self'
        }

    """
    open the second counting sheet
    """
    def create_second_counting(self):
        return {
            'name': ('Second Counting'),
            'res_model': 'smartest.inventory',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('smartest_adjustement.feuille_comptage_2').id,
            'res_id': self.id,
            # 'context': self.env.context,
            # 'views': [(False, 'form')],
            'terget': 'self'
        }

    """
    open the third counting sheet
    """
    def create_third_counting(self):
        return {
            'name': ('Third Counting'),
            'res_model': 'smartest.inventory',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('smartest_adjustement.feuille_comptage_3').id,
            'res_id': self.id,
            # 'context': self.env.context,
            # 'views': [(False, 'form')],
            'terget': 'self'
        }

    """
    validate the first count    
    """
    def validate_first_count(self):
        # self.statut = 'Second'
        return {
            'res_model': 'smartest.inventory',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'tree',
            'view_id': self.env.ref('smartest_adjustement.stock_quant_form').id,
            'res_id': self.id,
            # 'context':  ctx,
            'tag': 'current',
            'target': 'self',
        }

    """
    validate the second count
    """
    def validate_second_count(self):
        # self.statut = 'Chek'
        return {
            'res_model': 'smartest.inventory',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'tree',
            'view_id': self.env.ref('smartest_adjustement.stock_quant_form').id,
            'res_id': self.id,
            # 'context':  ctx,
            'tag': 'current',
            'target': 'self',
        }


    """
    validate the third count
    """
    def validate_third_count(self):
        # self.statut = 'End'
        return {
            'res_model': 'smartest.inventory',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'tree',
            'view_id': self.env.ref('smartest_adjustement.stock_quant_form').id,
            'res_id': self.id,
            # 'context':  ctx,
            'tag': 'current',
            'target': 'self',
        }

    """
    end the third count and change the status to Second
    """
    def done_first_count(self):
        self.statut = 'Second'
        return {
            'res_model': 'smartest.inventory',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'tree',
            'view_id': self.env.ref('smartest_adjustement.stock_quant_form').id,
            'res_id': self.id,
            # 'context':  ctx,
            'tag': 'current',
            'target': 'self',
        }


    """
    end the second count and change tha status to Chek
    """
    def done_second_count(self):
        self.statut = 'Chek'
        return {
            'res_model': 'smartest.inventory',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'tree',
            'view_id': self.env.ref('smartest_adjustement.stock_quant_form').id,
            'res_id': self.id,
            # 'context':  ctx,
            'tag': 'current',
            'target': 'self',
        }


    """
    end the third count and change the status to End
    """
    def done_third_count(self):
        self.statut = 'End'
        return {
            'res_model': 'smartest.inventory',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'tree',
            'view_id': self.env.ref('smartest_adjustement.stock_quant_form').id,
            'res_id': self.id,
            # 'context':  ctx,
            'tag': 'current',
            'target': 'self',
        }

    """
    end the counting and add the result to the stoq.quant 
    """
    def end_counting(self):
        inv_line = self.inventory_line_ids
        st_quant = self.env['stock.quant'].search([])
        print(st_quant.product_id)
        for rec in inv_line:
            product_location = self.env['stock.quant'].search([('product_id', '=', rec.product_id.id)])
            print(product_location)
            for toto in st_quant:
                if toto.location_id == rec.location and rec.product_id == toto.product_id:
                    record_to_update = self.env['stock.quant'].browse(toto.id)
                    if record_to_update.exists():
                        if rec.difference_qty != 0:
                            record_to_update.write({'inventory_quantity': rec.third_count})
                        else:
                            record_to_update.write({'inventory_quantity': rec.first_count})

            if (rec.product_id not in st_quant.product_id):
                if rec.difference_qty != 0:
                    self.env['stock.quant'].create({
                        'location_id': rec.location.id,
                        'product_id': rec.product_id.id,
                        'quantity': rec.third_count,
                        'inventory_quantity': rec.third_count,
                    })

                elif rec.difference_qty == 0:
                    self.env['stock.quant'].create({
                        'location_id': rec.location.id,
                        'product_id': rec.product_id.id,
                        'quantity': rec.first_count,
                        'inventory_quantity': rec.first_count,
                    })


            elif rec.location not in product_location.location_id:
                if rec.difference_qty != 0:
                    self.env['stock.quant'].create({
                        'location_id': rec.location.id,
                        'product_id': rec.product_id.id,
                        'quantity': rec.third_count,
                        'inventory_quantity': rec.third_count,
                    })
                else:
                    self.env['stock.quant'].create({
                        'location_id': rec.location.id,
                        'product_id': rec.product_id.id,
                        'quantity': rec.first_count,
                        'inventory_quantity': rec.first_count,
                    })

        return {
            'name': 'Inventory Adjustments',
            'res_model': 'stock.quant',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'list',
            'view_id': self.env.ref('stock.view_stock_quant_tree_inventory_editable').id,
            # 'context': self.env.context,
            # 'views': [(False, 'form')],
            'terget': 'self',

        }
