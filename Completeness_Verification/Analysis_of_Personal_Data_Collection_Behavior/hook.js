function getStackTrace() {
    var Exception = Java.use('java.lang.Exception');
    var ins = Exception.$new('Exception');
    var straces = ins.getStackTrace();
    if (undefined == straces || null == straces) {
        return;
    }
    var result = '';
    for (var i = 0; i < straces.length; i++) {
        var str = '   ' + straces[i].toString();
        result += str + '\r\n';
    }
    Exception.$dispose();
    return result;
}

function get_format_time() {
    var myDate = new Date();
    var month = myDate.getMonth() + 1;
    return myDate.getFullYear() + '-' + month + '-' + myDate.getDate() + ' ' + myDate.getHours() + ':' + myDate.getMinutes() + ':' + myDate.getSeconds();
}

function alertSend(action, messages, arg, res) {
    var _time = get_format_time();
    var result;
    if(res == null)
        result = 'null';
    else if(res == undefined)
        result = 'undefined';
    else if(action == '获取网络信息')
        result = res.toString();
    else if(action == '获取位置信息')
        result = res.toString();
    else
        result = JSON.stringify(res);
    send({
        'type': 'notice',
        'time': _time,
        'action': action,
        'messages': messages,
        'arg': arg,
        'result': result,
        'stacks': getStackTrace()
    });
}

function hookMethod(targetClass, targetMethod, targetArgs, action, messages) {
    try {
        var _Class = Java.use(targetClass);
    } catch (e) {
        return false;
    }
    var overloadCount = _Class[targetMethod].overloads.length;

    for (var i = 0; i < overloadCount; i++) {
        _Class[targetMethod].overloads[i].implementation = function () {
            var temp = this[targetMethod].apply(this, arguments);
            var argumentValues = Object.values(arguments);
            if (Array.isArray(targetArgs) && targetArgs.length > 0 && !targetArgs.every(item => argumentValues.includes(item))) {
                return null;
            }
            var arg = '';
            for (var j = 0; j < arguments.length; j++) {
                arg += '参数' + j + '：' + JSON.stringify(arguments[j]) + '\r\n';
            }
            if (arg.length == 0) arg = '无参数';
            else arg = arg.slice(0, arg.length - 1);
            console.log(temp);
            alertSend(action, messages, arg, temp);
            return temp;
        }
    }
    return true;
}

function getNetwork() {
    var action = '获取网络信息';

    hookMethod('android.net.wifi.WifiInfo','getSSID','',action,'获取wifi SSID');
    hookMethod('java.net.InetAddress','getHostAddress','',action,'获取IP地址');
    hookMethod('java.net.Inet4Address','getHostAddress','',action,'获取IP地址');
    hookMethod('java.net.Inet6Address','getHostAddress','',action,'获取IP地址');
    hookMethod('android.net.NetworkInfo','getTypeName','',action,'获取网络类型名称');

    try {
        var _WifiInfo = Java.use('android.net.wifi.WifiInfo');

        _WifiInfo.getIpAddress.implementation = function () {
            var temp = this.getIpAddress();
            var _ip = new Array();
            _ip[0] = (temp >>> 24) >>> 0;
            _ip[1] = ((temp << 8) >>> 24) >>> 0;
            _ip[2] = (temp << 16) >>> 24;
            _ip[3] = (temp << 24) >>> 24;
            var _str = String(_ip[3]) + "." + String(_ip[2]) + "." + String(_ip[1]) + "." + String(_ip[0]);
            alertSend(action, '获取IP地址：' + _str, '', temp);
            return temp;
        }
    } catch (e) {
        console.log(e)
    }
}

function getDevice(){
    var action = '获取设备信息';

    hookMethod('android.provider.Settings$Secure','getString',['android_id'],action,'获取安卓ID');
    hookMethod('android.provider.Settings$System','getString',['android_id'],action,'获取安卓ID');
    hookMethod('com.android.id.impl.IdProviderImpl','getOAID','',action,'获取匿名设备标识符OAID');
    hookMethod('com.android.id.impl.IdProviderImpl','getVAID','',action,'获取开发者匿名设备标识符VAID');
    hookMethod('com.android.id.impl.IdProviderImpl','getAAID','',action,'获取匿名设备标识符AAID');
}

function getTelephony(){
    var action = '获取电话信息';

    hookMethod('android.telephony.TelephonyManager','getSimOperator','',action,'获取MCC/MNC');
    hookMethod('android.telephony.TelephonyManager','getNetworkOperator','',action,'获取MCC/MNC');
    hookMethod('android.telephony.TelephonyManager','getSimCountryIso','',action,'获取SIM卡国家代码');
}

function getLocation(){
    var action = '获取位置信息';

    hookMethod('android.location.LocationManager','requestLocationUpdates','',action,action);
    hookMethod('android.location.LocationManager','getLastKnownLocation','',action,action);
    hookMethod('android.location.LocationManager','requestSingleUpdate','',action,action);
    hookMethod('android.location.LocationManager','getProvider','',action,action);
    hookMethod('android.location.LocationManager','getCurrentLocation','',action,action);
    hookMethod('android.location.Location','getLongitude','',action,action);
    hookMethod('android.location.Location','getLatitude','',action,action);
    hookMethod('android.location.Location','getExtras','',action,action);
    hookMethod('android.location.Location','getAltitude','',action,action);
    hookMethod('android.location.Location','getAccuracy','',action,action);
    hookMethod('android.location.Location','getTime','',action,action);
    hookMethod('android.location.Geocoder','getFromLocation','',action,action);
}


function main() {
    try {
        Java.perform(function () {
           getNetwork();
           getDevice();
           getTelephony();
           getLocation();
        });
    } catch (e) {
        console.log(e)
    }
}

