from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseValidator(models.Model):
    _name = "purchase.validator"
    _description = "Purchase Validator"
    _order = "id desc"

    name = fields.Char('Name')
    validation_type = fields.Selection(
        [("qty", "Quantity"), ("amount", "Amount"), ("general", "general"), ("other", "other"),
         ("purchase_process", "Purchase Process max duration")], string='Type')
    line_ids = fields.One2many('purchase.validator.line', 'purchase_validator_id', string='Rules')
    days = fields.Integer('Days')


class PurchaseValidatorLine(models.Model):
    _name = "purchase.validator.line"
    _description = "Purchase Validator line"

    description = fields.Char('Description')
    purchase_validator_id = fields.Many2one('purchase.validator')
    min_value = fields.Float('Valeur Minmum')
    max_value = fields.Float('Valeur Maximum')
    group_validator = fields.Many2many('res.groups', string='Groupe',
                                       help="Groups that have the right to confirme the PO if the rule is applied")
    is_limitless = fields.Boolean('Has All Right')
