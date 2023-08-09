from odoo import _, fields, models, api
class SubDepartement(models.Model):
    _inherit = 'purchase.product.request'


    sub_departement = fields.Many2one('sub.departement', string="Sous Famille", domain="[('departement_id', '=', department_id)]")
    treatment = fields.Many2one('purchase.request.treatment', string="Traitement", domain="[('sub_departement', '=', sub_departement)]")

    @api.onchange('department_id')
    def compute_sub_departement(self):
        if not self.department_id:
            self.sub_departement = False
        elif not self.sub_departement:
            self.treatment = False
