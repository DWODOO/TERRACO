# -*- coding:utf-8 -*-
from odoo import api, Command, fields, models, _


class SmartestMasse(models.Model):
    _name = 'masse.salariale'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Masse Salariale'

    reference = fields.Char(
        'Référence',
        required=True,
        tracking=True,
        readonly=True,
        default=lambda self: _('New'))
    name = fields.Char(
        '',
        required=True
    )
    company_id = fields.Many2one('res.company',
                                 required=True,
                                 default=lambda self: self.env.company
                                 )
    date = fields.Date(
        'Date',
        required=True,
        index=True,
        default=fields.Date.context_today
    )
    date_begin = fields.Datetime(
        'Start Date',
        tracking=True,
        required=True
    )
    date_end = fields.Datetime(
        'End Date',
        tracking=True,
        required=True
    )
    masse_type = fields.Selection([
        ('employee', 'Employee'),
        ('department', 'Departement'),
        ('post', 'Poste'),
        ('CSP', 'CSP'),
    ], required=True)
    state = fields.Boolean(
        '',
        default=False)
    masse_line_ids = fields.One2many(
        'masse.salariale.line',
        'masse_id'
    )

    def calculate_masse(self, type, model, attribute_id):
        values = []
        department = self.env[model].search([])
        for dep in department:
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', self.date_begin), ('date_to', '<=', self.date_end),
                 ('company_id', '=', self.company_id.id), (attribute_id, '=', dep.id)])
            somme_initial = 0
            somme_global = 0
            for payslip in payslips:

                somme_initial += payslip.smartest_payroll_init
                somme_global += payslip.payroll

            val = Command.create({
                type: dep.id,
                'masse_salariale': somme_initial,
                'masse_salariale_global': somme_global,
            })

            values.append(val)
        self.write({
            'masse_line_ids': values,
        })

    def create_lines(self):
        self.state = True
        if self.masse_type == 'CSP':
            csp = self.env['hr.socioprofessional.categories.levels'].search([])
            values = []

            for rec in csp:
                payslips = self.env['hr.payslip'].search(
                    [('date_from', '>=', self.date_begin), ('date_to', '<=', self.date_end),
                     ('company_id', '=', self.company_id.id), ('csp_cat.id', '=', rec.id)])

                somme_global = 0
                somme_initial = 0
                for payslip in payslips:

                    somme_initial += payslip.smartest_payroll_init
                    somme_global += payslip.payroll
                    val = Command.create({
                        'employee_id': payslip.employee_id.id,
                        'masse_salariale': somme_initial,
                        'masse_salariale_global': somme_global,
                    })
                    values.append(val)
            self.write({
                'masse_line_ids': values,
            })

        if self.masse_type == 'employee':
            payslips = self.env['hr.payslip'].search(
                [('date_from', '>=', self.date_begin), ('date_to', '<=', self.date_end),
                 ('company_id', '=', self.company_id.id)])
            employees = payslips.employee_id
            values = []
            for emp in employees:

                employee_payslips = payslips.filtered(
                    lambda payslip: payslip.employee_id.id == emp.id)

                somme_global = 0
                somme_initial = 0
                for payslip in employee_payslips:
                    somme_initial += payslip.smartest_payroll_init
                    somme_global += payslip.payroll
                    val = Command.create({
                        'employee_id': payslip.employee_id.id,
                        'masse_salariale': somme_initial,
                        'masse_salariale_global': somme_global,
                    })
                    values.append(val)
            self.write({
                'masse_line_ids': values,
            })
        if self.masse_type == 'department':
            self.calculate_masse('department_id', 'hr.department', 'department_id.id')

        if self.masse_type == 'post':
            self.calculate_masse('job_id', 'hr.job', 'job_id.id')

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('masse.sal') or _(
                'New')
        result = super(SmartestMasse, self).create(vals)
        return result


class SmartestMasseLine(models.Model):
    _name = 'masse.salariale.line'

    employee_id = fields.Many2one('hr.employee')
    department_id = fields.Many2one('hr.department')
    job_id = fields.Many2one('hr.job')
    csp_id = fields.Many2one('hr.socioprofessional.categories.levels')
    company_currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='masse_id.company_id.currency_id',
        readonly=True,
    )
    masse_salariale = fields.Monetary(
        'Masse salariale Initial',
        currency_field="company_currency_id",

    )
    masse_salariale_global = fields.Monetary(
        'Masse salariale Global',
        currency_field="company_currency_id",

    )
    masse_id = fields.Many2one('masse.salariale', string='Emplacement')
