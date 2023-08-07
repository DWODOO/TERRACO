
from odoo import models, fields, api, _




class RessourceCalendar(models.Model):
    _inherit = 'resource.calendar'


    def extract_day_of(self):
        days=[]
        all_days=[]
        for rec in self:
            for attendance in rec.attendance_ids:
                days.append(attendance.dayofweek)
        for i in range(7):
            all_days.append(str(i))
        days_off = list(set(all_days) - set(days))
        return days_off
