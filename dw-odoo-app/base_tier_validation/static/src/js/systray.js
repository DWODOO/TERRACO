/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { qweb } from "web.core";
import { useBus } from "@web/core/utils/hooks";
import { Component, useState, mount, useComponent, onWillStart, onMounted, onWillUnmount, onWillUpdateProps, onPatched, onWillPatch, onWillRender, onRendered, onWillDestroy, useRef } from "@odoo/owl";


class ReviewMenu extends Component {
    setup() {
        this.$reviews_preview = $(".o_mail_systray_dropdown_items");
//        this.rootRef = useRef("root");
        this.orm = useService("orm");
        this.action = useService("action");
        this._updateReviewPreview();
        this.state = useState({flag: false });
        var self = this;
        var channel = "base.tier.validation";
        this.env.services['bus_service'].addEventListener('notification',self._handleNotifications)
     }

    async _handleNotifications({ detail: notifications }) {
        const proms = notifications.map(message => {
            if (typeof message === 'object') {
                switch (message.type) {
                    case 'base.tier.validation':
                    if (message.payload == 'create'){
                        var counter = $(".o_notification_counter").text();
                        $(".o_notification_counter").text(parseInt(counter)+1);
                        }
                    if (message.payload == 'done'){
                        var counter = $(".o_notification_counter").text();
                        $(".o_notification_counter").text(parseInt(counter)-1);
                        }

                    }

            }
        });
    }

     _updateReviewPreview() {
        var self = this;
        self._getReviewData();
        }

     _onReviewFilterClick(ev) {

            var data = _.extend(
                {},
                $(event.currentTarget).data(),
                $(event.target).data()
            );
            var context = {};
            this.env.services.action.doAction(
            {
                name: data.model_name,
                type: "ir.actions.act_window",
                view_mode: "form",
                views: [
                    [false, "list"],
                    [false, "form"]
                    ],
                res_model: data.res_model,
                search_view_id: [false],
                domain: [["can_review", "=", true]],
                context: context,
            });
    }



    async _getReviewData() {
            var self = this;
            const action = await this.orm.call("res.users", "review_user_count", [], {})
            .then(function (data) {
                    self.reviews = data;
                    self.reviewCounter = _.reduce(
                        data,
                        function (total_count, p_data) {
                            return total_count + p_data.pending_count;
                        },
                        0
                    );
                    $(".o_notification_counter").text(self.reviewCounter);
//                    $el.toggleClass("o_no_notification", !self.reviewCounter);
                });
        }

    _onClick() {
        var self = this;
        this.state.flag = !this.state.flag;
    }
}
ReviewMenu.template = "base_tier_validation.SystrayItem";


export const mainmenu = {
    Component: ReviewMenu,
    isDisplayed: (env) => env.services.user,
};

registry.category("systray").add("ReviewMenu", mainmenu, { sequence: 1 });
