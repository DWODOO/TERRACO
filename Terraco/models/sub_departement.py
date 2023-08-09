# -*- coding:utf-8 -*-

from odoo import _, fields, models

class SubDepartement(models.Model):
    _name = 'sub.departement'
    _description = 'sous familles des départements'


    sub_departement = fields.Char(string="Sous Famille")
    departement_id = fields.Many2one("hr.department", string="Famille")

    def name_get(self):
        return [(record.id, record.sub_departement) for record in self]
class PurchaseRequestTreatment(models.Model):
    _name = 'purchase.request.treatment'
    _description = 'traitement par sous familles'

    treatment = fields.Char(string="Traitement")
    sub_departement = fields.Many2one("sub.departement", string="Sous  familles")

    def name_get(self):
        return [(record.id, record.treatment) for record in self]

