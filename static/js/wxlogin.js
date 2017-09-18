/**
 * Created by Winsom on 2015/8/9.
 */
var WX_OAUTH_URL = "https://open.weixin.qq.com/connect/oauth2/authorize?scope=snsapi_base&state=STATE%23wechat_redirect&response_type=code";
var CHECK_WX_LOGIN_URL = '/tms-api/connect/check_wx_login';
var WX_APP_ID = "wxde492242f3312d5a";

var browser = {
    versions: function () {
        var u = navigator.userAgent, app = navigator.appVersion;
        return {         //移动终端浏览器版本信息
            trident: u.indexOf('Trident') > -1, //IE内核
            presto: u.indexOf('Presto') > -1, //opera内核
            webKit: u.indexOf('AppleWebKit') > -1, //苹果、谷歌内核
            gecko: u.indexOf('Gecko') > -1 && u.indexOf('KHTML') == -1, //火狐内核
            mobile: !!u.match(/AppleWebKit.*Mobile.*/), //是否为移动终端
            ios: !!u.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/), //ios终端
            android: u.indexOf('Android') > -1 || u.indexOf('Linux') > -1, //android终端或uc浏览器
            iPhone: u.indexOf('iPhone') > -1, //是否为iPhone或者QQHD浏览器
            iPad: u.indexOf('iPad') > -1, //是否iPad
            webApp: u.indexOf('Safari') == -1, //是否web应该程序，没有头部与底部
            isWeixin: u.toLowerCase().indexOf('micromessenger') != -1
        };
    }(),
    language: (navigator.browserLanguage || navigator.language).toLowerCase()
};

var params = GetRequestParam();  //获取参数字典

if (params['store_flag'] || params['hotel_flag']){ //用于标记来源酒店及门店信息
    if (params['store_flag']){
        localStorage.setItem('store_flag', params['store_flag']);
    }
    if(params['hotel_flag']){
        localStorage.setItem('hotel_flag', params['hotel_flag']);
    }
    $.get('/tms-api/mark_user?store_flag='+params['store_flag']+"&hotel_flag="+params['hotel_flag']);
}

var enduser = localStorage.getItem('enduser');
enduser = enduser ? JSON.parse(enduser) : {};
var wx_user = enduser['wx_user'] || {};
//alert(location.href);
if (browser.versions.isWeixin) {//判断是否微信中打开
    if(!wx_user['openid']){
        //只有包含code，且code未曾使用，才进行检查，否则需要重新获取code
        if(params['code']
            && (!localStorage.getItem('last_wx_code')
                || localStorage.getItem('last_wx_code')!=params['code'])){
            localStorage.setItem('last_wx_code', params['code']);
            $.get(CHECK_WX_LOGIN_URL, {'code': params['code']}, function(data){
                //alert("enduser(old): " + JSON.stringify(enduser));
                //alert("check_wx_login: "+JSON.stringify(data));
                if (data && (data['mobile'] || data['wx_user'])) {
                    saveLocalUser(data);
                }
            });
        }else{
            var redirect = WX_OAUTH_URL + "&redirect_uri=" + encodeURIComponent(location.href) + "&appid=" + WX_APP_ID;
            location.replace(redirect);
        }
    }
}