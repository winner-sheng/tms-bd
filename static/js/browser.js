var appleUrl = 'http://itunes.apple.com/us/app/tu-hou/id961665300?l=zh&ls=1&mt=8';
var tecentUrl = 'http://android.myapp.com/myapp/detail.htm?apkName=android.twohou.com';
//手机端判断各个平台浏览器及操作系统平台
var isAndroid = /android/i.test(navigator.userAgent);
var isIos = /(iPhone|iPad|iPod|iOS)/i.test(navigator.userAgent);
var isLinuxBrowser = /Linux/i.test(navigator.userAgent); //这是Linux操作系统下的浏览器
var isLinux = /Linux/i.test(navigator.platform); //这是Linux操作系统平台
var isMM = /MicroMessenger/i.test(navigator.userAgent); //这是微信平台下浏览器
var url = isIos ? appleUrl : tecentUrl;
location.replace(url);