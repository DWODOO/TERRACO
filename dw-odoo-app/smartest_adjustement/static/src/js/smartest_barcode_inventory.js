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
//    alert("Obama is " );

var MainFunction = AbstractAction.extend({
    template: 'inventory_code_scanner',


    init: function (parent) {
        this._super.apply(this, arguments);
        this.of_ids = false;
        this.selected_of_id = false;
        this._get_inventory_name();

    },
    
// _get_inventory_name the get the inventory adjustment name
 
    _get_inventory_name: function() {
        var self = this;
        framework.unblockUI();
        this._rpc({
                model: 'smartest.inventory',
                method: 'inventory_name',
            })
        .then(function (values) {
        var values_str = JSON.stringify(values);
        data_values = JSON.parse(values);
        po_ids = Object.keys(data_values);
        var po = document.getElementById("inventory_id");
        for (var index in po_ids){
            po.options[po.options.length] = new Option(po_ids[index]);
            }
                    });
        framework.unblockUI();

        },

     events: {
    "change .o_inventory_id": async function(){
        var selectedOption = $('#inventory_id').val();
        this.inventory_idOnChange();

        },
            "change .o_count_id": async function(){
        var selectedOption = $('#count_id').val();
        if ( isNaN(selectedOption) == false){
                this.countOnChange();
        }
        else {
        alert("Please Enter a Valid Number")
        }

        },
     "change .o_order_fabrication_id":'inventory_idOnChange',
     "change .methods":'methods_idOnChange',
     "keypress .o_input[type='text']":'_onBarcodeScannedScanner',
     "click .o_validate_count":'_createLine',
     "click .o_stock_mobile_barcode":'openMobileScanner',},

    methods_idOnChange: function(){
        var location = document.getElementById("location_id");
        var product = document.getElementById("product_id");

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
        var val_list = {
            'serial_number': $('.o_input').val(),
        };


        this._rpc({
        model: 'smartest.inventory',
        method: 'check_barcode_scanned',
        args: [val_list],
                }).then(function(value) {
            if (value == false){
            alert('Error please scan again! or change product');
               }
            else {
                window.navigator.vibrate(100);
                var items = document.getElementById("o_items");
//                items.style.visibility = 'visible';
//                items.innerHTML = value;
            }


            if (value[0] == 'location'){
                var po = document.getElementById("location_id");
                po.value = value[1];
                po.style.visibility = 'visible';
                }
            else if  (value[0] == 'product'){
                var po = document.getElementById("product_id");
                po.value = value[1];
                po.style.visibility = 'visible';
                }

            var loc = document.getElementById("location_id");
            var pro = document.getElementById("product_id");
            if (loc.value != 'default_value_location_id' && pro.value != 'default_value_product_id'){
            var cou = document.getElementById("count_id")
             cou.style.visibility = 'visible';
            }
            });
        $('.o_input').val('');
        return
        }},



    _createLine: function () {
    var val_list = {
        'inventory_id' : $('#inventory_id').val(),
        'location_id' : $('#location_id').val(),
        'product_id' : $('#product_id').val(),
        'count_id' : $('#count_id').val(),
    };
    this._rpc({
        model: 'smartest.inventory',
        method: 'create_line',
        args: [val_list],
            }).then(function(value) {
            window.location.reload();

            });
    },

     async openMobileScanner() {
        const barcode = await BarcodeScanner.scanBarcode();
        if (barcode){
            this._onBarcodeScanned(barcode);
            if ('vibrate' in window.navigator) {
                window.navigator.vibrate(100);
            }}

    },
    countOnChange: function(){
        var CameraScanner = document.getElementById("o_stock_mobile_barcode");
        CameraScanner.style.visibility = 'hidden';
        var count_validate = document.getElementById("o_validate_count");
        count_validate.style.visibility = 'visible';
    },


    inventory_idOnChange: function(){
        var Method = document.getElementById("methods");
        Method.style.visibility = 'visible';

         var val_list = {
        'inventory_id' : $('#inventory_id').val(),
    };
        this._rpc({
        model: 'smartest.inventory',
        method: 'get_the_count_number',
        args: [val_list],
            }).then(function(value) {
                  var just_test = document.getElementById("p_id");
                  just_test.innerHTML = value;

            });

    },
    _onBarcodeScanned: function (barcode) {
    var val_list = {
        'serial_number': barcode,
    };
    this._rpc({
        model: 'smartest.inventory',
        method: 'check_barcode_scanned',
        args: [val_list],
            }).then(function(value) {
            if (value == false){
            alert('Error please scan again! or change product');
            var items = document.getElementById("o_items");
//                items.style.visibility = 'visible';
//                items.innerHTML = value;
               }
            else {
                window.navigator.vibrate(100);
                var items = document.getElementById("o_items");
//                items.style.visibility = 'visible';
//                items.innerHTML = value;
            }


            if (value[0] == 'location'){
                var po = document.getElementById("location_id");
                po.value = value[1];
                po.style.visibility = 'visible';
                }
            else if  (value[0] == 'product'){
                var po = document.getElementById("product_id");
                po.value = value[1];
                po.style.visibility = 'visible';
                }

            var loc = document.getElementById("location_id");
            var pro = document.getElementById("product_id");
            if (loc.value != 'default_value_location_id' && pro.value != 'default_value_product_id'){
            var cou = document.getElementById("count_id")
             cou.style.visibility = 'visible';
            }
            });
    },
    });

core.action_registry.add('smartest_barcode_inventory', MainFunction);

return smartest_barcode_inventory;
export default MainFunction;

