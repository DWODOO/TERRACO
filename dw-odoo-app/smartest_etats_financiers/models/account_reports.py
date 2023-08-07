# -*- coding: utf-8 -*-
# Part of Smartest

from odoo import models, fields, api, _, osv


class SmartestAccountReport(models.Model):
    _inherit = 'account.report'


    date_from = fields.Char('date from')
    date_to = fields.Char('date to')
    year_1 = fields.Char('year 1')
    year_2 = fields.Char('year 2')
    comparison = fields.Char('comparison')



    def _init_options_buttons(self, options, previous_options=None):
        res = super(SmartestAccountReport, self)._init_options_buttons(options)
        if self.custom_pdf_button_satisfy_condition(self.get_report_ids_to_customize()):
            options["buttons"].append({'name': _('Custom PDF'), 'sequence': 200, 'action': 'smartest_custom_pdf'})
        return res

    def get_report_ids_to_customize(self):
        return [self.env.ref('smartest_etats_financiers.accounting_bilan_pasif').id,
                self.env.ref('smartest_etats_financiers.accounting_bilan_actif').id,
                self.env.ref('smartest_etats_financiers.accounting_balance').id]

    def custom_pdf_button_satisfy_condition(self, report_ids):
        self.ensure_one()
        if self.id in report_ids:
            return True
        return False

    def smartest_custom_pdf(self, options):
        data = self.smartest_print_custom_pdf(options)
        if self.id == self.env.ref('smartest_etats_financiers.accounting_bilan_pasif').id:
            action = 'smartest_etats_financiers.algerian_report_passif_custom_pdf_report'
        if self.id == self.env.ref('smartest_etats_financiers.accounting_bilan_actif').id:
            get_net = self.get_net(options, 2)
            dict_header_column_net_list = get_net[0]
            data = self.smartest_print_custom_pdf(options)
            data["table_data_column"] = dict_header_column_net_list
            data["table_data_line"] = get_net[1]
            action = 'smartest_etats_financiers.algerian_report_actif_custom_pdf_report'

        if self.id == self.env.ref('smartest_etats_financiers.accounting_balance').id:
            action = 'smartest_etats_financiers.algerian_report_balance_custom_pdf_report'

        return self.env.ref(action).report_action(self, data=data)

    def smartest_print_custom_pdf(self, options):
        lines = self._get_lines(options)
        dict_lines = self.action_get_custom_lines(lines)
        dict_header_column = self.action_get_custom_columns_header(options['columns'])
        company = self.env.company
        self._compute_get_options_date(options)

        return {
            'table_data_line': dict_lines,
            'table_data_column': dict_header_column[0],
            'report_id': self,
            # 'date_start':,
            # 'date_end':,
            'company_commercial_register': company.commercial_register,
            'company_nif': company.fiscal_identification,
            'company_taxation': company.taxation,
            'company_nis': company.nis,
            'company_phone': company.phone,
            'company_mobile': company.mobile,
            'company_email': company.email,
            'company_name': company.name,
            'company_street': company.street,
            'company_street2': company.street2,
            'company_city': company.city,
            'company_zip': company.zip,
            'company_state': company.state_id.name if company.state_id else "",
            'company_country': company.country_id.name if company.state_id else "",
            'date_from':self.date_from,
            'date_to':self.date_to,
            'year_1':self.year_1,
            'year_2':self.year_2,
            'comparison':self.comparison


        }

    def action_get_custom_lines(self, lines):
        custom_dict = []
        list_report_line_id = []
        AccountReportLine = self.env["account.report.line"].sudo()
        columns_dict_list = [line.get("columns") for line in lines]
        company = self.env.company
        for line_column in columns_dict_list:
            col_dict = []
            for line in line_column:
                report_line_id = line.get("report_line_id")
                col_dict.append(
                    {"expression_label": line.get("line"), "with_format": line.get("name"), "style": line.get("style"),
                     "no_format": line.get("no_format"),
                     "with_format_int": str(int(line.get("no_format"))) if line.get("no_format") else "",

                     })
            custom_dict.append({"columns": col_dict})
            list_report_line_id.append(report_line_id)

        report_line_ids = AccountReportLine.browse(list_report_line_id)
        range_ids = len(report_line_ids)
        for i in range(range_ids):
            custom_dict[i]["line_name"] = lines[i]["name"]
            custom_dict[i]["line_code"] = report_line_ids[i]["code"]
            custom_dict[i]["line_level"] = lines[i]["level"]
            custom_dict[i]["line_id"] = report_line_ids[i]

        return custom_dict

    def get_net(self, options, column_report_len):
        dict_header_column_net = self.action_get_custom_columns_header(options['columns'])
        dict_header_column_net_list = dict_header_column_net[0]
        len_column_list = dict_header_column_net[1] - 1  # lenth
        head_to_add = []
        i = 0
        col_to_add = []
        while i + 1 <= len_column_list:
            i = i + column_report_len
            col_to_add.append({"position": i, "value": {"expression_label": "net", "name": "NET","style": 'white-space:nowrap; text-align:right;',
                                                        "column_group_key": ""}})
        head_to_add.append({"columns": col_to_add}) #dont need line_position
        for line in head_to_add:
            columns = line.get("columns")
            len_c = len(columns)
            i = len_c - 1
            while i >= 0:
                dict_header_column_net_list.insert(columns[i]["position"], columns[i]["value"])
                i = i - 1
        if len_column_list > column_report_len:
            del dict_header_column_net_list[3]
            del dict_header_column_net_list[3]



        lines = self._get_lines(options)
        dict_lines_net = self.action_get_custom_lines(lines)
        company = self.env.company
        j = 0
        line_col_to_add = []
        for line in dict_lines_net:
            columns = line.get("columns")
            len_col = len(columns) - 1
            i = 0
            col_to_add = []
            while i + 1 <= len_col:
                net_0 = columns[i].get("no_format") if columns[i].get("no_format") else 0
                net_1 = columns[i + 1].get("no_format") if columns[i + 1].get("no_format") else 0
                net = round(net_0 - net_1, 2)
                i = i + column_report_len
                col_to_add.append({"position": i, "value": {"expression_label": "Net",
                                                            "with_format": str(
                                                                net) + " " + company.currency_id.name if net else "",
                                                            "style": 'white-space:nowrap; text-align:right;',
                                                            "no_format": net if net else "",
                                                            "with_format_int": str(
                                                                int(net)) if net else "",
                                                            }})

            line_col_to_add.append({"line_position": j, "columns": col_to_add})
            j = j + 1

        for line in line_col_to_add:
            columns = line.get("columns")
            len_c = len(columns)
            i = len_c - 1
            while i >= 0:
                dict_lines_net[line["line_position"]]["columns"].insert(columns[i]["position"], columns[i]["value"])
                i = i - 1
        if len_column_list > column_report_len:
            for line in dict_lines_net:
                del line['columns'][3]
            for line in dict_lines_net:
                del line['columns'][3]
        return dict_header_column_net_list, dict_lines_net


    def action_get_custom_columns_header(self, column_list):
        col_dict = []

        for col in column_list:
            col_dict.append(
                {"expression_label": col.get("expression_label"), "name": col.get("name"), "style": col.get("style"),
                 "column_group_key": col.get("column_group_key")})
        return col_dict, len(col_dict)

    def _compute_get_options_date(self, options):
        for rec in self:
            rec.date_from = options['date']['date_from']
            rec.date_to = options['date']['date_to']
            rec.year_1 = options['date']['string']
            rec.comparison = options['comparison']['filter']
            if rec.comparison != 'no_comparison':
                rec.year_2 = options['comparison']['string']



    def get_custom_line_by_attribute(self, lines, attribute, attribute_value):
        filtered_list_of_dicts = [
            dictionary for dictionary in lines
            if dictionary[attribute] == attribute_value
        ]
        if filtered_list_of_dicts:
            return filtered_list_of_dicts[0]
        return False
