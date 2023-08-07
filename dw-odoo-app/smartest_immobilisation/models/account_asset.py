# -*- coding: utf-8 -*-

from odoo import models, fields, api


class smartest_stock(models.Model):
    _inherit = 'account.asset'

    anouar_test = fields.Many2one('maintenance.equipment')
    just_test = fields.Char(default="False")

    @api.onchange('anouar_test')
    def set_asset_name(self):
        self.just_test = str(self.anouar_test.display_name)
        # self.name = str(self.anouar_test.name)+'/'+str(self.anouar_test.serial_no)
        self.name = self.anouar_test.display_name
        print("hello",self.anouar_test.category_id.name)
        print("hello",self.just_test)
        # self.get_equipment_name(self.anouar_test.category_id.name)


    # def get_equipment_name(self,cat):
    #     test = self.env["maintenance.equipment"].search([('category_id.name','=',cat)])
    #     print("len test is :",len(test))
    #     for rec in test:
    #         print("rec is -()-)(-()-",rec.display_name)

    def open_equipment(self):
        print("EQUIPMENT")
        print("statuesss : ",self.just_test)
        return{
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.equipment',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('maintenance.hr_equipment_view_form').id,
            'res_id': self.anouar_test.id,
            'target': 'current',
        }