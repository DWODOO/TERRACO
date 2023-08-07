# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, _, Command
from odoo.exceptions import ValidationError


class SmartestStartFormation(models.Model):
    _name = 'formation.start'
    _description = 'start course'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    smartest_company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                          default=lambda self: self.env.company)
    today = datetime.now().strftime("%Y-%m-%d")
    smartest_start_date = fields.Datetime('Date de Début', default=today)
    smartest_end_date = fields.Datetime("Date de Fin")
    smartest_plan_parent_id = fields.Many2one('plan', string='Plan Parent')
    smartest_start_formation = fields.Many2one('formation.details', string='formation')
    smartest_start_formation_name = fields.Char(string='formation name',
                                                related='smartest_start_formation.smartest_name')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    smartest_department_ids = fields.Many2many('hr.department', string='Department')
    smartest_responsible = fields.Many2one('hr.employee', string='Manager', relation='smartest_start_formation')
    smartest_employee_dep_ids = fields.Many2many('hr.employee')
    smartest_employee_ids = fields.Many2many('hr.employee', relation='departemnt_employees',
                                             domain="[('id', 'in', smartest_employee_dep_ids)]")
    # smartest_type_formation = fields.Selection(type,'Type de Formation')
    formation_state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'), ('request', 'Request'), ('confirmed', 'Confirmed'), ('progress', 'In Progress'),
                   ('done', 'Done'), ('cancel', 'Cancel')],
        default='draft',
        readonly=True, )

    def name_get(self):
        return [(record.id, record.smartest_start_formation_name) for record in self]

    def action_request(self):
        self.formation_state = 'request'

    def action_confirmed(self):
        self.formation_state = 'confirmed'
        # activty_type = self.env['mail.activity.type'].search([('name','=','Formation Warning')])
        # for rec in self.smartest_employee_ids:
        #     self.env['mail.activity'].create({
        #             'summary': 'You Are Assigned to this Formation',
        #             'activity_type_id': activty_type.id,
        #             'res_model_id': self.env['ir.model']._get_id('start.formation'),
        #             'res_id': self.id,
        #             'user_id': rec.user_id.id,
        #     }

    def action_progress(self):
        self.formation_state = 'progress'

    def action_done(self):
        self.formation_state = 'done'

    def action_cancel(self):
        self.formation_state = 'cancel'

    @api.onchange('smartest_department_ids')
    def _compute_smartest_employee_ids(self):
        if self.smartest_department_ids:
            self.smartest_employee_dep_ids = self.smartest_department_ids.member_ids.ids
            self.smartest_employee_ids = None
        else:
            self.smartest_employee_dep_ids = False

    def create_purchase_order(self):
        company = self.env.company
        product_ids = self.env['product.product'].search([('name', '=', 'Formation Service')])

        purchase_data = self._prepare_purchase_order(product_ids, company)
        self.env['purchase.order'].sudo().create(purchase_data)

    def _prepare_purchase_order(self, product_ids, company_id):
        logging_user = self.env.user
        date = fields.Date.today()
        return {
            'partner_id': self.smartest_start_formation.smartest_institute_id.id,
            'company_id': company_id.id,
            'user_id': logging_user.id,
            'date_order': date,
            'order_line': [Command.create(self._prepare_purchase_line_data(product_id, company_id)) for
                           product_id in product_ids],

        }

    @api.model
    def _prepare_purchase_line_data(self, product_id, company_id):
        """ Generate the Purchase Line values for the PO """

        return {
            'product_qty': 1,
            'product_id': product_id and product_id.id or False,
            'name': self.smartest_start_formation_name,
            'company_id': company_id and company_id.id or False,
            'price_unit': self.smartest_start_formation.smartest_course_price,
        }