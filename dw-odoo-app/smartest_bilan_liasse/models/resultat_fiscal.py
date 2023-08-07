from odoo import api, fields, models, _


class ResultFiscal(models.Model):
    _name = 'smartest_bilan.resultat_fiscal'
    _description = 'Import Export Mat'

    name = fields.Char(readonly="1",
                       string=" "
    )
    total = fields.Integer(
    )

    catego= fields.Char( string="Categories",readonly="1")

    resultfiscal_id = fields.Many2one('smartest_bilan.resultat_fis', tracking=True)
