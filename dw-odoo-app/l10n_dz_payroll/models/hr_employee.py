# -*- coding:utf-8 -*-
from odoo import api, fields, models
from odoo.osv import expression


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    recruitment_date = fields.Date(
        'Recruitment  Date',
        compute='_compute_recruitment_date'
    )
    company_cnas_id = fields.Many2one(
        'res.company.cnas',
        'Employer Number'
    )


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    recruitment_date = fields.Date(
        'Recruitment  Date',
        compute='_compute_recruitment_date'
    )
    company_cnas_id = fields.Many2one(
        'res.company.cnas',
        'Employer Number'
    )

    @api.depends('contract_ids')
    def _compute_recruitment_date(self):
        hrContract = self.env['hr.contract']
        for employee in self:
            domain = [
                ('employee_id', '=', employee.id),
                ('state', 'in', ('open', 'close'))
            ]
            contract = hrContract.search(domain, order="date_start ASC", limit=1)
            employee.recruitment_date = contract.date_start

    def _get_contracts(self, date_from, date_to, states=['open'], kanban_state=False):
        """
        Override this method to ignore contract dates when generating payslip batch
        """

        ignore = self._context.get('ignore_contract_date')
        valid_contract_ids = []

        if ignore:
            state_domain = [('state', 'in', states)]
            if kanban_state:
                state_domain = expression.AND([state_domain, [('kanban_state', 'in', kanban_state)]])

            for employee in self:
                nb_contract = employee.contracts_count
                if nb_contract > 1:
                    last_contract = self.env['hr.contract'].search([('id', 'in', employee.contract_ids.ids),
                                                                    ('state', '=', 'open')], order="date_start desc",
                                                                   limit=1)
                    valid_contract_ids.append(last_contract.id)
                else:
                    valid_contract_ids.append(employee.contract_id.id)

            valid_contracts = self.env['hr.contract'].search(
                expression.AND([[('id', 'in', valid_contract_ids)], state_domain]))

        else:
            valid_contracts = super(HrEmployee, self)._get_contracts(date_from, date_to, states=['open'],
                                                                     kanban_state=False)

        return valid_contracts
