# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    smartest_code_prefix = fields.Char(string="Prefix")
    smartest_padding_code = fields.Integer(string="Code Length")

    @api.constrains('smartest_padding_code')
    def _check_smartest_padding_code(self):
        if any(record.smartest_padding_code <= 0 for record in self):
            raise ValidationError(_('Code length Must Be greater than 0.!'))

    @api.model
    def get_values(self):
        config = super(ResConfigSettings, self).get_values()
        config['smartest_code_prefix'] = self.env['ir.config_parameter'].sudo().get_param('hr_payroll.smartest_code_prefix')
        config['smartest_padding_code'] = self.env['ir.config_parameter'].sudo().get_param('hr_payroll.smartest_padding_code')

        return config

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('hr_payroll.smartest_code_prefix', self.smartest_code_prefix)
        self.env['ir.config_parameter'].sudo().set_param('hr_payroll.smartest_padding_code', self.smartest_padding_code)

        super(ResConfigSettings, self).set_values()