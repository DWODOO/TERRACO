from odoo import api, fields, models, _


class HrLawSections(models.Model):
    _name = 'hr.law.sections'
    _description = "Hr Law Sections"
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        "Name"
    )
    description = fields.Html(
        "Description"
    )
    law_type = fields.Selection(
        [
            ('contract', 'Contract'),
            ('decision', 'Decision')
        ]
    )
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=1)
    not_article = fields.Boolean()
