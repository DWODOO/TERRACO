# -*- coding: utf-8 -*-
# Part of SMARTEST ALGERIA

# Import Odoo libs
import pdb

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    def _get_partner_id(self, credit_account):
        """
        Get partner_id of slip line to use in account_move_line
        """
        # use partner of salary rule or fallback on employee's address
        register_partner_id = self.salary_rule_id.register_id.partner_id
        partner_id = register_partner_id.id or self.slip_id.employee_id.address_home_id.id
        if credit_account:
            if register_partner_id or self.salary_rule_id.account_credit.internal_type in ('receivable', 'payable'):
                return partner_id
        else:
            if register_partner_id or self.salary_rule_id.account_debit.internal_type in ('receivable', 'payable'):
                return partner_id
        return False


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    date = fields.Date('Date Account', states={'draft': [('readonly', False)]}, readonly=True,
        help="Keep empty to use the period of the validation(Payslip) date.")

    @api.model
    def create(self, vals):
        return super(HrPayslip, self).create(vals)

    # @api.onchange('contract_id')
    # def onchange_contract(self):
    #     super(HrPayslip, self).onchange_contract()

    def action_payslip_cancel(self):
        return super(HrPayslip, self).action_payslip_cancel()

    def action_payslip_done(self):
        return super(HrPayslip, self).action_payslip_done()


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        'Analytic Account'
    )
    account_debit = fields.Many2one(
        'account.account',
        'Debit Account',
        domain=[('deprecated', '=', False)]
    )
    account_credit = fields.Many2one(
        'account.account',
        'Credit Account',
        domain=[('deprecated', '=', False)]
    )
    appear_on_move = fields.Boolean(
        'Appear on Move'
    )


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    journal_id = fields.Many2one(
        'account.journal',
        'Salary Journal', states={'draft': [('readonly', False)]},
        readonly=True,
        required=True,
        domain="[('type', '=', 'general')]",
        default=lambda self: self.env['account.journal'].search([('type', '=', 'general')], limit=1)
    )
    move_id = fields.Many2one(
        'account.move',
        'Accounting Entry',
        readonly=True,
        copy=False
    )
    test_move_id = fields.Many2one(
        'account.move',
        'Test Move',
        readonly=True,
        copy=False
    )

    def post_account_move(self):
        # Raise an exception if this Payslip is already accounted
        if self.move_id and self.move_id.state == 'posted':
            raise ValidationError(
                _("The Accounting Entry of this Payslip Batch is Already Posted")
            )

        # Retrieve payroll accounting configurations
        payroll_account_record = self.env.ref('smartest_hr_payroll_account.payroll_account_record')
        account_lines = payroll_account_record.line_ids.filtered(lambda p: p.active is True)

        # If no configuration found then do nothing and exit
        if not account_lines:
            return

        # Get Employees
        employee_ids = account_lines.get_employees().ids

        # Get Payslips Lines
        payslip_lines = self.slip_ids.filtered(lambda p: p.state == 'done' and p.employee_id.id in employee_ids).mapped('line_ids')
        # If no payslips line found then do nothing and exit
        if not payslip_lines:
            return

        # Get Payslips hidden Lines
        hidden_payslip_lines = self.slip_ids.filtered(
            lambda p: p.state == 'done' and p.employee_id.id in employee_ids
        ).mapped('hidden_line_ids')

        # Initialize variables
        lines = []
        lines_ext = []

        self.move_id.name = '/'
        self.move_id.unlink()
        move = self.env['account.move'].create({
            'move_type': 'entry',
            'date': fields.Date.today(),
            'is_payroll': True,
            'journal_id': self.journal_id.id,
            'ref': self.name
        })

        self.test_move_id.name = '/'
        self.test_move_id.unlink()
        test_move = self.env['account.move'].create({
            'move_type': 'entry',
            'date': fields.Date.today(),
            'is_payroll': True,
            'is_test': True,
            'journal_id': self.journal_id.id,
            'ref': self.name + ' TEST'
        })

        for account in account_lines:
            total = 0
            for line in payslip_lines:
                if line.salary_rule_id.id in account.salary_rule_ids.mapped('salary_rule_id').mapped('id') \
                        and line.employee_id.id in account.get_employees().ids:
                    if account.salary_rule_ids.filtered(lambda l: l.salary_rule_id.id == line.salary_rule_id.id).minus:
                        total -= abs(line.total)
                    else:
                        total += abs(line.total)
                    lines_ext.append({
                        'name': '',
                        'move_id': test_move.id,
                        'account_id': account.account_id.id,
                        'employee_id': line.employee_id.id,
                        'salary_rule_id': line.salary_rule_id.id,
                        'debit': round(abs(line.total), 2) if account.status == 'debit' else 0,
                        'credit': round(abs(line.total), 2) if account.status == 'credit' else 0,
                        'debit_test': round(line.total, 2) if account.status == 'debit' else 0,
                        'credit_test': round(line.total, 2) if account.status == 'credit' else 0,
                    })
            for line in hidden_payslip_lines:
                if line.salary_rule_id.id in account.salary_rule_ids.mapped('salary_rule_id').mapped('id') and line.employee_id.id in account.get_employees().ids:
                    if account.salary_rule_ids.filtered(lambda l: l.salary_rule_id.id == line.salary_rule_id.id).minus:
                        total -= abs(line.total)
                        amount = - round(abs(line.total), 2)
                    else:
                        total += abs(line.total)
                        amount = round(abs(line.total), 2)
                    lines_ext.append({
                        'name': '',
                        'move_id': test_move.id,
                        'account_id': account.account_id.id,
                        'employee_id': line.employee_id.id,
                        'salary_rule_id': line.salary_rule_id.id,
                        'debit': round(abs(line.total), 2) if account.status == 'debit' else 0,
                        'credit': round(abs(line.total), 2) if account.status == 'credit' else 0,
                        'debit_test': amount if account.status == 'debit' else 0,
                        'credit_test': amount if account.status == 'credit' else 0,
                    })

            if total > 0:
                lines.append({
                    'name': account.name,
                    'move_id': move.id,
                    'account_id': account.account_id.id,
                    'debit': round(total, 2) if account.status == 'debit' else 0,
                    'credit': round(total, 2) if account.status == 'credit' else 0,
                })

        if not lines:
            move.unlink()
            return

        credit = round(sum(p['credit'] for p in lines),2)
        debit = round(sum(p['debit'] for p in lines),2)
        if credit != debit:
            lines.append({
                'name': 'ERROR !!!',
                'move_id': move.id,
                'account_id': lines[0]['account_id'],
                'debit': round(abs(credit - debit), 2) if debit < credit else 0,
                'credit': round(abs(debit - credit), 2) if debit > credit else 0,
            })

        credit = round(sum(p['credit'] for p in lines_ext),2)
        debit = round(sum(p['debit'] for p in lines_ext),2)
        if credit != debit:
            credit_test = round(sum(p['credit_test'] for p in lines_ext), 2)
            debit_test = round(sum(p['debit_test'] for p in lines_ext), 2)
            lines_ext.append({
                'name': 'ERROR !!!',
                'move_id': test_move.id,
                'account_id': lines[0]['account_id'],
                'debit': round(abs(credit - debit),2) if debit < credit else 0,
                'credit': round(abs(debit - credit),2) if debit > credit else 0,
                'debit_test': round(credit_test - debit_test, 2) if debit_test < credit_test else 0,
                'credit_test': round(debit_test - credit_test, 2) if debit_test > credit_test else 0,
            })


        self.env['account.move.line'].create(lines)
        self.env['account.move.line'].create(lines_ext)
        self.move_id = move.id
        self.test_move_id = test_move.id

        action_data = self.sudo().env.ref('account.action_move_journal_line').read()[0]
        action_data['res_id'] = move.id
        action_data['view_mode'] = 'form,tree,kanban'
        action_data['view_id'] = self.env.ref('account.view_move_form').id

        return {
            'name': _('Invoice created'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'account.move',
            'view_id': self.env.ref('account.view_move_form').id,
            'target': 'current',
            'res_id': move.id,
        }
