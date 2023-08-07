# -*- coding: utf-8 -*-
from odoo import _, fields, http
from odoo.http import request
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager


class PayslipPortal(CustomerPortal):

    def _prepare_home_portal_values(self,counters):
        # Call super to initialize values with original values
        values = super(PayslipPortal, self)._prepare_home_portal_values(counters)

        # Get current user
        user_sudo = request.env.user.sudo()

        # Count user's payslips
        HrPayslip = request.env['hr.payslip']
        payslip_count = HrPayslip.sudo().search_count([
            ('state', '=', 'done'),
            ('employee_id.user_id', '=', user_sudo.id),
        ]) if HrPayslip.check_access_rights('read', raise_exception=False) else 0

        # Update values
        values.update({
            'payslip_count': payslip_count,
        })

        # Return
        return values

    @http.route(['/my/payslips', '/my/payslips/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_payslips(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        user_sudo = request.env.user.sudo()
        HrPayslip = request.env['hr.payslip'].sudo()

        domain = [
            ('state', '=', 'done'),
            ('employee_id.user_id', '=', user_sudo.id)
        ]

        searchbar_sortings = {
            'date': {'label': _('Deadline'), 'order': 'date_from desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('hr.payslip', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        payslip_count = HrPayslip.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/payslips",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=payslip_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        payslips = HrPayslip.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_payslips_history'] = payslips.ids[:100]

        values.update({
            'date': date_begin,
            'payslips': payslips.sudo(),
            'page_name': 'payslips',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/payslips',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("smartest_hr_payroll_portal.portal_my_payslips", values)

    @http.route(['/my/payslips/<int:payslip_id>'], type='http', auth="public", website=True)
    def portal_payslip_page(self, payslip_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            payslip_sudo = self._document_check_access('hr.payslip', payslip_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        user_sudo = request.env.user.sudo()
        employee_sudo = payslip_sudo.employee_id.sudo()
        if report_type in ('html', 'pdf', 'text'):
            if employee_sudo.id != user_sudo.employee_id.id:
                raise UserError(_('You Dont have the right the this record !'))
            return self._show_report(
                model=payslip_sudo,
                report_type=report_type,
                report_ref='hr_payroll.action_report_payslip',
                download=download
            )
        is_internal_user = user_sudo.has_group('base.group_user')
        values = {
            'payslip': payslip_sudo,
            'employee': employee_sudo,
            'message': message,
            'token': access_token,
            'is_internal_user': is_internal_user,
            'bootstrap_formatting': True,
            'partner_id': payslip_sudo.employee_id.related_partner_id.id,
            'report_type': 'html',
            'action': request.env.ref('hr_payroll.action_view_hr_payslip_month_form', False)
        }
        if payslip_sudo.company_id:
            values['res_company'] = payslip_sudo.company_id

        if employee_sudo.id != user_sudo.employee_id.id:
            raise UserError(_('You Dont have the right the this record !'))

        history = request.session.get('my_payslips_history', [])
        values.update(get_records_pager(history, payslip_sudo))

        return request.render('smartest_hr_payroll_portal.payslip_portal_template', values)
