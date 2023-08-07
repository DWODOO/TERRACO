from datetime import timedelta
import datetime
import time
from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_request_ids = fields.Many2many(
        'purchase.request',
        'purchase_request_purchase_order_rel',
        column1="purchase_order_id",
        column2="purchase_request_id",
        string="Origin Requests",
        readonly=True,
        copy=False,
    )

    purchase_request_count = fields.Integer(
        compute="_compute_line_count"
    )
    state = fields.Selection(selection_add=[('technical_validation', 'Validation Technique'),
                                            ('quantity_validation', 'Validation Quantitative'),
                                            ('financial_validation', 'Validation Financiere'), ('purchase',)])
    # requisition_last_date = fields.Datetime(related='requisition_id.date_end',string='Convention End Date')
    team_members_id = fields.Many2many('res.users', string='Purchase team members')
    require_tech_validation = fields.Boolean('Require Technical Validation')
    tech_validator_id = fields.Many2one('res.users', string='Technical Validator', tracking=True)
    url = fields.Char()
    purchase_request_create_id = fields.Many2one('res.users')
    service_done = fields.Boolean('Service Fait')

    @api.onchange('service_done')
    def check_service_done(self):
        for order in self:
            if order.purchase_request_create_id and order.state == 'done':
                if order.purchase_request_create_id == self.env.user and order.state == 'purchase':
                    continue
                else:
                    raise ValidationError(
                        _("Only the user : %s can edit this field") % (order.purchase_request_create_id.name))

    # @api.onchange('requisition_id')
    # def check_requisition_end_date(self):
    #     for order in self:
    #         if order.requisition_last_date:
    #             process_days = self.env['purchase.validator'].search([('validation_type','=','purchase_process')], limit=1)
    #             if order.requisition_last_date < order.date_order + timedelta(days=process_days.days):
    #                 raise exceptions.Warning(_('The Purchase order process may outdate the convention date %s.') % order.requisition_last_date)
    def fiancial_validator_method(self):
        for order in self:
            if order.purchase_request_ids:
                for rec in order.purchase_request_ids:
                    rec.financial_validator = self.env.user
                    rec.po_date_approve = datetime.datetime.now()

    @api.depends("purchase_request_ids")
    def _compute_line_count(self):
        for order in self:
            order.purchase_request_count = len(order.mapped("purchase_request_ids"))

    def action_view_purchase_request(self):
        """
        This method is used by the Purchase Request smart button. It opens a form view or a tree view
        :return: Action Dict
        """

        requests = self.mapped('purchase_request_ids')
        if not requests:
            raise UserError(
                _('There is no Request to view.')
            )
        tree_view = self.env.ref('smartest_purchase_request.view_purchase_request_tree')
        form_view = self.env.ref('smartest_purchase_request.view_purchase_request_form')
        action = {
            'name': _('Purchase Request(s)'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.request',
            'context': {'default_purchase_order_ids': [(4, self.id)]}
        }
        if len(requests) == 1:
            action['views'] = [(form_view.id, 'form')]
            action['res_id'] = requests.id
            action['view_mode'] = 'form'
        else:
            action['views'] = [(tree_view.id, 'tree'), (form_view.id, 'form')]
            action['domain'] = [('id', 'in', requests.ids)]
        return action

    def send_mail_to_pr_created_by(self):
        for order in self:
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data._xmlid_lookup('smartest_purchase_request.mail_template_request_Quantity_validation')[
                2]
            template = self.env['mail.template'].browse(template_id)
            order.team_members_id = order.purchase_request_create_id
            template.send_mail(self.id, force_send=True)

    def send_mail_to_quantity_validator(self):
        for order in self:
            validator = self.env['purchase.validator'].search([('validation_type', '=', 'qty')], limit=1)
            for line in order.order_line:
                for rule in validator.line_ids.sorted('id', reverse=False):
                        if   line.product_qty <= rule.max_value or rule.is_limitless:
                            if rule.group_validator.id == self.env.ref(
                                    'smartest_purchase_request.group_team_leader').id:
                                order.send_mail_to_pr_created_by()
                                break
                            for u in rule.group_validator.users:
                                ir_model_data = self.env['ir.model.data']
                                template_id = ir_model_data._xmlid_lookup('smartest_purchase_request.mail_template_request_Quantity_validation')[
                                    2]
                                template = self.env['mail.template'].browse(template_id)
                                order.team_members_id = u
                                template.send_mail(self.id, force_send=True)
                            break

    def send_mail_to_financial_validator(self):
        for order in self:
            validator = self.env['purchase.validator'].search([('validation_type', '=', 'amount')], limit=1)
            for rule in validator.line_ids.sorted('id', reverse=False):
                    if order.amount_total <= rule.max_value or rule.is_limitless:
                        if rule.group_validator.id == self.env.ref('smartest_purchase_request.group_team_leader').id:
                            order.send_mail_to_pr_created_by()
                            break
                        for u in rule.group_validator.users:
                            ir_model_data = self.env['ir.model.data']
                            template_id = ir_model_data._xmlid_lookup('smartest_purchase_request.mail_template_request_Financial_validation')[
                                2]
                            template = self.env['mail.template'].browse(template_id)
                            order.team_members_id = u
                            template.send_mail(self.id, force_send=True)
                        break

    def quantity_validation(self):
        for order in self:
            validator = self.env['purchase.validator'].search([('validation_type', '=', 'qty')], limit=1)
            if not validator:
                order.state = 'financial_validation'
            for line in order.order_line:
                for rule in validator.line_ids.sorted('id', reverse=False):
                    if self.env.uid in rule.group_validator.mapped('users.id') and (
                            line.product_qty <= rule.max_value or rule.is_limitless):
                        order.state = 'financial_validation'
                        break
                else:
                    raise ValidationError(_('You dont have the right to validate this Purchase Order.'))

    def sent_for_technical_validation(self):
        for order in self:
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data._xmlid_lookup('smartest_purchase_request.mail_template_request_Tehcnical_validation')[2]
            template = self.env['mail.template'].browse(template_id)
            template.send_mail(self.id, force_send=True)

    def financial_validation(self):
        for order in self:
            validator = self.env['purchase.validator'].search([('validation_type', '=', 'amount')], limit=1)
            if not validator:
                order.button_confirm()
            for rule in validator.line_ids.sorted('id', reverse=False):
                if (
                        order.amount_total <= rule.max_value or rule.is_limitless) and self.env.uid in rule.group_validator.mapped(
                    'users.id'):
                    order.fiancial_validator_method()
                    order.button_confirm()
                    return
            else:
                raise ValidationError(_('You dont have the right to validate this Purchase Order.'))

    def sent_mail_to_created_by(self):
        for order in self:
            body = "Quantity Validation Done!"
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data._xmlid_lookup('smartest_purchase_request.mail_template_request_Quantity_validation')[2]
            template = self.env['mail.template'].browse(template_id)
            order.team_members_id = order.create_uid
            template.send_mail(self.id, force_send=True)
    def check_technical_validator(self):
        for rec in self:
            if rec.tech_validator_id != self.env.user:
                raise ValidationError(_('You dont have the right to validate this Purchase Order, Only the Technical Validator can validate this state!.'))


    def button_approval(self):
        for order in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            base_url = '/web?db=%s#id=%d&view_type=form&model=%s' % (self._cr.dbname,self.id, self._name)
            order.url = base_url
            if order.state == 'draft':
                if order.require_tech_validation:
                    try:
                        order.sent_for_technical_validation()
                    except:
                        pass
                    order.state = 'technical_validation'
                else:
                    try:
                        order.send_mail_to_quantity_validator()
                    except:
                        pass
                    order.state = 'quantity_validation'
            elif order.state == 'sent':
                if not order.payment_term_id:
                    raise ValidationError(_('please set the Receipt Date and the Payment Terms!.'))
                if order.require_tech_validation:
                    try:
                        order.sent_for_technical_validation()
                    except:
                        pass
                    order.state = 'technical_validation'
                else:
                    try:
                        order.send_mail_to_quantity_validator()
                    except:
                        pass
                    order.state = 'quantity_validation'
            elif order.state == 'technical_validation':
                try:
                    order.check_technical_validator()
                    order.sent_mail_to_created_by()
                except:
                    pass
                # order.send_mail_to_quantity_validator()
                order.state = 'quantity_validation'
            elif order.state == 'quantity_validation':
                try:
                    order.send_mail_to_financial_validator()
                except:
                    pass
                order.quantity_validation()
            elif order.state == 'financial_validation':
                order.financial_validation()

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'financial_validation']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.company.currency_id._convert(
                        order.company_id.po_double_validation_amount, order.currency_id, order.company_id,
                        order.date_order or fields.Date.today())) \
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    purchase_request_line_ids = fields.Many2many(
        "purchase.request.line",
        "purchase_order_line_ids",
        string="Purchase Request Lines",
        readonly=True,
        copy=False,
    )

    @api.onchange('product_id')
    def onchange_product_id(self):
        initial_quantity = self.product_qty
        initial_name = self.name
        super(PurchaseOrderLine, self).onchange_product_id()
        if initial_quantity:
            self.product_qty = initial_quantity
        if initial_name:
            self.name = initial_name
