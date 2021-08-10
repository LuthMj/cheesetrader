//==============================================================================
/**
@file       position_pi.js
@brief      CheeseTrader API Plugin
@copyright  (c) 2021, CheeseTrader.io
            This source code is licensed under the MIT-style license found in the LICENSE file.
**/
//==============================================================================

if ($SD) {
    $SD.on("connected", function (jsonObj) {
        console.log(`[connected] ${JSON.stringify(jsonObj)}`);
        if (jsonObj.hasOwnProperty('actionInfo')) {
            settings = Utils.getProp(jsonObj, 'actionInfo.payload.settings', {});
        }
    });
};
const save = function () {
    if ($SD) {
        var payload = {};
        [].forEach.call(document.querySelectorAll(".inspector"), element => {
            payload[element.id] = element.value;
        });
        $SD.api.sendToPlugin($SD.uuid, $SD.actionInfo["action"], payload);
    }
}