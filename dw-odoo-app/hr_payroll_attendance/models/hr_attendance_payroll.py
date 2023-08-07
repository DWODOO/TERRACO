from odoo import api, fields, models, _, Command
from datetime import datetime
from datetime import timedelta


class HrAttendancePayroll(models.Model):
    _name = 'smartest.hr_attendance.payroll'
    _description = 'Chargement presences et absences des employees'


    state = fields.Selection([
        ('draft', 'Draft'),
        ('loaded', 'loaded'),
        ('prestation', 'Prestation')
    ], default='draft', string="State", readonly=True, tracking=True)

    bool = fields.Boolean(default=False)

    check = fields.Boolean(default=False)
    prestation_check = fields.Boolean(default=False)

    date = fields.Date(default=fields.date.today(),required=True)

    attendance_payroll_ids = fields.One2many('smartest.hr_attendance.payroll.list','attendance_payroll_id')

    _sql_constraints = [
        (
            'Date_Unique',
            'UNIQUE(date)',
            'date exists !'
        ),
    ]

    def action_loaded(self):
        for record in self:
            record.state = "loaded"

    def action_prestation(self):
        for record in self:
            record.state = "prestation"


    @api.constrains("attendance_payroll_ids")
    def charger_paie(self):
        heure_absence_legal = self.env['ir.config_parameter'].get_param('hr_attendance.nombre_heure_present_journee')
        prestation = self.env['hr.work.entry']
        contract_ids = self.env['hr.contract']
        dict ={}
        pres_ids = []
        i=1
        attendance_ids = self.env['hr.attendance']
        for rec in self.attendance_payroll_ids:
            print(rec.type_prestation)
            if rec.abs_days or float(rec.abs_hours) > float(heure_absence_legal):
                self.check = True
            if float(rec.abs_hours) > 0:
                prestation.search([]).filtered(
                    lambda o: o if o.employee_id == rec.employee_id and o.date_start.date() == self.date else None).unlink()
                date_stp =  rec.check_in+ timedelta(hours=rec.worked_hours)
                print(date_stp)
                prestation.create(
                    {'name':rec.employee_id.name,
                     'employee_id': rec.employee_id.id,
                     'work_entry_type_id': 1,
                     'state': 'draft',
                     'date_start': rec.check_in,
                     'date_stop': date_stp,
                     'duration': False,
                     }
                )
                date_stp_retard = date_stp + timedelta(hours=rec.abs_hours)
                prestation.create(
                    {'name': rec.employee_id.name,
                     'employee_id': rec.employee_id.id,
                     'work_entry_type_id': rec.type_prestation.id,
                     'state': 'draft',
                     'date_start': date_stp,
                     'date_stop': date_stp_retard,
                     'duration': False,
                     }
                )
            if rec.abs_days >0:
                prestation_ids = prestation.search([]).filtered(
                    lambda o: o if o.employee_id == rec.employee_id and o.date_start.date() == self.date else None)

                for pres in prestation_ids:
                    pres.write(
                        {
                         'work_entry_type_id': rec.type_prestation.id,
                         }
                    )
                print(prestation_ids)
        self.prestation_check=True
        self.action_prestation()





    def get_default_data(self):
        # res = super(HrAttendancePayroll, self).default_get(fields_list)
        pres_ids = []
        line = {}
        heure_absence_legal = self.env['ir.config_parameter'].get_param('hr_attendance.nombre_heure_present_journee')

        attendance_ids = self.env['hr.attendance']
        contract_ids = self.env['hr.contract']
        pres_abs_ids = self.env['smartest.hr_attendance.payroll.list']
        resultat_rec = self.env['hr.employee'].search([('inclus_presence','=',False)])
        for result in resultat_rec:
            attendance = attendance_ids.search([],order = 'check_in').filtered(
                 lambda o: o if o.employee_id == result and o.check_in.date() == self.date else None)
            contract = contract_ids.search([]).filtered(
                 lambda o: o if o.employee_id == result else None).resource_calendar_id.hours_per_day
            check_in = attendance.mapped("check_in")
            i=0
            if check_in:
                for check in check_in:
                    rec = check
                    i=+1
                    if i==1:
                        break


            present = sum(attendance.mapped("worked_hours"))
            if present:
                if present > contract:
                    line = Command.create(
                            {'employee_id': result.id,
                             'worked_hours': contract,
                             'date_presence':self.date,
                             'check_in':rec,
                             'abs_days':0,
                             'abs_hours':0,
                             'justification': "",
                             'type_prestation':"",
                             }
                            )
                    pres_ids.append(line)
                else:
                    if present < contract:
                        retard = contract - present
                        line = Command.create(
                            {'employee_id': result.id,
                             'worked_hours': sum(attendance.mapped("worked_hours")),
                             'date_presence': self.date,
                             'check_in': rec,
                             'abs_days': 0,
                             'abs_hours': retard,
                             'justification': "",
                             'type_prestation': "",
                             }
                        )
                        pres_ids.append(line)
            else:
                line = Command.create(
                    {'employee_id': result.id,
                     'worked_hours': 0,
                     'date_presence': self.date,
                     'check_in':False,
                     'abs_days': 1,
                     'abs_hours': 0,
                     'justification': "",
                     'type_prestation': False,
                     }
                )
                pres_ids.append(line)
            # pres_ids.append(line)
         
        self.write({
            "attendance_payroll_ids": pres_ids
        })
        self.bool=True
        self.action_loaded()





class HrAttendancePayrollList(models.Model):
    _name = 'smartest.hr_attendance.payroll.list'

    attendance_payroll_id = fields.Many2one('smartest.hr_attendance.payroll')
    employee_id = fields.Many2one('hr.employee',readonly=True)
    date_presence = fields.Date(string="date")
    worked_hours = fields.Float()
    abs_days = fields.Integer()
    abs_hours = fields.Float(string="temps d'absence")
    justification = fields.Char(string="Justification d'absence")
    type_prestation = fields.Many2one('hr.work.entry.type')
    check_in =fields.Datetime()



class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    presence_id = fields.Many2one('smartest.hr_attendance.payroll')

class HrResConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    nombre_heure_present_journee = fields.Char(string="Nombre d'heures Present / Jours")

    @api.model
    def get_values(self):
        res = super(HrResConfig, self).get_values()

        ICPsudo = self.env['ir.config_parameter'].sudo()
        heure_abs = ICPsudo.get_param('hr_attendance.nombre_heure_present_journee')
        res.update(
            nombre_heure_present_journee = heure_abs,
        )
        return res


    def set_values(self):
        res = super(HrResConfig, self).set_values()
        self.env['ir.config_parameter'].set_param('hr_attendance.nombre_heure_present_journee', self.nombre_heure_present_journee)
        return res

class hr_employee_presence(models.Model):
    _inherit = 'hr.employee'

    inclus_presence = fields.Boolean()
    pres_employee_id = fields.Many2one('smartest.hr_attendance.payroll')

class HREmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    inclus_presence = fields.Boolean()
    pres_employee_id = fields.Many2one('smartest.hr_attendance.payroll')


class HrWorkEntries(models.Model):
    _inherit='hr.work.entry'



