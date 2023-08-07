from odoo import fields, models


class PurchaseType(models.Model):
	_name = 'purchase.order.type'
	_description = "Type of purchase order"
	_order = 'code'
	_rec_name = 'code'
	name = field_name = fields.Char(
		string='name',
		)
	code = field_name = fields.Char(
		string='Code',
		required=True,
		)
	description = field_name = fields.Text(
		string='About this type',
		)
