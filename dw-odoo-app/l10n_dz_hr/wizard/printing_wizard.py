# -*- coding:utf-8 -*-
from datetime import datetime

from odoo import models


class MaintenanceTaskStopWizard(models.TransientModel):
    _name = 'hr.employee.printing.wizard'
    _description = 'Hr employee printing management'

    def action_display_global_view(self):
        return self.env.ref('l10n_dz_hr.hr_report_employment_attestation'). \
            report_action(self)

    def action_submit(self, docids):
        action = {}
        for docid in docids:
            attestation = self.env["hr.employee"].browse(docid)
            self.env["hr.employee.printing.log"].create(
                {
                    'name': self.env.ref('l10n_dz_hr.sequence_hr_employment_certificate').next_by_id(),
                    'document': "Attestation: " + attestation.first_name + " " + attestation.last_name,
                    'date': datetime.datetime.now(),
                }
            )

        return self.action_display_global_view()
