# -*- encoding: utf-8 -*-

# Python libs
import logging
import pdb

import pytz

# Odoo libs
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import date_utils

# Global variables
_logger = logging.getLogger(__name__)


class HrContributionRegister(models.Model):
    _name = "hr.contribution.register"
    _inherit = ['mail.thread', 'mail.activity.mixin']

class HrAbsence(models.Model):
    _name = "hr.absence"
    _description = "Employee Absence"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_work_entry_type_id(self):
        return self.env.ref('l10n_dz_payroll.hr_absence_work_entry', False)

    name = fields.Char(
        'Name',
        readonly=True,
        store=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee',
        required=True,
        readonly=True,
        store=True,
        states={'draft': [('readonly', False)]},
    )
    date_from = fields.Datetime(
        'Start Date',
        readonly=True,
        store=True,
        required=True,
        states={'draft': [('readonly', False)]},
    )
    date_to = fields.Datetime(
        'To Date',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
    )
    duration = fields.Float(
        'Duration',
        required=True,
        readonly=True,
        store=True,
        states={'draft': [('readonly', False)]},
    )
    duration_type = fields.Selection([
        ('days', 'Days'),
        ('hours', 'Hours'),
    ],
        string='Type',
        default='days',
        required=True,
        readonly=True,
        store=True,
        states={'draft': [('readonly', False)]},
    )
    work_entry_type_id = fields.Many2one(
        'hr.work.entry.type',
        default=_default_work_entry_type_id,
        required=True,
        readonly=True,
        store=True,
        states={'draft': [('readonly', False)]},
    )
    work_entry_ids = fields.One2many(
        'hr.work.entry',
        'absence_id',
        string='Work entries'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled'),
    ],
        string='State',
        default='draft',
        readonly=True,
        store=True,
    )
    description = fields.Text(
        'Description',
    )

    @api.constrains('date_from', 'date_to')
    def _check_absence_conflict(self):
        for absence in self:
            conflict_absence = absence._get_conflict_absence()
            if conflict_absence:
                raise ValidationError(
                    _("Absence for the same employee are already exist on the same period")
                )

    @api.onchange('date_from', 'date_to', 'duration_type')
    def _onchange_date(self):
        if self.date_from and self.date_to:
            dt = self.date_to - self.date_from
            # dt = abs((self.date_to.date() - self.date_from.date()).days)
            if self.duration_type == 'days':
                self.duration = abs((self.date_to.date() - self.date_from.date()).days)
            else:
                self.duration = dt.total_seconds() / 60 / 60 / 3

    def _prepare_work_entries_vals(self):
        """
        :return: Values of hr.work.entry object as list of dicts
        """
        self.ensure_one()

        # Get the valid contract depends on period. If not found do nothing
        contracts = self.employee_id._get_contracts(self.date_from, self.date_to)
        if not contracts:
            return []

        # Initialize variables
        contract = contracts[0]
        employee = self.employee_id
        calendar = contract.resource_calendar_id
        resource = employee.resource_id
        tz = pytz.timezone(calendar.tz)
        default_work_entry_type = contract.structure_type_id.default_absence_work_entry_type_id
        work_entry_type_id = self.work_entry_type_id or default_work_entry_type
        absence_vals = []

        # Get absences intervals according to working calendar
        absences_intervals = calendar._work_intervals_batch(
            pytz.utc.localize(self.date_from) if not self.date_from.tzinfo else self.date_from,
            pytz.utc.localize(self.date_to) if not self.date_to.tzinfo else self.date_to,
            resources=[resource],
            tz=tz
        )[resource.id]
        # Absences
        for interval in absences_intervals:
            # All benefits generated here are using datetimes converted from the employee's timezone
            absence_vals += [{
                'name': "%s: %s" % (work_entry_type_id.name, employee.name),
                'date_start': interval[0].astimezone(pytz.utc).replace(tzinfo=None),
                'date_stop': interval[1].astimezone(pytz.utc).replace(tzinfo=None),
                'work_entry_type_id': work_entry_type_id.id,
                'employee_id': employee.id,
                'contract_id': contract.id,
                'absence_id': self.id,
                'company_id': contract.company_id.id,
                'state': 'draft',
            }]

        # return
        return absence_vals

    def _generate_work_entries(self):
        # Get the valid contract depends on period. If not found do nothing
        contracts = self.employee_id._get_contracts(self.date_from, self.date_to)
        if not contracts:
            return []

        # Initialize variables
        contract = contracts[0]
        absence_vals = []
        WorkEntry = self.env['hr.work.entry']

        # Collect all absences work entries values
        for absence in self:
            # If work entries are not yet created for this absence then create them
            if not absence.work_entry_ids:
                absence_vals += absence._prepare_work_entries_vals()

        # Generate work entries
        min_date_from = min([fields.Date.to_date(absence.date_from) for absence in self])
        max_date_to = max([fields.Date.to_date(absence.date_to) for absence in self])
        contract._generate_work_entries(min_date_from, max_date_to)

        # Create Work entries
        absence_work_entry_ids = WorkEntry.create(absence_vals)

        # Resolve conflict
        for entry in absence_work_entry_ids:
            WorkEntry.search([
                ('employee_id', '=', entry.employee_id.id),
                ('id', '!=', entry.id),
                ('date_start', '>=', entry.date_start),
                ('date_stop', '<=', entry.date_stop),
            ]).unlink()
            # entry._get_conflicting_work_entries().unlink()

        # Return
        return absence_work_entry_ids

    def _get_conflict_absence(self):
        """
        :return: A hr.absence objects that are in conflict with the self Absence
        """
        self.ensure_one()
        domain = [
            '&',
            ('id', '!=', self.id),
            '&',
            ('employee_id', '=', self.employee_id.id),
            '|',
            '&',
            ('date_from', '>=', self.date_from),
            ('date_from', '<=', self.date_to),
            '&',
            ('date_to', '>=', self.date_from),
            ('date_to', '<=', self.date_to),
            ('state', 'in', ['draft', 'done'])
        ]
        conflict_absence = self.env['hr.absence'].search(domain)
        return conflict_absence

    def action_confirm(self):
        # Check if no draft absence will be confirmed. If yes, raise an error
        if self.filtered(lambda absence: absence.state != 'draft'):
            raise ValidationError(
                _('Only draft Absences can be confirmed')
            )

        # Generate the related work entries
        work_entries = self._generate_work_entries()

        # Log warning if no work entry is created
        if not work_entries:
            _logger.warning(
                _("No work entry is generated for those absences: %s" % ', '.join(self.mapped('name')))
            )

        # Edit state -> 'confirm'
        self.write({
            'state': 'confirm'
        })

    def action_cancel(self):
        # Check if no confirmed absence will be canceled. If yes, raise an error
        if self.filtered(lambda absence: absence.state != 'confirm'):
            raise ValidationError(
                _('Only confirmed Absences can be cancelled')
            )

        # Edit state -> 'cancel'
        self.write({
            'state': 'cancel'
        })

    def unlink(self):
        if self.filtered(lambda absence: absence.state in ('confirm')):
            raise ValidationError(
                _('Only draft Absences can be deleted')
            )
        return super(HrAbsence, self).unlink()

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            sequence = self.env.ref('l10n_dz_payroll.hr_absence_sequence', False)
            if sequence:
                vals['name'] = sequence.next_by_id()
        return super(HrAbsence, self).create(vals)
