# Part of SMARTEST ALGERIA
# Import python Libs
from datetime import timedelta

from odoo.exceptions import ValidationError

# Import Odoo libs
from odoo import _, api, fields, models


class SmartestImportFile(models.Model):
    _name = 'smartest.import.file'
    _description = "The import file (L/C)"
    _order = "id desc"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('pre_dom', 'Pré Domiciliation'),
            ('dom', 'Domiciliation'),
            ('open', 'Open'),
            ('closed', 'Closed'),
            ('expired', 'Expired'),
            ('rejected', 'Rejected'),

        ],
        tracking=True,
        force_save=True
    )

    import_plan_id = fields.Many2one(
        'smartest.import.plan',
        'Import Plan',
        domain="[('state', '=', 'approved'),('active', '=', True)]",
        tracking=True
    )
    import_file_type = fields.Selection([
        ('lc', 'Credit Letter'),
        ('tl', 'Free Transfer'),
        ('withoutdom', 'Without Domiciliation'),
    ], default="withoutdom",
        string='Importation File Type',
        required=True,
        tracking=True
    )
    bank_id = fields.Many2one(
        'res.bank',
        'Bank',
        required=True,
    )
    swift_confirming = fields.Char(
        'SWIFT',
    )
    commission_rate = fields.Float(
        'Commission rate',
    )
    agency_id = fields.Many2one(
        'res.bank.agency',
        domain="[('bank_id', '=', bank_id)]",
    )
    bank_authorization = fields.Char(
        'Bank Authorization',
        # required=True,
    )
    importation_type = fields.Selection([
        ('resale', 'Resale'),
        ('investment', 'Investment'),
        ('operation', 'Operation'),
    ],
        string='Importation Type',
    )
    currency_id = fields.Many2one('res.currency', string='Currency')
    supplier_id = fields.Many2one(
        'res.partner',
        domain='[("is_supplier","=", True)]'
    )

    supplier_image = fields.Binary(
        related='supplier_id.image_1920'
    )

    allocated_amount = fields.Monetary(
        'Allocated Amount',
        currency_field="currency_id",
    )
    bank_sent_date = fields.Date(
        'Bank Sent Date',
        tracking=True
    )
    note = fields.Text(
        'Note'
    )
    import_file_amount = fields.Monetary(
        'Import File Amount',
        currency_field="currency_id",
        tracking=True
    )
    fiscal_year_use = fields.Selection(related="import_plan_id.fiscal_year"
                                       )
    name = fields.Char(
        'Reference',
    )
    domiciliation_number = fields.Char(
        'Domiciliation Number',
    )
    opening_date = fields.Date(
        'Opening Date',
        tracking=True
    )
    expiration_date = fields.Date(
        'Expiration Date',
        help="Expiration Date = Opening date + 90 day.\n",
        tracking=True
    )
    boarding_deadline = fields.Date(
        'Boarding Deadline',
        help="Boarding Deadline = Expiration Date - 21 day.\n",
        tracking=True
    )
    file_lifetime = fields.Integer(
        'File Lifretime',
        help="Days left before expiration date.\n",
        compute='_compute_file_lifetime',
        default=0
    )
    closing_date = fields.Date(
        'Import File Closing Date',
        tracking=True
    )
    bank_reply_date = fields.Date(
        'Bank Reply Date',
        tracking=True
    )
    opening_exchange_rate = fields.Char(
        'Exchange Rate at Opening',
    )
    demande_exchange_rate = fields.Char(
        'Exchange Rate at Demande',
    )
    current_user_id = fields.Many2one(
        'res.users',
        'Closed By',
        # default=lambda self: self.env.user.id
    )
    transport_mode = fields.Selection(
        [
            ('shipping', 'Shipping'),
            ('air', 'Air transport '),
            ('rail', 'Rail transport.'),
        ],
        string='Transport Mode',
    )
    air_waylbill_refrence = fields.Char(
        'Air Waylbill Refrence'
    )
    remaining_age = fields.Integer(
        'Remaining age',
        compute='_compute_remaining_age',
        default=0
    )
    type = fields.Selection([
        ('import', 'Import'), ('export', 'Export'),
    ], string="Type", default="import",
        required=True,
        tracking=True)
    import_folder_id = fields.Many2one('smartest.import.folder', string="Import Folder")
    export_folder_id = fields.Many2one('export.folder', string="Export Folder")

    # @api.model
    # def create(self, vals):
    #     """
    #     Override the create method in order to automatically generate the import file name according to
    #     the type (lc/tl/withoutdom).
    #     """
    #     import_file_type = vals.get('import_file_type')
    #     name = vals.get('name')
    #     if not name:
    #
    #         if import_file_type == 'lc':
    #             vals['name'] = self.env.ref('smartest_foreign_trade.import_file_lc_sequence').next_by_id()
    #         elif import_file_type == 'tl':
    #             vals['name'] = self.env.ref('smartest_foreign_trade.import_file_tl_sequence').next_by_id()
    #         else:
    #             vals['name'] = self.env.ref('smartest_foreign_trade.import_file_withoutdom_sequence').next_by_id()
    #     return super(SmartestImportFile, self).create(vals)

    def action_confirm(self):
        """
        This method is used by the Confirm action button. It updates the task state to 'Opened'.
        """
        if self.filtered(lambda task: task.state not in ['draft']):
            raise ValidationError(
                _("Only Draft Files can be Marked as Open")
            )
        if not self.filtered(lambda task: task.opening_date):
            raise ValidationError(
                _("You should specify the Opening Date first")
            )
        return self.write({
            'state': 'open'
        })

    def action_reopen(self):
        """
        This method is used by the Confirm action button. It updates the task state to 'Opened'.
        """
        if self.filtered(lambda task: task.state not in ['closed']):
            raise ValidationError(
                _("Only Closed Files can be Re-Opened")
            )
        return self.update({
            'state': 'open'
        })

    def action_close(self):
        """
        This method is used by the Close action button. It updates the task state to 'Closed'.
        """
        # if self.filtered(lambda task: task.state not in ['open']):
        #     raise ValidationError(
        #         _("Only Open files can be Closed")
        #     )
        return self.update({
            'current_user_id': self.env.user.id,
            'closing_date': fields.Date.today(),
        })

    @api.depends('expiration_date', 'opening_date')
    def _compute_remaining_age(self):
        remaining_age = 0
        files_without_tl = self.filtered(lambda file: file.import_file_type not in ['tl'] and file.expiration_date)
        files_with_tl = self.filtered(lambda file: file.import_file_type in ['tl'] or not file.expiration_date)
        for file in files_without_tl:
            remaining_age = int((file.expiration_date - file.opening_date).days)
            file.update({
                'remaining_age': remaining_age,
            })
        files_with_tl.update({
            'remaining_age': remaining_age,
        })

    @api.depends('expiration_date', 'import_file_type', 'state')
    def _compute_file_lifetime(self):
        file_lifetime = 0
        files_without_tl_and_exp_date = self.filtered(
            lambda file: file.import_file_type not in ['tl'] and file.expiration_date)
        files_without_tl_and_not_exp_date = self.filtered(
            lambda file: file.import_file_type not in ['tl'] and not file.expiration_date)
        files_with_tl = self.filtered(lambda file: file.import_file_type in ['tl'])
        files_without_tl_and_not_exp_date.update({
            'file_lifetime': file_lifetime,
        })
        files_with_tl.update({
            'file_lifetime': file_lifetime,
        })
        for file in files_without_tl_and_exp_date:
            file_lifetime = int((file.expiration_date - fields.Date.today()).days)
            if file_lifetime <= 0 and (file.state == 'open'):
                file.update({
                    'file_lifetime': file_lifetime,
                    'state': 'expired',
                })
            else:
                if file_lifetime > 0 and file.state == 'expired':
                    file.update({
                        'state': 'open',
                    })
                file.update({
                    'file_lifetime': file_lifetime,
                })

    @api.onchange('opening_date')
    def _onchange_opening_date(self):
        """
        When the opening date changes we update the relative fields.
        """
        if self.opening_date:
            if self.import_file_type != 'tl':
                self.expiration_date = self.opening_date + timedelta(days=90)
                self.boarding_deadline = self.opening_date + timedelta(days=69)

    @api.onchange('import_file_type')
    def _onchange_opening_date(self):
        """
        When the opening date changes we update the state field.
        """
        if self.import_file_type != 'withoutdom':
            self.state = "pre_dom"
        else:
            self.state = "draft"

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_open(self):
        files_with_dom = self.filtered(lambda file: file.import_file_type not in ['withoutdom'])
        files_without_dom = self.filtered(lambda file: file.import_file_type in ['withoutdom'])
        files_with_dom.write({'state': 'pre_dom'})
        files_without_dom.write({'state': 'open'})

    def action_rejected(self):
        self.write({'state': 'rejected'})

    def action_closed(self):
        self.action_close()
        files_with_dom = self.filtered(lambda file: file.import_file_type not in ['withoutdom'])
        files_without_dom = self.filtered(lambda file: file.import_file_type in ['withoutdom'])
        files_with_dom.write({'state': 'dom'})
        files_without_dom.write({'state': 'closed'})

    @api.model
    def action_import_files_analysis(self):
        domain = []
        if self.env.context['active_model'] == 'export.folder':
            export_folder = self.env.context.get('active_ids')
            if export_folder:
                domain = [('export_folder_id', 'in', self.env.context.get('active_ids', []))]
            export_folder_id = self.env["export.folder"].browse(export_folder[-1])
        else:
            purchase_folder_import_id = self.env.context.get('active_ids')

            if purchase_folder_import_id:
                domain = [('import_folder_id', 'in', self.env.context.get('active_ids', []))]
            purchase_folder_import_id = self.env["smartest.import.folder"].browse(purchase_folder_import_id[-1])

        action = self.env['ir.actions.act_window']._for_xml_id('smartest_foreign_trade.import_file_lc_action')
        action['display_name'] = _("Credit Commitment Analysis")
        action['domain'] = domain
        if self.env.context['active_model'] == 'export.folder':
            action['context'] = {'default_export_folder_id': export_folder_id.id,
                                 'default_type': 'export',
                                 }
        else:
            action['context'] = {'default_import_folder_id': purchase_folder_import_id.id,
                                 }
        return action
