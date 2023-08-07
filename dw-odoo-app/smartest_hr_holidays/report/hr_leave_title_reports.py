import datetime

from odoo import api, models, _
from odoo.exceptions import ValidationError


class HrLeaveEmployeePrintingLog(models.TransientModel):
    _name = 'report.smartest_hr_holidays.hr_report_leave_title_parent'
    _description = 'HR Leave Title'


    def _get_report_values(self, docids, data=None):

        # get the report action back as we will need its data
        report = self.env['ir.actions.report']._get_report_from_name(
            'smartest_hr_holidays.hr_report_leave_title_parent')

        # get the records selected for this rendering of the report
        docs = self.env[report.model].browse(docids)

        for doc in docs:

            if doc.state not in ["validate","done"]:
                raise ValidationError(
                    _('You can not print this report')
                )
            # return a custom rendering context
            return {
                'doc_ids': docids,
                'doc_model': report.model,
                'data': data,
                'docs': docs,
            }



