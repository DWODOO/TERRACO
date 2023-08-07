# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta

AVAILABLE_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Normal'),
    ('2', 'hight'),
    ('3', 'Urgent')
]

class SmartestPreventiveDates(models.Model):
    _name = 'maintenance.preventive.dates'

    #this module purpose is the creation of preventive Maintenance order

    maintenance_request_ids = fields.One2many('maintenance.request','preventive_id', string="Maintenance Requests")
    number_maintenance_request_ids = fields.Integer(compute="get_number_maintenances_ids", string="Request(s)")
    equipment_id = fields.Many2one('maintenance.equipment', string="Equipement")
    user_id = fields.Many2one('res.users', string="Assigne to")
    name = fields.Char(string="Name", default='/')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self : self.env.company)
    start_date = fields.Date(string='Start Date')
    state = fields.Selection([('draft','Draft'),('done','Done')],default='draft')
    priority = fields.Selection(AVAILABLE_PRIORITIES, "Priority", default='0')
    period_str = fields.Selection([
        ('yearly', 'Yearly'),
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('daily', 'Daily'),('custom','Custom')],ondelete='cascade',string="periodically")
    period = fields.Integer(string="Period (days)")
    nbr_due_dates = fields.Integer(string="Nombre D'écheance")
    pdr_line_ids = fields.One2many('maintenance.preventive.lines','operation_preventive_id',string="PDR Lines", domain=[('is_pdr', '=', True),('is_operation', '=', False)])
    operation_line_ids = fields.One2many('maintenance.preventive.lines','operation_preventive_id',string="Operations Lines", domain=[('is_operation', '=', True),('is_pdr', '=', False)])

    def get_number_maintenances_ids(self):
        for this in self:
            maintenances_ids = self.env['maintenance.request'].search([('preventive_id', '=', this.id)])
            this.number_maintenance_request_ids = 0 if not maintenances_ids else len(maintenances_ids.mapped('id'))

    @api.onchange('period_str')
    def onchange_period_str(self):
        for this in self:
            if this.period_str == 'yearly':
                this.period = 365
            elif this.period_str == 'monthly':
                this.period = 30
            elif this.period_str == "weekly":
                this.period = 7
            elif this.period_str == "daily":
                this.period = 1
            else :
                this.period = 0

    def prepare_confirmed_vals(self,Date):
        self.ensure_one()
        maintenance_request_vals = {
            'name': 'MP'+'/'+self.equipment_id.name +'/'+str(Date),
            'preventive_id': self.id,
            'equipment_id': self.equipment_id.id,
            'maintenance_type': 'preventive',
            'category_id': self.equipment_id.category_id.id,
            'user_id': self.user_id.id,
            'company_id': self.company_id.id,
            'request_date': date.today(),
            'schedule_date': Date,
            'priority': self.priority,
        }
        return maintenance_request_vals


    def confirm_equipement_maintenance_preventif(self):
        for this in self:
            date = this.start_date
            for i in range(this.nbr_due_dates):
                vals = this.prepare_confirmed_vals(date)
                date += timedelta(days=this.period)
                this.maintenance_request_ids.create(vals)
                this['state'] = 'done'

    def action_open_maintenance_ids(self):
        for this in self:
            maintenance_ids = self.env['maintenance.request'].search([('preventive_id', '=', this.id)])
            return {
                "type": "ir.actions.act_window",
                "res_model": "maintenance.request",
                "views": [[self.env.ref('maintenance.hr_equipment_request_view_tree').id, "tree"],
                          [False, "form"], [False, "calendar"]],
                "domain": [["id", "in", maintenance_ids.ids]],
                "name": _("Maintenance Request(s)"),
            }

    def unlink(self):
        """
        Overriding rhe unlink method in order to disallow deleting record that are not in draft state
        """
        if self.filtered(lambda task: task.state not in ['draft']):
            raise ValidationError(
                _("You can only delete draft or canceled records.")
            )
        return super(SmartestPreventiveDates, self).unlink()



class SmartestPreventiveDatesMoveLine(models.Model):
    _name = 'maintenance.preventive.lines'

    operation_preventive_id = fields.Many2one('maintenance.preventive.dates',string="Preventive Date")
    product_id = fields.Many2one('product.product',string="Produit")
    product_qty = fields.Integer(string="Quantity")
    product_uom = fields.Many2one('uom.uom',related="product_id.uom_id",string="UOM")
    location_id = fields.Many2one('stock.location',string='Start Location')
    is_pdr = fields.Boolean('PDR')
    is_operation = fields.Boolean('Operation')
    operation_name = fields.Char('Opération')