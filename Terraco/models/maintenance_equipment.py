
from odoo import _, api, fields, models

class SmartestMaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'


    code = fields.Char(
        'history.equipment',
    )
    history_equipment = fields.Many2one(
        'history.equipment',
    )
    state = fields.Selection([
        ('stock','Stock'),
        ('affecter','Affecter')
    ])
    type_affectation = fields.Selection([
        ('definitif','Définitif'),
        ('provisoire','Provisoire')
    ])
    nature = fields.Selection([
        ('investissement','Investissement'),
        ('consommable','Consommable')
    ])
    etat = fields.Many2one(
        'etat.equipment'
    )
    project_id = fields.Many2one(
        'etat.equipment'
    )


    @api.model
    def create(self,vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].with_company(vals.get('company_id')).next_by_code('smartest.convention') or 'New'
        result = super(SmartestConvention, self).create(vals)
        return result


    if self.name == 'New':
        if self.is_quantity_copy != 'none':
            self.name = self.env['ir.sequence'].next_by_code('sale.requisition.sale.tender')
        else:
            self.name = self.env['ir.sequence'].next_by_code('sale.requisition.blanket.order')
