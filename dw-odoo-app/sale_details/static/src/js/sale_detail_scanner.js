/** @odoo-module **/
import AbstractAction from 'web.AbstractAction';
import core from 'web.core';
import Dialog from 'web.Dialog';
import Session from 'web.session';
import Model from 'web.Model';
import framework from 'web.framework';
import ajax from 'web.ajax';
import * as BarcodeScanner from '@web_enterprise/webclient/barcode/barcode_scanner';
const _t = core._t;
import { useService } from "@web/core/utils/hooks";


var serial_number;
var self;
var res_id;
var data;

var MainFunction = AbstractAction.extend({

    init: function (parent) {
        this._super.apply(this, arguments);
        this.rpc = useService('rpc');
        var self =this;
        res_id = self.searchModelConfig.context.res_id;
        data = self.searchModelConfig.context.data;
        this.openMobileScanner();
        },

     async openMobileScanner() {
        const barcode = await BarcodeScanner.scanBarcode();
        if (barcode){
            this.onBarcodeScannedMobile(barcode);
            if ('vibrate' in window.navigator) {
                window.navigator.vibrate(100);
            }
            else{
                self.trigger_up('reload');
            }
            }
    },
    onBarcodeScannedMobile: function (barcode) {
        self = this;
        var rec = this;
        var val_list = {
            'res_id': res_id,
            'barcode': barcode,
        };
        this._rpc({
        model: 'sale.details.line',
        method: 'create_lines_from_front',
        args: [val_list],
        }).then(function(value) {
                    if (value[0] == false){
                        self.displayNotification({ title: value[1], type: 'danger' });
                        }
//                    else{
                    rec.do_action({
                        name: 'Sale Details',
                        res_model: 'sale.details',
                        views: [[false, 'form']],
                        type: 'ir.actions.act_window',
                        view_mode: 'form',
                        target: 'new',
                        res_id: res_id,
                        context: data,
                    });
//                        }
                   });
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
        },
    });

core.action_registry.add('smartest_sale_details_main_menu', MainFunction);

return smartest_sale_details_main_menu;
export default MainFunction;

