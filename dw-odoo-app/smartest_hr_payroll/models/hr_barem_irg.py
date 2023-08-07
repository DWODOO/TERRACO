# Part of SMARTEST ALGERIA

# Import Odoo libs
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrBaremeIrg(models.Model):
    _name = 'hr.bareme.irg'
    _description = "IRG Plan"
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
    smartest_amount_deducted = fields.Float(
        string='Amount Deducted',
        required=True
    )
    smartest_amount_cumul = fields.Float(
        string='Amount To Add',
        required=True,
        readonly=True
    )
    smartest_active = fields.Boolean(
        string='Active',
        default=True

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
