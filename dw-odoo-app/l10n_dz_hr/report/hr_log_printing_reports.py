import datetime

from odoo import api, models, _
from odoo.exceptions import ValidationError


class HrContractEmployeePrintingLog(models.TransientModel):
    _name = 'report.l10n_dz_hr.hr_contract_with_bonus_report_template'
    _description = 'HR Contract Employee Printing Report Log'

    @api.model
    def _get_report_values(self, docids, data=None):
        action = {}

        for docid in docids:
            contract = self.env["hr.contract"].browse(docid)
            self.env["hr.employee.printing.log"].create(
                {
                    'name': contract.name,
                    'document': "Contract: " + contract.employee_id.first_name + " " + contract.employee_id.last_name,
                    'date': datetime.datetime.now(),
                    'source_employee': True
                }
            )
            action['doc_ids'] = docids
            action['doc_model'] = 'hr.contract'
            action['docs'] = contract
            action['report_type'] = data.get('report_type') if data else ''
        return action


class HrEmployeeAttestationPrintingLog(models.TransientModel):
    _name = 'report.l10n_dz_hr.hr_report_employment_attestation'
    _description = 'HR Employee Attestation Printing Report Log'

    @api.model
    def _get_report_values(self, docids, data=None):
        action = {}
        for docid in docids:
            attestation = self.env["hr.employee"].browse(docid)
            contract = self.env['hr.contract'].search([('employee_id', '=', attestation.id), ('state', '=', 'open')])

            if not contract:
                raise ValidationError(
                    _('You can not print this employment attestation, This employee has no ongoing contract.')
                )

            sequence = attestation.get_work_attestation_sequence(),
            attestation['last_report_sequence'] = sequence[0]

            self.env["hr.employee.printing.log"].create(
                {
                    'name': sequence[0],
                    'document': "Attestation: " + attestation.first_name + " " + attestation.last_name,
                    'date': datetime.datetime.now(),
                    'source_employee': True
                }
            )
            action['doc_ids'] = docids
            action['doc_model'] = 'hr.employee'
            action['docs'] = attestation
            action['report_type'] = data.get('report_type') if data else ''
        return action


class HrEmployeeCertificatePrintingLog(models.TransientModel):
    _name = 'report.l10n_dz_hr.hr_report_employment_certificate'
    _description = 'HR Employee Certification Printing Report Log'

    @api.model
    def _get_report_values(self, docids, data=None):
        action = {}
        for docid in docids:
            certification = self.env["hr.employee"].browse(docid)
            contract = self.env['hr.contract'].search([('employee_id', '=', certification.id), ('state', '=',  "open")])

            if contract:
                raise ValidationError(
                    _('You can not print this employment certificate, This employee has an ongoing contract.')
                )

            sequence = certification.get_work_certificate_sequence(),
            certification['last_report_sequence'] = sequence[0]

            self.env["hr.employee.printing.log"].create(
                {
                    'name': sequence[0],
                    'document': "Certification: " + certification.first_name + " " + certification.last_name,
                    'date': datetime.datetime.now(),
                    'source_employee': True
                }
            )
            action['doc_ids'] = docids
            action['doc_model'] = 'hr.employee'
            action['docs'] = certification
            action['report_type'] = data.get('report_type') if data else ''
        return action
