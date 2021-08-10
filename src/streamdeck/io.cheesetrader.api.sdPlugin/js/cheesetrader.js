//==============================================================================
/**
@file       cheesetrader.js
@brief      CheeseTrader API Plugin
@copyright  (c) 2021, CheeseTrader.io
            This source code is licensed under the MIT-style license found in the LICENSE file.
**/
//==============================================================================

$SD.on('connected', (jsonObj) => connected(jsonObj));

function connected(jsonObj) {
    console.log(`[connected] ${JSON.stringify(jsonObj)}`);
    // Order Action
    $SD.on('io.cheesetrader.api.order.willAppear', (jsonObj) => order.onWillAppear(jsonObj));
    $SD.on('io.cheesetrader.api.order.keyDown', (jsonObj) => order.onKeyDown(jsonObj));
    $SD.on('io.cheesetrader.api.order.didReceiveSettings', (jsonObj) => order.onDidReceiveSettings(jsonObj));
    $SD.on('io.cheesetrader.api.order.sendToPlugin', (jsonObj) => order.onSendToPlugin(jsonObj));
    // Postion Action
    $SD.on('io.cheesetrader.api.position.willAppear', (jsonObj) => position.onWillAppear(jsonObj));
    $SD.on('io.cheesetrader.api.position.keyDown', (jsonObj) => position.onKeyDown(jsonObj));
    $SD.on('io.cheesetrader.api.position.didReceiveSettings', (jsonObj) => position.onDidReceiveSettings(jsonObj));
    $SD.on('io.cheesetrader.api.position.sendToPlugin', (jsonObj) => position.onSendToPlugin(jsonObj));
};

const order = {
    onDidReceiveSettings: (jsonObj) => {
        console.log(`[onDidReceiveMessage] ${JSON.stringify(jsonObj)}`);
    },
    onWillAppear: (jsonObj) => {
        console.log(`[onWillAppear] ${JSON.stringify(jsonObj)}`);
        $SD.api.sendToPropertyInspector(jsonObj.context, Utils.getProp(jsonObj, "payload.settings", {}), jsonObj.action);
    },
    onSendToPlugin: (jsonObj) => {
        console.log(`[onSendToPlugin] ${JSON.stringify(jsonObj)}`);
        if (jsonObj.payload) {
            $SD.api.setSettings(jsonObj.context, jsonObj.payload);
        }
    },
    onKeyDown: (jsonObj) => {
        console.log(`[onKeyDown] ${JSON.stringify(jsonObj)}`);
        if (!jsonObj.payload.settings || !jsonObj.payload.settings.order_type || !jsonObj.payload.settings.symbol || !jsonObj.payload.settings.lot_size) {
            $SD.api.showAlert(jsonObj.context);
            return;
        }
        base_url = 'http://127.0.0.1:8000/'
        url = base_url + 'orders/open_order?symbol=' + jsonObj.payload.settings.symbol + '&order_type=' + jsonObj.payload.settings.order_type + '&size=' + jsonObj.payload.settings.lot_size
        fetch(url, {
            "method": "PUT",
            "headers": {
                "content-type": "application/json"
            },
            "body": "{}"
        }).then(result => $SD.api.showOk(jsonObj.context), error => $SD.api.showAlert(jsonObj.context));
    }
};

const position = {
    onDidReceiveSettings: (jsonObj) => {
        console.log(`[onDidReceiveMessage] ${JSON.stringify(jsonObj)}`);
    },
    onWillAppear: (jsonObj) => {
        console.log(`[onWillAppear] ${JSON.stringify(jsonObj)}`);
        $SD.api.sendToPropertyInspector(jsonObj.context, Utils.getProp(jsonObj, "payload.settings", {}), jsonObj.action);
    },
    onSendToPlugin: (jsonObj) => {
        console.log(`[onSendToPlugin] ${JSON.stringify(jsonObj)}`);
        if (jsonObj.payload) {
            $SD.api.setSettings(jsonObj.context, jsonObj.payload);
        }
    },
    onKeyDown: (jsonObj) => {
        console.log(`[onKeyDown] ${JSON.stringify(jsonObj)}`);
        if (!jsonObj.payload.settings) {
            $SD.api.showAlert(jsonObj.context);
            return;
        }
        fetch('http://127.0.0.1:8000/positions/close_all_positions', {
            "method": "PUT",
            "headers": {
                "content-type": "application/json"
            },
            "body": "{}"
        }).then(result => $SD.api.showOk(jsonObj.context), error => $SD.api.showAlert(jsonObj.context));
    }
};