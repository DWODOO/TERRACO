/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { qweb } from "web.core";
import { session } from '@web/session';
import fieldRegistry from 'web.field_registry';
import AbstractFieldOwl from 'web.AbstractFieldOwl';


import { Component, useState, mount, useComponent, onWillStart, onMounted, onWillUnmount, onWillUpdateProps, onPatched, onWillPatch, onWillRender, onRendered, onWillDestroy, useRef } from "@odoo/owl";


class ReviewField extends AbstractFieldOwl {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        var self = this;
        this.state = useState({flag: false, reviews: false });

            }

        async _getReviewData() {
            var self = this;
            const res_ids = this.props.value.resIds;
            const data = await this.orm.call("res.users", "get_reviews", [res_ids,], {})
            .then(function (data) {
                    self.state.reviews = data;
            });
        }
    _flagchange() {
        var self = this;
        self.state.flag = !self.state.flag;
    }

     _onReviewFilterClick() {
            var self = this;
            if (self.state.flag == false) {
                this._getReviewData()
                .then(function () {
                self._flagchange();
                });
            }
            else{
                self._flagchange();
            }
    }
}
ReviewField.template = "base_tier_validation.tier_review_Collapse";
ReviewField.supportedTypes = ['many2many','one2many'];


registry.category("fields").add("tier_valid", ReviewField);
