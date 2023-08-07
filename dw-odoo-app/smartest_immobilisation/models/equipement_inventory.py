# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
from odoo.exceptions import UserError


class EquipementInventory(models.Model):
    _name = 'equipement.inventory'

    name = fields.Char(
        'Name'
    )

    date = fields.Date(
        string='Accounting Date'
    )

    asset = fields.Many2one('account.asset')
    product = fields.Many2one('product.product')
    location = fields.Selection(selection=lambda self: self.dynamic_selection())
    equipement_inventory_line_ids = fields.One2many('equipement.inventory.line', 'equipement_inventory_id', string='Lines')

    statut = fields.Selection([
        ('Start', 'Start Inventory'),
        ('Countig', 'Count'),
        ('End', 'End Count'),
    ], string="Status", default="Start")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Name already exists !"),
    ]

    @api.model
    def js_test(self):
        values = {}
        json_data = {}
        test = self.env['equipement.inventory'].search([])
        for p in test:
            value = {}
            # for op in test.equipement_inventory_line_ids:
            value[p.name] = p.mapped("location")
            json_d = json.dumps(value)
            values[p.name] = json_d
            json_data = json.dumps(values)
        # for p in test:
        #     value = {}
        #     for op in test.equipement_inventory_line_ids:
        #         value[op.equipement.display_name] = p.mapped("location")
        #         json_d = json.dumps(value)
        #     values[p.name] = json_d
        #     json_data = json.dumps(values)
        # print("hhheeelllooo", str(json_data))
        # print("hhheeelllooo", test.equipement_inventory_line_ids.equipement[1].serial_no)

        if json_data:
            return str(json_data)
        else:
            return

    @api.model
    def action_create_record(self, val_list):
        print("inside action_create_record")
        serial_number = val_list['serial_number']
        print("hiiii",serial_number)

        po_name = val_list['production_id']
    #     po_operation = val_list['operation_id']
    #     operation_workcenter = val_list['workcenter']
        # mrp_workorder_id = self.env['mrp.workorder'].search(
        #     [('production_id.name', '=', po_name), ('name', '=', po_operation),
        #      ('workcenter_id.name', '=', operation_workcenter)])
        serial = self.env['equipement.inventory'].search([('name', '=', po_name)])
        print("serial number is :",serial_number)
        x_return = 'false'
        for rec in serial.equipement_inventory_line_ids:
            print("hiiii",len(serial.equipement_inventory_line_ids))
            if rec.equipement.serial_no == serial_number:
                record_to_update = self.env['equipement.inventory.line'].browse(rec.id)
                print("rec.equipement.serial_no",rec.equipement.serial_no)
                if serial.statut == 'Countig':
                    record_to_update.write({'first_count': 1})
                    x_return = 'true'
        return x_return


                # return serial_number
            # elif (serial_number not in serial.equipement_inventory_line_ids.equipement.serial_no):
            #     raise UserError(
            #                 _('The equipment scanned does not exist exist in the inventory selected !.'))
        # serial_used = self.env['workorder.details'].search([('workproduction_id.name', '=', po_name)]).mapped(
        #     'serial_number')
        # if serial:
        #     if serial not in serial_used:
        #         mrp_workorder_id.workorder_details.create({
        #             'serial_number': serial.id, 'workorder_id': mrp_workorder_id.id, })
        #         number_of_record = len(self.env['workorder.details'].search(
        #             [('workproduction_id.name', '=', po_name), ('workorder_id.name', '=', po_operation)]).mapped(
        #             'serial_number'))
        #         return number_of_record
        #     else:
        #         raise UserError(
        #             _('Using same serial number in two operation of the same PO is not allowed !.'))

    def dynamic_selection(self):
        result = self.env['maintenance.equipment'].read_group([("active", "=", "True")], fields=['location'],
                                                              groupby=['location'])
        select = []
        for rec in result:
            select = select + [(rec['location'], rec['location'])]
        return select

    def equip_inv(self):
        print("hello world !!!!! ")


    def get_equipement(self):
        self.statut = 'Countig'
        equip = self.env['maintenance.equipment'].search([('location','=',self.location)])
        print("len",len(equip))
        for rec in equip:
            print("heloo",rec)
            print("heloo",rec.category_id)
            self.env['intermediate.line'].create({
                'equipement': rec.id,
                'category': rec.category_id.id,
                'serial_no': rec.serial_no,
            })
        test = self.env['intermediate.line'].search([])

        for rec in test:
            print("loop", rec.serial_no)

            self.env['equipement.inventory.line'].create({
                'equipement': rec.equipement.id,
                'category': rec.category.id,
                'serial_no': rec.serial_no,
                'equipement_inventory_id': self.id,
            })
        self.env.cr.execute(
            "delete from intermediate_line"
        )


    def validate(self):
        self.statut = 'End'
        print("heloo world ::!!")
        e_i = self.equipement_inventory_line_ids
        m_e = self.env['maintenance.equipment'].search([])
        for rec in e_i:
            print("rec::::__________________________________",rec.equipement.name)
            for toto in m_e:
                if rec.equipement == toto:
                    print("toto::::", toto.name)
                    record_to_update = self.env['maintenance.equipment'].browse(toto.id)
                    if record_to_update.exists():
                        record_to_update.write({'barcode': rec.barcode})

                            # if rec.product_id == toto.product_id:
                #     record_to_update = self.env['stock.quant'].browse(toto.id)

    def done(self):
        print("done")

