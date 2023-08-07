# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA

# Import Odoo libs
from odoo import api, fields, models


class HrPayrollAccountVerifLine(models.TransientModel):
    _name = 'hr.payroll.account.verif.line'

    account_line_id = fields.Many2one(
        'payroll.account.line',
        string='Journal'
    )
    account_id = fields.Many2one(
        'account.account',
        string='Journal', related="account_line_id.account_id"
    )
    config_line_id = fields.Many2one(
        'payroll.account.rule_config',
        string='Config'
    )

    salary_rule_id = fields.Many2one(
        'hr.salary.rule', related="config_line_id.salary_rule_id",
        string='Salary Rules'
    )
    rule_minus = fields.Boolean(string="Minus", related="config_line_id.minus"
                                )
    account_name = fields.Char(related="account_line_id.name",
                               string="Account"
                               )
    name = fields.Char()
    total = fields.Float()
    status = fields.Selection(related="account_line_id.status"

                              )
    verif_id = fields.Many2one(
        'hr.payroll.account.verif',
    )


class HrPayrollAccountVerif(models.TransientModel):
    _name = 'hr.payroll.account.verif'

    payslip_run_id = fields.Many2one(
        'hr.payslip.run',
        string='Journal',
        required=True
    )
    date_start = fields.Date(
        string='From',
        related="payslip_run_id.date_start"
    )
    date_end = fields.Date(
        string='To',
        related="payslip_run_id.date_end"
    )
    verif_line_ids = fields.One2many(
        'hr.payroll.account.verif.line', 'verif_id',
        string='Lines'
    )

    @api.onchange('payslip_run_id')
    def action_verify(self):
        self.ensure_one()
        self.verif_line_ids=False
        slip_ids=self.payslip_run_id.slip_ids.filtered(lambda p: p.state == 'done')
        run_rules_ids = sorted(slip_ids.line_ids.salary_rule_id, key=lambda x: x["sequence"])
        data = []
        AccountLine = self.env['payroll.account.line']
        id = self.id
        for rule in run_rules_ids:
            account_line_id = AccountLine.search([('salary_rule_ids.salary_rule_id.id', '=', rule.id)])
            total = sum(slip_ids.line_ids.filtered(lambda line: line.salary_rule_id.id == rule.id).mapped("total"))
            if not account_line_id:
                data.append({
                    'name': rule.name,
                    'verif_id': id,
                    'total': total,
                })
            else:
                for account in account_line_id:
                    config_line_id = account.salary_rule_ids.filtered(
                        lambda config: config.salary_rule_id.id == rule.id)
                    for config in config_line_id:
                        data.append({
                            'account_line_id': account.id,
                            'name': rule.name,
                            'config_line_id': config.id,
                            'verif_id': id,
                            'total': total,

                        })
        self.env['hr.payroll.account.verif.line'].create(data)
