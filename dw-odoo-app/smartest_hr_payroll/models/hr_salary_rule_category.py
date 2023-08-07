# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA

# Import Odoo libs
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class SmartestHrSalaryRuleCategory(models.Model):
    _inherit = 'hr.salary.rule.category'

    smartest_category_type = fields.Selection(
        string="Category Type",
        selection=[("base", "Basic"),
                   ("contribution", "Contribution"),
                   ("contribution_10", "Contribution 10%"),
                   ("taxable", "Taxable"),
                   ("taxable_10", "Taxable 10%"),
                   ("net", "Net"),
                   ("other", "Other"),
                   ("abs", "Absence"),
                   ("exceptional", "Exceptional"),
                   ("ni_impo_ni_coti", "Neither taxable nor contributory")
                   ]
    )
    smartest_range_min = fields.Integer(
        string="From"
    )
    smartest_range_max = fields.Integer(
        string="To"
    )

    @api.constrains('smartest_range_min', 'smartest_range_max')
    def _check_range(self):
        for record in self:
            if not (record.smartest_range_min <= record.smartest_range_max):
                raise ValidationError(_('Minimum Date Range <= To Maximum Date Range !'))
            # chevauchement = self.env['hr.salary.rule.category'].sudo().search(
            #     ['&', ('id', '!=', record.id), '|', '&',
            #      ('smartest_range_min', '<=', record.smartest_range_min), ('smartest_range_max', '>=', record.smartest_range_min), '|', '&',
            #      ('smartest_range_min', '<=', record.smartest_range_max), ('smartest_range_max', '>=', record.smartest_range_min), '&',
            #      ('smartest_range_min', '>=', record.smartest_range_min), ('smartest_range_max', '<=', record.smartest_range_max)], limit=1)
            # if chevauchement:
            #     raise ValidationError(
            #         _('Range Overlaps with (%s) : From (%d) To (%d)', chevauchement.name,
            #           chevauchement.smartest_range_min,
            #           chevauchement.smartest_range_max))
