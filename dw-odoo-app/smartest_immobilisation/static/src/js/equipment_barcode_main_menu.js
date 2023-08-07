/** @odoo-module **/
import AbstractAction from 'web.AbstractAction';
import core from 'web.core';
import Dialog from 'web.Dialog';
import Session from 'web.session';
import Model from 'web.Model';
import framework from 'web.framework';
import ajax from 'web.ajax';
import * as BarcodeScanner from "@web/webclient/barcode/barcode_scanner";
const _t = core._t;

var data_values;
var po_ids;
var index;
var op_ids;
var operation_ids
var workcenter;

var MainFunction = AbstractAction.extend({
    template: 'smartest_code_scanner',


    init: function (parent) {
        this._super.apply(this, arguments);
        this.of_ids = false;
        this.selected_of_id = false;
        this._get_mrp_production();


    },

//get the all the inventory equipment names
    _get_mrp_production: function() {
        var self = this;
        framework.unblockUI();
        this._rpc({
                model: 'equipement.inventory',
                method: 'js_test',
            })
        .then(function (values) {
        console.log('tets',values)
        if (values){
        var values_str = JSON.stringify(values);
        var json = '{"result":true, "count":42}';
        data_values = JSON.parse(values);
        po_ids = Object.keys(data_values);
        var po = document.getElementById("inventory_id");
//        alert("Obama is "+data_values.anouar);
//        console.log("Obama is "+data_values );
//        var operation = document.getElementById("equipment");
        for (var index in po_ids){

            po.options[po.options.length] = new Option(po_ids[index]);
            }
        }
                    });
        framework.unblockUI();
        },
//
    events: {
    "change .o_order_fabrication_id": async function(){
        var selectedOption = $('#inventory_id').val();
//        alert("selectedOption",+selectedOption)

        var operation = document.getElementById("methods");
        operation.style.visibility = 'visible';
//        operation.options.length = 1;
//        for (var val in data_values){
//            if (val === selectedOption){
//                op_ids = JSON.parse(data_values[val]);
//                operation_ids = Object.keys(JSON.parse(data_values[val]));
//                for (var index in operation_ids){
//                    operation.options[operation.options.length] = new Option(operation_ids[index]);
//                    }
//
//            }
//        }
        this.WorkcenterOnChange();

        },
//    "change .o_operation_id": async function(){
//        var selectedOption = $('#equipment').val();
//        document.getElementById("inventory_id").disabled = true;
//        var center = document.getElementById("workcenter_id");
//        center.options.length = 1;
//        center.style.visibility = 'visible';
//        var items = document.getElementById("o_items");
//        items.style.visibility = 'hidden';
//        var keys = Object.keys(op_ids);
//        keys.forEach(function(key){
//            if (key === selectedOption){
//                center.options[center.options.length] = new Option(op_ids[key]);
//                }});
//        },
     "change .methods":'WorkcenterOnChange',
     "keypress .o_input[type='text']":'_onBarcodeScannedScanner',
     "click .o_stock_mobile_barcode":'openMobileScanner',},


     async openMobileScanner() {
        const barcode = await BarcodeScanner.scanBarcode();
        if (barcode){
            this._onBarcodeScanned(barcode);
            if ('vibrate' in window.navigator) {
                window.navigator.vibrate(100);
            }}

    },
// whene the equipment inventory is selected apply some changes
    WorkcenterOnChange: function(){
//        var CameraScanner = document.getElementById("o_stock_mobile_barcode");
//        CameraScanner.style.visibility = 'visible';
        var methode = document.getElementById("methods");
        if (methode.selectedOptions.item(0).innerHTML == 'Scanner'){
            var CameraScanner = document.getElementById("o_input");
            CameraScanner.style.visibility = 'visible';
            var CameraScanner = document.getElementById("o_stock_mobile_barcode");
            CameraScanner.style.visibility = 'hidden';
            var LabelCameraScanner = document.getElementById("o_input_label");
            LabelCameraScanner.style.visibility = 'visible';
            $(".o_input").focus();
            }
        if (methode.selectedOptions.item(0).innerHTML == 'Téléphone'){
            var CameraScanner = document.getElementById("o_stock_mobile_barcode");
            CameraScanner.style.visibility = 'visible';
            var CameraScanner = document.getElementById("o_input");
            CameraScanner.style.visibility = 'hidden';
            var LabelCameraScanner = document.getElementById("o_input_label");
            LabelCameraScanner.style.visibility = 'hidden';
            }

//        document.getElementById("operation_id").disabled = true;
    },


        _onBarcodeScannedScanner: function (barcode) {
//    document.getElementById("operation_id").disabled = false;
        if(barcode.keyCode == 13 ){
        var test ='true';
        var notificationOptions
        var val_list = {
            'serial_number': $('.o_input').val(),
            'production_id' : $('#inventory_id').val(),
        };


        this._rpc({
        model: 'equipement.inventory',
        method: 'action_create_record',
        args: [val_list],
                }).then(function(value) {
                $('.o_input').val('');
                if (value == 'false'){
//                this.onTest('false');
                test = 'false'
//                alert('Error please scan again! or change Equipment');
                    var items = document.getElementById("o_items");
//                    this.onTest('true');
                    items.style.visibility = 'visible';
                    items.style.color = 'red';
                    items.innerHTML = 'Failed Please Scan Again!';
                   }
                else {
//                    window.navigator.vibrate(100);
                    test = 'true'
                    var items = document.getElementById("o_items");
//                    this.onTest('true');
                    items.style.visibility = 'visible';
                    items.style.color = 'lime';
                    items.innerHTML = 'Success Please Scan Again!';
                    $('.o_input').val('');
                }
                   test = value;

                });
                this.onTest(test);
        $('.o_input').val('');
        return
        }},




    _onBarcodeScanned: function (barcode) {
//    document.getElementById("equipment").disabled = false;
    var test ='true';
    var notificationOptions
    var val_list = {
        'serial_number': barcode,
        'production_id' : $('#inventory_id').val(),
//        'operation_id' : $('#equipment').val(),
//        'workcenter' : $('#workcenter_id').val(),
    };
         this._rpc({
        model: 'equipement.inventory',
        method: 'action_create_record',
        args: [val_list],
            }).then(function(value) {

            window.navigator.vibrate(50);
            test = 'value';
//            alert("valueirer"+test);


//           let notificationOptions = {
//                    type: 'success',
//                    message: _t("The sales orders have successfully been assigned."),
//                };
//             this.displayNotification(notificationOptions);


//            this._notification();
//            var items = document.getElementById("o_items");
//            items.style.visibility = 'visible';
//            items.innerHTML = value;

            });

            this.onTest(test);



//            if (test == 'true'){
//             notificationOptions = {
//                    type: 'success',
//                    message: _t("Scan Next Equipment !"),
//                };}
//                else if(test == 'false'){
//                notificationOptions = {
//                    type: 'danger',
//                    message: _t("Equipment does not exist in the inventory please scan another Equipment!"),
//                };
//                }
//             this.displayNotification(notificationOptions);
//             alert("outside"+test);

//             window.location.reload();
//                this.openMobileScanner()
    },

    async onTest (xxx) {
    var notificationOptions;
    if (xxx == 'true'){
             notificationOptions = {
                    type: 'success',
                    message: _t("Scan Next Equipment !"),
                };
                this.displayNotification(notificationOptions);}
                else if(xxx == 'false'){
                notificationOptions = {
                    type: 'danger',
                    message: _t("Equipment does not exist in the inventory please scan another Equipment!"),
                };
                this.displayNotification(notificationOptions);
                }
//             this.displayNotification(notificationOptions);
//             alert("outside"+xxx);
             },
//    _notification: function() {
//        this.displayNotification({
//            type: 'success',
//            message:_t("Scan Next Item !"),
//            });
//            alert("_notification marche !!!!");
//
//    },

    });

core.action_registry.add('equipment_barcode_main_menu', MainFunction);

//return equipment_barcode_main_menu;
//export default MainFunction;

