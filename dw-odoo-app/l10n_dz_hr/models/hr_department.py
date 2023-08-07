from odoo import _, api, fields, models


class ResDepartment(models.Model):
    _inherit = 'hr.department'

    code = fields.Char(
        "Department Code"
    )
