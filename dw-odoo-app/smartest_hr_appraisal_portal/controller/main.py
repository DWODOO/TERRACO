# -*- coding: utf-8 -*-
from odoo import _, fields, http
from odoo.http import request
from odoo.exceptions import AccessError, MissingError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager


class EmployeePortal(CustomerPortal):

    def _prepare_home_portal_values(self,counters):
        # Call super to initialize values with original values
        values = super(EmployeePortal, self)._prepare_home_portal_values(counters)

        # Get current user
        user = request.env.user

        # Count user's appraisals
        HrAppraisal = request.env['hr.appraisal']
        appraisal_count = HrAppraisal.sudo().search_count([
            ('employee_id.user_id', '=', user.id)
        ]) if HrAppraisal.check_access_rights('read', raise_exception=False) else 0

        # Update values
        values.update({
            'appraisal_count': appraisal_count,
        })

        # Return
        return values

    @http.route(['/my/appraisals', '/my/appraisals/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_appraisals(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user
        HrAppraisal = request.env['hr.appraisal'].sudo()

        domain = [
            ('employee_id.user_id', '=', user.id)
        ]

        searchbar_sortings = {
            'date': {'label': _('Deadline'), 'order': 'date_close desc'},
            # 'quarter': {'label': _('Quarter'), 'order': 'appraisal_quarter'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('hr.appraisal', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        appraisal_count = HrAppraisal.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/appraisals",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=appraisal_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        appraisals = HrAppraisal.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_appraisals_history'] = appraisals.ids[:100]

        values.update({
            'date': date_begin,
            'appraisals': appraisals.sudo(),
            'page_name': 'appraisals',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/appraisals',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("smartest_hr_appraisal_portal.portal_my_appraisals", values)

    @http.route(['/my/appraisals/<int:appraisal_id>'], type='http', auth="public", website=True)
    def portal_appraisal_page(self, appraisal_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            appraisal_sudo = self._document_check_access('hr.appraisal', appraisal_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(
                model=appraisal_sudo,
                report_type=report_type,
                report_ref='smartest_hr_appraisal.action_hr_appraisal_report',
                download=download
            )
        employee_sudo = appraisal_sudo.employee_id.sudo()
        validator_sudo = appraisal_sudo.validator_id.sudo()
        is_internal_user = request.env.user.has_group('base.group_user')
        values = {
            'appraisal': appraisal_sudo,
            'employee': employee_sudo,
            'validator': validator_sudo,
            'message': message,
            'token': access_token,
            'is_internal_user': is_internal_user,
            'bootstrap_formatting': True,
            'partner_id': appraisal_sudo.employee_id.related_partner_id.id,
            'report_type': 'html',
            'action': request.env.ref('hr_appraisal.open_view_hr_appraisal_tree', False)
        }
        if appraisal_sudo.company_id:
            values['res_company'] = appraisal_sudo.company_id

        history = request.session.get('my_appraisals_history', [])
        values.update(get_records_pager(history, appraisal_sudo))

        return request.render('smartest_hr_appraisal_portal.appraisal_portal_template', values)
