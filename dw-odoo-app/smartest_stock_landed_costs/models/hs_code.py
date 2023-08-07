from odoo import fields, models


class SmartestHsCode(models.Model):
    _name = 'stock.hs.code'
    _description = "Clearance Rate by HS Code"

    name = fields.Char(
        "HS Code",
        index=True,
    )
    description = fields.Char(
        "Description"
    )
    percentage = fields.Float(
        "Clearance Rate"
    )
    test = fields.Selection([
        ('1', 'One'),
        ('2', 'Two'),
    ])

    # _sql_constraints = [
    #     ('name_uniq', 'unique (name)', 'The HS Code must be unique !'),
    # ]
