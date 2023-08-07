# -*- coding:utf-8 -*-
import pdb

from dateutil.relativedelta import relativedelta
from num2words import num2words
import datetime
import re

from odoo.tools.misc import get_lang
from odoo.osv import expression
from odoo.exceptions import ValidationError
from odoo import api, fields, models, _

MONTH_PER_YEAR = 12
WEEK_PER_YEAR = 52
DEFAULT_HOURS_PER_MONTH = 173.33
DEFAULT_DAYS_PER_MONTH = 0
DAYS_PER_WEEK = 7
DAYS_PER_MONTH = 30
WEEKS_PER_MONTH = 4


class Contract(models.Model):
    _inherit = 'hr.contract'

    hours_per_month = fields.Float(
        string='Work hours / month',
        # track_visibility='always',
        default=DEFAULT_HOURS_PER_MONTH,
        tracking=True
    )
    days_per_month = fields.Integer(
        string='Work days / month',
        # track_visibility='always',
        default=DEFAULT_DAYS_PER_MONTH,
        tracking=True
    )
    nature = fields.Selection(
        [
            ('contract', 'New Contract'),
            ('amendment', 'Contract amendment ')
        ],
        'Nature',
        # track_visibility='always',
        required=True,
        default='contract',
        copy=False,
        tracking=True
    )
    first_contract_date = fields.Date(
        'First contract start date',
        default=fields.Date.today,
        store=True,
        compute='_compute_first_contract_date',
        tracking=True
    )

    leave = fields.Boolean(
        'Leave ?',
        # track_visibility='always',
        readonly=False,

        tracking=True
    )
    stc_state = fields.Boolean(
        'STC done ?',
        # track_visibility='always',
        readonly=False,

        tracking=True
    )
    leave_date = fields.Date(
        'Leaving date',
        # track_visibility='always',
        readonly=False,

        tracking=True
    )
    leave_reason = fields.Char(
        'Leaving reason',
        # track_visibility='always',
        readonly=False,

        tracking=True
    )
    leave_notice = fields.Integer(
        'Leave notice',
        # track_visibility='always',
        tracking=True
    )
    use_contract_sequence = fields.Boolean(
        related='company_id.use_contract_sequence'
    )
    name = fields.Char(
        'Contract Reference',
        required=True,
        copy=False,
        tracking=True
    )
    pre_wage = fields.Monetary(
        string='Pre salary',
        currency_field="company_currency",
        tracking=True
    )
    # ------------------------------------- Payroll rules fields ---------------------------------------------------
    company_currency = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',

        tracking=True
    )
    allowance_responsibility_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Responsibility allowance Paid in',
        default='calendar',
        tracking=True
    )
    allowance_responsibility_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'Responsibility allowance type',
        default='amount',
        tracking=True
    )
    allowance_responsibility_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'Responsibility Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_responsibility = fields.Float(
        'Responsibility Allowance',
        
        tracking=True
    )
    allowance_clothing = fields.Float(
        'Clothing Allowance',
        
        tracking=True
    )
    allowance_clothing_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Clothing allowance Paid in',
        default='ouverable',
        tracking=True
    )
    allowance_clothing_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'Clothing allowance type',
        default='amount',
        tracking=True
    )
    allowance_clothing_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'Clothing Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_cash = fields.Float(
        'Cash Allowance',
        
        tracking=True
    )
    allowance_cash_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Cash allowance Paid in',
        default='calendar',
        tracking=True
    )
    allowance_cash_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'Cash allowance type',
        default='amount',
        tracking=True
    )
    allowance_cash_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'Cash Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_isp = fields.Float(
        'P.S.A',
        help='Permanent Service Allowance',
        tracking=True
    )
    allowance_isp_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'I.S.P allowance Paid in',
        default='calendar',
        tracking=True
    )
    allowance_isp_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'I.S.P allowance type',
        default='percentage',
        tracking=True
    )
    allowance_isp_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'I.S.P Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_in_iep = fields.Float(
        'P.E.A (In company)',
        help='Professional Experience Allowance within the company',
        tracking=True
    )
    allowance_in_iep_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'IEP IN allowance Paid in',
        default='calendar',
        tracking=True
    )
    allowance_in_iep_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'IEP IN allowance type',
        default='percentage',
        tracking=True
    )
    allowance_in_iep_dependency = fields.Selection(
        [('non_abs_non_leave', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'IEP IN Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_out_iep = fields.Float(
        'P.E.A (Out of company)',
        help='Professional Experience Allowance out of the company',
        tracking=True
    )
    allowance_out_iep_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'IEP OUT allowance PAid in',
        default='calendar',
        tracking=True
    )
    allowance_out_iep_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'IEP OUT allowance type',
        default='percentage',
        tracking=True
    )
    allowance_out_iep_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'IEP OUT Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_pri = fields.Float(
        'Individual Performance Allowance',
        
        tracking=True
    )
    allowance_pri_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'PRI allowance PAID in',
        default='ouverable',
        tracking=True
    )
    allowance_pri_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'PRI allowance type',
        default='percentage',
        tracking=True
    )
    allowance_pri_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'PRI Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_icr = fields.Float(
        'S.I.A',
        help='Supplementary Income Allowance',
        
        tracking=True
    )
    allowance_icr_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'ICR allowance Paid in',
        default='ouverable',
        tracking=True
    )
    allowance_icr_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'ICR allowance type',
        default='percentage',
        tracking=True
    )
    allowance_icr_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'ICR Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_technicality = fields.Float(
        'Technicality Allowance',
        
        tracking=True
    )
    allowance_technicality_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Technicality allowance Paid in',
        default='calendar',
        tracking=True
    )
    allowance_technicality_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'Technicality allowance type',
        default='amount',
        tracking=True
    )
    allowance_technicality_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'Technicality Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_isolated_area = fields.Float(
        'Isolated Area Allowance',
        
        tracking=True
    )
    allowance_isolated_area_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Isolated Area allowance Paid in',
        default='ouverable',
        tracking=True
    )
    allowance_isolated_area_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'Isolated Area allowance type',
        default='amount',
        tracking=True
    )
    allowance_isolated_area_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'Isolated Area Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_nuisance = fields.Float(
        'Nuisance Allowance',
        tracking=True
    )
    allowance_nuisance_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Nuisance allowance Paid in',
        default='calendar',
        tracking=True
    )
    allowance_nuisance_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'Nuisance allowance type',
        default='percentage',
        tracking=True
    )
    allowance_nuisance_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'Nuisance Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_availability = fields.Float(
        'Availability Allowance',
        
        tracking=True
    )
    allowance_availability_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Availability allowance Paid in',
        default='ouverable',
        tracking=True
    )
    allowance_availability_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'Availability allowance type',
        default='percentage',
        tracking=True
    )
    allowance_availability_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'Availability Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_soiling = fields.Float(
        'Performance Allowance',
        
        tracking=True
    )
    allowance_soiling_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Performance allowance Paid in',
        default='calendar',
        tracking=True
    )
    allowance_soiling_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'Performance allowance type',
        default='percentage',
        tracking=True
    )
    allowance_soiling_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'Performance Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_meal = fields.Float(
        'Meal Allowance',
        
        tracking=True
    )
    allowance_meal_type = fields.Selection(
        [(
            'day', 'Day'),
            ('month', 'Month'),
        ],
        'Meal allowance type',
        default='day',
        tracking=True
    )
    allowance_meal_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Meal allowance Paid in',
        default='ouverable',
        tracking=True
    )
    allowance_transportation = fields.Float(
        'Transportation Allowance',
        
        tracking=True
    )
    allowance_transportation_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Transportation allowance Paid in',
        default='ouverable',
        tracking=True
    )
    allowance_vehicle = fields.Float(
        'Vehicle Allowance',
        
        tracking=True
    )
    allowance_vehicle_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Vehicle allowance Paid in',
        default='ouverable',
        tracking=True
    )
    allowance_vehicle_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'Vehicle allowance type',
        default='amount',
        tracking=True
    )
    allowance_vehicle_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'Vehicle Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_travel = fields.Float(
        'Travel Allowance',
        
        tracking=True
    )
    allowance_travel_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Travel allowance Paid in',
        default='ouverable',
        tracking=True
    )
    allowance_travel_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'Travel allowance type',
        default='amount',
        tracking=True
    )
    allowance_travel_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'Travel Dependency type',
        default='non_abs',
        tracking=True
    )
    allowance_rent = fields.Float(
        'Rent Allowance',
        
        tracking=True
    )
    allowance_rent_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Rent allowance Paid in',
        default='ouverable',
        tracking=True
    )
    allowance_rent_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'Rent allowance type',
        default='amount',
        tracking=True
    )
    allowance_rent_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'Rent Dependency type',
        default='non_abs',
        tracking=True
    )
    allowance_refund_rent = fields.Float(
        'Refund Rent Allowance',
        
    )
    allowance_refund_rent_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Refund Rent allowance Paid in',
        default='ouverable',
        tracking=True
    )
    allowance_refund_rent_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'Refund Rent allowance type',
        default='amount',
        tracking=True
    )
    allowance_refund_rent_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'Refund Rent Dependency type',
        default='non_abs',
        tracking=True
    )
    allowance_transportation_type = fields.Selection(
        [
            ('day', 'Day'),
            ('month', 'Month'),
        ],
        'Transportation allowance type',
        default='day',
        tracking=True
    )

    allowance_phone = fields.Float(
        'Phone Allowance',
        
        tracking=True
    )
    allowance_phone_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Phone allowance Paid in',
        default='ouverable',
        tracking=True
    )
    allowance_phone_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'Phone allowance type',
        default='amount',
        tracking=True
    )
    allowance_phone_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'Phone Dependency type',
        default='non_abs',
        tracking=True
    )
    allowance_unique_salary = fields.Float(
        'Unique Salary Allowance',
        
        tracking=True
    )
    allowance_unique_salary_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Unique Salary  allowance type',
        default='ouverable',
        tracking=True
    )
    allowance_unique_salary_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'Unique Salary allowance type',
        default='amount',
        tracking=True
    )
    allowance_unique_salary_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'Unique Salary  Dependency type',
        default='non_abs',
        tracking=True
    )
    allowance_pop = fields.Float(
        'P.O.P',
        
        tracking=True
    )
    allowance_pop_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'P.O.P allowance Paid in',
        default='calendar',
        tracking=True
    )
    allowance_pop_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'P.O.P allowance type',
        default='percentage',
        tracking=True
    )
    allowance_pop_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'P.O.P Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_pap = fields.Float(
        'P.A.P',
        
        tracking=True
    )
    allowance_pap_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'P.A.P allowance Paid in',
        default='calendar',
        tracking=True
    )
    allowance_pap_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'P.A.P allowance type',
        default='percentage',
        tracking=True
    )
    allowance_pap_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'P.A.P Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_hse = fields.Float(
        'H.S.E',
        
        tracking=True
    )
    allowance_hse_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'H.S.E allowance Paid in',
        default='calendar',
        tracking=True
    )
    allowance_hse_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'H.S.E allowance type',
        default='percentage',
        tracking=True
    )
    allowance_hse_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'H.S.E Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_iff = fields.Float(
        'I.F.F',
        
        tracking=True
    )
    allowance_iff_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'I.F.F allowance Paid in ',
        default='calendar',
        tracking=True
    )
    allowance_iff_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'I.F.F allowance type',
        default='percentage',
        tracking=True
    )
    allowance_iff_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'I.F.F Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_ifsp = fields.Float(
        'I.F.S.P',
        
        tracking=True
    )
    allowance_ifsp_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'I.F.S.P allowance Paid in',
        default='calendar',
        tracking=True
    )
    allowance_ifsp_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'I.F.S.P allowance type',
        default='percentage',
        tracking=True
    )
    allowance_ifsp_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'I.F.S.P Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_itp = fields.Float(
        'I.T.P',
        
        tracking=True
    )
    allowance_itp_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'I.T.P allowance Paid in',
        default='calendar',
        tracking=True
    )
    allowance_itp_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'I.T.P  allowance type',
        default='percentage',
        tracking=True
    )
    allowance_itp_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'I.T.P Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_risk = fields.Float(
        'Risk Allowance',
        
        tracking=True
    )
    allowance_risk_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Risk allowance Paid in',
        default='calendar',
        tracking=True
    )
    allowance_risk_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'Risk allowance type',
        default='amount',
        tracking=True
    )
    allowance_risk_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'Risk Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_master_apprentice = fields.Float(
        'Master Apprentice Allowance',
        
        tracking=True
    )
    allowance_master_apprentice_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Master Apprentice allowance Paid in',
        default='calendar',
        tracking=True
    )
    allowance_master_apprentice_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'Master Apprentice allowance type',
        default='amount',
        tracking=True
    )
    allowance_master_apprentice_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'Master Apprentice Dependency type',
        default='abs_leave',
        tracking=True
    )
    allowance_mutuel = fields.Float(
        'Mutuel Restrained',
        
        tracking=True
    )
    allowance_mutuel_paid_in = fields.Selection(
        [('ouverable', 'Ouverable'), ('calendar', 'Calendrier'),
         ],
        'Mutuel allowance type',
        default='ouverable',
        tracking=True
    )
    allowance_mutuel_type = fields.Selection(
        [('percentage', 'Percentage'), ('amount', 'Amount'),
         ],
        'allowance type',
        default='amount',
        tracking=True
    )
    allowance_mutuel_dependency = fields.Selection(
        [('non_abs', 'Ne dépend pas des Abs'), ('abs_leave', 'Dépend des abs'),
         ],
        'Dependency type',
        default='non_abs',
        tracking=True
    )
    period_count_text = fields.Char(
        compute='_compute_period_count_text',
        tracking=True
    )
    trial_period_count_text = fields.Char(
        compute='_compute_period_count_text',
        tracking=True
    )
    leave_notice_text = fields.Char(
        compute='_compute_leave_notice_text',
        tracking=True
    )
    #  Inherited fields
    state = fields.Selection(
        selection_add=[
            ('amendment', 'Has Amendment')
        ],
        tracking=True
    )
    parent_contract_id = fields.Many2one(
        'hr.contract',
        'Parent contract',
        tracking=True
    )
    structure_type_id = fields.Many2one(
        tracking=True
    )
    department_id = fields.Many2one(
        tracking=True
    )
    job_id = fields.Many2one(
        tracking=True
    )
    trial_date_end = fields.Date(
        tracking=True
    )
    resource_calendar_id = fields.Many2one(
        tracking=True
    )
    contract_wage = fields.Monetary(
        tracking=True
    )
    company_id = fields.Many2one(
        tracking=True
    )
    contract_type_id = fields.Many2one(
        tracking=True
    )
    currency_id = fields.Many2one(
        tracking=True
    )
    permit_no = fields.Char(
        tracking=True
    )
    visa_no = fields.Char(
        tracking=True
    )
    visa_expire = fields.Date(
        tracking=True
    )
    calendar_mismatch = fields.Boolean(
        tracking=True
    )
    contract_decisions_ids = fields.One2many(
        'hr.contract.decisions',
        'contract_id'
    )
    contract_decisions_ids_count = fields.Integer(compute='_compute_contract_decisions_ids_count')
    socio_professional_category_level_id = fields.Many2one(
        'hr.socioprofessional.categories.levels',
    )
    article12 = fields.Selection([
        ('travaux_prestation', "Le travailleur est recruté pour l'exécution d’un contrat lié à des contrats de travaux "
                               "ou de prestation non  renouvelables"),
        ('interim', "Remplacer le titulaire d’un poste qui s’absente temporairement et au profit duquel l’employeur est"
                    " tenu de conserver le poste de travail"),
        ('travaux_periodiques', "Il s’agit pour l’organisme employeur d’effectuer des travaux périodiques à caractère "
                                "discontinu"),
        ('surcroît', "Surcroît de travail, ou lorsque des motifs saisonniers le justifient"),
        ('nature_temporaires', "Il s’agit d’activités ou d’emplois à durée limitée ou qui sont par nature temporaires")
    ],
        'Article 12'
    )

    @api.depends('employee_id', 'date_start')
    def _compute_first_contract_date(self):
        for contract in self:
            old_contracts = contract.employee_id.contract_ids.sorted('date_start')
            if old_contracts.ids:
                contract.first_contract_date = old_contracts.mapped('date_start')[0]
            else:
                contract.first_contract_date = contract.date_start or fields.Date.today()

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        # res = super(Contract, self)._onchange_employee_id()
        if self.employee_id and not self.id:
            self.nature = 'amendment' if self.employee_id.contract_ids.ids else 'contract'
        # return res

    @api.onchange('resource_calendar_id')
    def _on_calendar_change(self):
        calendar = self.resource_calendar_id
        if calendar.hours_per_day:
            days_per_week = len(list(dict.fromkeys(calendar.mapped('attendance_ids.dayofweek'))))
            days_off_per_week = DAYS_PER_WEEK - days_per_week
            self.hours_per_month = (calendar.hours_per_day * days_per_week * WEEK_PER_YEAR) / MONTH_PER_YEAR
            self.days_per_month = DAYS_PER_MONTH - WEEKS_PER_MONTH * days_off_per_week

    @api.depends('date_start', 'date_end', 'trial_date_end')
    def _compute_period_count_text(self):
        for contract in self:
            contract.period_count_text = contract._get_contract_period_text(contract.date_start, contract.date_end)
            contract.trial_period_count_text = contract._get_contract_period_text(contract.date_start, contract.trial_date_end)

    @api.depends('leave_notice')
    def _compute_leave_notice_text(self):
        for contract in self:
            contract.leave_notice_text = contract._get_contract_period_text(months=contract.leave_notice)

    @api.model
    def create(self, values):
        if not values.get('name', False):
            company = self.env.user.company_id
            sequence = company.contract_sequence_id or self.env.ref('l10n_dz_hr.sequence_hr_employee_documents')
            values['name'] = sequence.next_by_id() if company.use_contract_sequence else '/'
            employee = self.env['hr.employee'].browse(values['employee_id'])
            self.env["hr.employee.printing.log"].create(
                {
                    'name': values['name'],
                    'document': "Contract: " + employee.first_name + " " +
                                employee.last_name,
                    'date': datetime.datetime.now(),
                    'source_employee': True
                }
            )
        return super(Contract, self).create(values)

    def _get_contract_period_text(self, date_start=False, date_end=False, months=False):
        lang = self._get_lang_code()
        if date_start and date_end:
            delta = relativedelta(date_end, date_start)
            months = delta.months + (1 if delta.days >= 28 else 0)
            return "%s (%d) " % (num2words(months, lang=lang), months) + _('months')
        elif months:
            return "%s (%d) " % (num2words(months, lang=lang), months) + _('months')
        return ""

    @api.model
    def _get_lang_code(self):
        lang_code = self.env.context.get('lang') or self.env.user.lang or get_lang(self.env).code
        lang = self.env['res.lang'].with_context(active_test=False).search([('code', '=', lang_code)])
        return lang.iso_code

    def action_open_contract_decisions(self):
        for contract in self:
            tree_view = self.env.ref('l10n_dz_hr.view_contract_decisions_tree')
            form_view = self.env.ref('l10n_dz_hr.view_contract_decisions_form')
            action = {
                'name': _('Employee Contract decisions'),
                'type': 'ir.actions.act_window',
                'res_model': 'hr.contract.decisions',
                'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
                'view_mode': 'tree, form',
                'context': {'default_contract_id': [(4, contract.id)]}
            }

            action['domain'] = [('id', 'in', contract.mapped('contract_decisions_ids.id'))]
            return action

    @api.depends("contract_decisions_ids_count")
    def _compute_contract_decisions_ids_count(self):
        for contract in self:
            contract.contract_decisions_ids_count = len(contract.mapped("contract_decisions_ids"))

    def _get_printed_contract_values(self, value):
        """
        This methode will take the value law, and use regex pattern to extract the needed parts,
        and replace it with the value of its meaning
        :param value:
        :return:
        """
        pattern = r"self.[a-z0-9_]+.[a-z0-9_]+|self.[a-z0-9_]+"
        vals = re.findall(pattern, value)
        if vals:
            for val in vals:
                attribute = val[5:].split('.')
                if len(attribute) >= 2:
                    class_attribute = attribute[0]
                    rest_attribute = attribute[1]
                    v = self[class_attribute][rest_attribute]
                else:
                    class_attribute = attribute[0]
                    v = self[class_attribute]
                value = value.replace(val, v)
        return value
