# Part of SMARTEST ALGERIA
# Import python Libs
import calendar
import datetime
from datetime import datetime

# Import Odoo libs
from odoo import api, fields, models


class SmartestImportPlan(models.Model):
    _name = 'smartest.import.plan'
    _description = "The fiscal year import plan"
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        'Name',
        readonly=True
    )

    fiscal_year = fields.Selection(
        [
            (str(num), str(num)) for num in range(2010, datetime.now().year + 1)
        ],
        'Year',
        required=True,
        default=str(datetime.now().year),
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True
    )

    fiscal_month = fields.Selection(
        [
            ('1', 'Jan'),
            ('2', 'Feb'),
            ('3', 'Mar'),
            ('4', 'Apr'),
            ('5', 'May'),
            ('6', 'Jun'),
            ('7', 'Jul'),
            ('8', 'Aug'),
            ('9', 'Sep'),
            ('10', 'Oct'),
            ('11', 'Nov'),
            ('12', 'Dec'),
        ],
        'Month',
        required=True,
        default='1',
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True
    )

    supplier_id = fields.Many2one(
        'res.partner',
        domain='[("is_supplier","=", True)]',
        readonly=True,
        states={'draft': [('readonly', False), ('required', True)]},
        tracking=True
    )

    currency_id = fields.Many2one('res.currency', string='Currency',
                                  readonly=True,
                                  states={'draft': [('readonly', False), ('required', True)]},
                                  tracking=True)

    value = fields.Monetary(
        'Value',
        currency_field="currency_id",
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        tracking=True
    )

    active = fields.Boolean(string="Active", default="True"
                            )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('expired', 'Expired'),
            ('rejected', 'Rejected'),

        ],
        default='draft',
        tracking=True
    )

    note = fields.Text(
        'Note',
    )

    validity_date = fields.Date(
        'Valide Untill',
        # readonly=True,
        store=True,
        readonly=True,
        states={'draft': [('readonly', False), ('required', True)]},
        tracking=True
    )

    @api.model
    def create(self, vals):
        """
        Override the create method in order to automatically generate the import file name according to
        it's year/month.
        """

        vals['name'] = self.env.ref('smartest_foreign_trade.import_plan_sequence').next_by_id()
        return super(SmartestImportPlan, self).create(vals)

    @api.onchange('fiscal_year', 'fiscal_month')
    def _onchange_opening_date(self):
        """
        When the fiscal year or the fiscal month fields change we update the validity date.
        """
        self.validity_date = datetime(int(self.fiscal_year), int(self.fiscal_month),
                                      calendar.monthrange(int(self.fiscal_year), int(self.fiscal_month))[1])

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_approved(self):
        self.write({'state': 'approved'})

    def action_rejected(self):
        self.write({'state': 'rejected'})

    def action_expired(self):
        self.write({'state': 'expired'})

    @api.depends('validity_date')
    def _compute_expired_import_plan(self):
        """
        When the validity_date of the import plan is consumed and the import plan is not approved it turns to an expired plan.
        """
        today = fields.Datetime.today()

        expired_plan = self.filtered(
            lambda plan: plan.validity_date > today and plan.state not in ['approved', 'rejected'])
        expired_plan.action_expired()
