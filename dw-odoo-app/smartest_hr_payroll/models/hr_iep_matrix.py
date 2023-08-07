# Part of SMARTEST ALGERIA

# Import Odoo libs
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrIEPMatrix(models.Model):
    _name = 'hr.iep.matrix'
    _description = "IEP Plan IN"
    _order = 'smartest_bound_from'

    smartest_bound_from = fields.Float(
        string='Bound From',
        required=True
    )
    smartest_bound_to = fields.Float(
        string='Bound To',
        required=True
    )
    smartest_rate = fields.Float(
        string='rate',
        required=True
    )
    smartest_active = fields.Boolean(
        string='Active',
        default=True

    )
    smartest_iep_in = fields.Boolean(
        string='IEP IN'
    )
    smartest_date_from = fields.Date(string='From',
                                     default=fields.Date.context_today)
    smartest_date_to = fields.Date(string='To')

    @api.constrains('smartest_bound_from', 'smartest_bound_to')
    def _check_bound_validity(self):
        if any(
                record.smartest_bound_from and record.smartest_bound_to and record.smartest_bound_to < record.smartest_bound_from
                for record in self):
            raise ValidationError(
                _('Bound To Must Be greater than Bound From!')
            )
