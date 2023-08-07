# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError

class SmartestRepairOrder(models.Model):
    _inherit = 'repair.order'

    #first inherit these fields and make them not required
    product_id = fields.Many2one(
        'product.product', string='Product to Repair',
        domain="[('type', 'in', ['product', 'consu']), '|', ('company_id', '=', company_id), ('company_id', '=', False)]",
        readonly=True, required=False, states={'draft': [('readonly', False)]}, check_company=True)
    product_qty = fields.Float(
        'Product Quantity',
        default=1.0, digits='Product Unit of Measure',
        readonly=True, required=False, states={'draft': [('readonly', False)]})
    product_uom = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        readonly=True, required=False, states={'draft': [('readonly', False)]}, domain="[('category_id', '=', product_uom_category_id)]")
    location_id = fields.Many2one(
        'stock.location', 'Location',
        index=True, readonly=True, check_company=True,
        help="This is the location where the product to repair is located.",
        states={'draft': [('readonly', False)], 'confirmed': [('readonly', True)]})
    #Custom fields
    repair_equipement = fields.Boolean('Maintenance sur Equipement')
    equipement_id = fields.Many2one(
        'maintenance.equipment', string='Equipement to Repair',
        domain="['|', ('company_id', '=', company_id), ('company_id', '=', False)]", check_company=True)
    maintenance_request_id = fields.Many2one('maintenance.request',string="Maintenance Request")
    picking_id = fields.Many2one('stock.picking',string="Transfert")
    compute_state = fields.Boolean(compute='validate_equipment_repair')
    state = fields.Selection(selection_add=[('picking', 'Livraison')])

    def open_maintenance_order(self):
        "open maintenance order from repair view"
        view = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(self.env.ref('maintenance.hr_equipment_request_view_form').id, 'form')],
            'name': _('Maintenance Order'),
            'res_model': 'maintenance.request',
            'res_id': self.maintenance_request_id.id,
        }
        return view

    def open_picking_transfert(self):
        "open maintenance order from repair view"
        view = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(self.env.ref('stock.view_picking_form').id, 'form')],
            'name': _('Stock Picking'),
            'res_model': 'stock.picking',
            'res_id': self.picking_id.id,
        }
        return view

    def action_validate(self):
        "inherit validate function and skip fct if repair equipment"
        self.ensure_one()
        if self.filtered(lambda repair: any(op.product_uom_qty < 0 for op in repair.operations)):
            raise UserError(_("You can not enter negative quantities."))
        if self.repair_equipement:
            self.action_repair_confirm()
        else:
            return super(SmartestRepairOrder, self).action_validate()

    def action_repair_end(self):
        "inherit  function and change state if  repair equipment"
        if self.filtered(lambda repair: repair.state != 'under_repair'):
            raise UserError(_("Repair must be under repair in order to end reparation."))
        for repair in self:
            if repair.repair_equipement:
                repair.write({'repaired': True})
                vals = {}
                vals['state'] = 'picking'
                vals['move_id'] = repair.action_repair_done()
                repair.write(vals)
                return True
            else:
                return super(SmartestRepairOrder, self).action_repair_end()

    def action_repair_done(self):
        "inherit  function and if  repair equipment create picking"
        if self.filtered(lambda repair: not repair.repaired):
            raise UserError(_("Repair must be repaired in order to make the product moves."))
        self._check_company()
        self.operations._check_company()
        self.fees_lines._check_company()
        res = {}
        for repair in self:
            if not repair.repair_equipement:
                return super(SmartestRepairOrder, self).action_repair_done()
            else :
                repair._action_create_picking()


    def get_lines_values(self):
        for this in self:
            move_lines = []
            for line in this.operations:
                vals = {
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'location_id': line.location_id.id,
                    'location_dest_id': line.location_dest_id.id,
                }
                move_lines.append(vals)
            return move_lines

    def _action_create_picking(self):
        # Create stock picking
        company_id = self.env.user.company_id
        vals_list = []
        for repair in self:
            new_moves = repair.operations.filtered(
                lambda this: not this.move_id and this.state != 'done')
            if new_moves:
                vals_list.append({
                    'partner_id': repair.partner_id.id,
                    'picking_type_id': self.env['stock.picking.type'].search([('code','=','internal')],limit=1).id,
                    'location_id': repair.location_id.id,
                    'location_dest_id': self.env['stock.location'].search([('usage','=','production')],limit=1).id,
                    'repair_order_id': repair.id,
                    'company_id': company_id.id,
                    'origin': repair.name,
                    'move_ids_without_package': self.get_lines_values(),
                })
        if not vals_list:
            return True
        self.picking_id = self.env['stock.picking'].create(vals_list)
        self.picking_id.repair_order_id = self.id
        self.picking_id.action_confirm()
        self.picking_id.action_assign()
        # return picking_id.id

    def validate_equipment_repair(self):
        "this fonction change the state of the repair if the picking linked is done"
        for repair in self:
            repair.compute_state = True
            if repair.repair_equipement and repair.picking_id.state == 'done' and repair.state != 'done' and repair.state == 'picking' :
                repair.state = 'done'
                repair.maintenance_request_id.stage_id = self.env['maintenance.stage'].search([('sequence','=',repair.maintenance_request_id.stage_id.sequence+1)])
                return


class SmartestStockPicking(models.Model):
    _inherit = 'stock.picking'

    repair_order_id = fields.Many2one('repair.order')

