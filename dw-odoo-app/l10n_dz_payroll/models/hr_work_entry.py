# -*- encoding: utf-8 -*-
from odoo import fields, models


class HrWorkEntry(models.Model):
    _inherit = "hr.work.entry"

    absence_id = fields.Many2one(
        'hr.absence',
        string='Absence'
    )

    def _get_conflicting_work_entries(self):
        """
        get overlapping work entries
        Return hr.work.entry object
        """
        # Use the postgresql range type `tsrange` which is a range of timestamp
        # It supports the intersection operator (&&) useful to detect overlap.
        # use '()' to exlude the lower and upper bounds of the range.
        # Filter on date_start and date_stop (both indexed) in the EXISTS clause to
        # limit the resulting set size and fasten the query.
        self.ensure_one()
        self.flush(['date_start', 'date_stop', 'employee_id', 'active'])
        query = """
            SELECT b1.id
            FROM hr_work_entry b1
            WHERE
            b1.date_start <= %s
            AND b1.date_stop >= %s
            AND active = TRUE
            AND EXISTS (
                SELECT 1
                FROM hr_work_entry b2
                WHERE
                    b2.id = %s 
                    AND b2.date_start <= %s
                    AND b2.date_stop >= %s
                    AND active = TRUE
                    AND tsrange(b1.date_start, b1.date_stop, '()') && tsrange(b2.date_start, b2.date_stop, '()')
                    AND b1.id <> b2.id
                    AND b1.employee_id = b2.employee_id
            );
        """
        self.env.cr.execute(query, (self.date_stop, self.date_start, self.id, self.date_stop, self.date_start))
        conflicts = [res.get('id') for res in self.env.cr.dictfetchall()]
        return self.browse(conflicts)

