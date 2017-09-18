# -*- coding: utf-8 -*-
import datetime
import time
import urllib
import json
import os

from django.http import HttpResponseRedirect
from pingpp import http_client, util
from django.utils import timezone

from util.renderutil import json_response, get_client, logger
from config.wxpub import CHANNEL
from profile.models import EndUserExt
from tms.config import WX_ACCESS_TOKEN_PATH


def _create_oauth_url_for_code(app_id, redirect_url, more_info=False):
    """
    用于获取授权code的URL地址，此地址用于用户身份鉴权，获取用户身份信息，同时重定向到$redirect_url
    :param app_id: 微信公众号应用唯一标识
    :param redirect_url: 授权后重定向的回调链接地址，重定向后此地址将带有授权code参数，
                         该地址的域名需在微信公众号平台上进行设置，
                         步骤为：登陆微信公众号平台 => 开发者中心 => 网页授权获取用户基本信息 => 修改
    :param order_no: 订单号，用于重定向后继续保留此参数
    :param more_info: FALSE 不弹出授权页面,直接跳转,这个只能拿到用户openid
                      TRUE 弹出授权页面,这个可以通过 openid 拿到昵称、性别、所在地，
    :return: 用于获取授权code的URL地址
    """
    data = dict()
    data['appid'] = app_id
    data['redirect_uri'] = redirect_url
    data['response_type'] = 'code'
    data['scope'] = 'snsapi_userinfo' if more_info else 'snsapi_base'
    data['state'] = 'STATE#wechat_redirect'
    # data['connect_redirect'] = 1
    # data['state'] = order_no
    query_str = urllib.urlencode(data)
    # log.debug("URL to get wx code: " + query_str)

    return "https://open.weixin.qq.com/connect/oauth2/authorize?%s" % query_str


def _create_oauth_url_for_openid(app_id, app_secret, code):
    """
    获取openid的URL地址
    :param app_id: 微信公众号应用唯一标识
    :param app_secret: 微信公众号应用密钥（注意保密）
    :param code: 授权code, 通过调用WxpubOAuth.createOauthUrlForCode来获取
    :return: 获取openid的URL地址
    """
    data = dict()
    data['appid'] = app_id
    data['secret'] = app_secret
    data['code'] = code
    data['grant_type'] = 'authorization_code'
    query_str = urllib.urlencode(data)

    return "https://api.weixin.qq.com/sns/oauth2/access_token?%s" % query_str


def get_wx_openid(app_id, app_secret, code):
    """
    获取微信公众号授权用户唯一标识
    :param app_id: 微信公众号应用唯一标识
    :param app_secret: 微信公众号应用密钥（注意保密）
    :param code: 授权code, 通过调用WxpubOAuth.createOauthUrlForCode来获取
    :return: openid 微信公众号授权用户唯一标识, 可用于微信网页内支付
    """
    url = _create_oauth_url_for_openid(app_id, app_secret, code)
    client = http_client.new_default_http_client()
    rbody, rcode = client.request('GET', url, {})  # 此处为pingpp SDK的bug，需要至少3个参数，只提供2个
    logger.debug("URL to get wx open id: %s" % url)
    logger.debug("get open_id rbody(rcode: %s): %s" % (rcode, rbody))
    if rcode == 200:
        data = util.json.loads(rbody)
        # {u'errcode': 40029, u'errmsg': u'req id: lgH5fA0964ns31, invalid code'}
        return data.get('openid')

    return None


def get_wx_code(request):
    """
    获取微信公众号授权code
    :param request:
        - back_to，指定返回的url，即通过微信oauth接口获取code之后，返回给指定url
    :return:
        重定向到指定的back_to地址，包含code参数
    """
    logger.debug("Referer of get_wx_code: %s" % request.META.get('HTTP_REFERER'))
    # request.session['back_to'] = request.REQUEST.get('back_to', '')
    back_to_url = request.REQUEST.get('back_to', '') or request.META.get('HTTP_REFERER', 'https://store.twohou.com/')
    url = _create_oauth_url_for_code(CHANNEL['wx_pub']['APP_ID'], back_to_url)
    logger.debug("URL for code: %s" % url)
    return HttpResponseRedirect(url)


def get_wx_access_token():
    """
    获取微信公众号基础支持的access_token，用于后续的其他操作
    :return:
        返回一个包含access_token及到期时间的对象，如下：
        {
            "access_token": "yaRJ_fG9_oM3AF7CTuR5Rv2ZJ...",
            "expires_in": 7200
        }
    """
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'
    url = url % (CHANNEL['wx_pub']['APP_ID'], CHANNEL['wx_pub']['APP_SECRET'])
    client = http_client.new_default_http_client()
    rbody, rcode = client.request('GET', url, {})  # 此处为pingpp SDK的bug，需要至少3个参数，只提供2个
    logger.debug("URL to get wx access token: %s" % url)
    data = {}
    if rcode == 200:
        data = util.json.loads(rbody)
    else:
        logger.error("Get wx_access_token failed(%s): %s" % (rcode, rbody))

    return data


def get_wx_user_info(token, openid):
    """
    使用微信公众号基础支持的access_token及用户的openid获取用户基本信息
    :param token: 微信公众号基础支持的access_token
    :param openid: 用户的openid，对指定公众号唯一
    :return:
    """
    url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s'
    url = url % (token, openid)
    client = http_client.new_default_http_client()
    rbody, rcode = client.request('GET', url, {})  # 此处为pingpp SDK的bug，需要至少3个参数，只提供2个
    logger.debug("URL to get wx user info: %s" % url)
    data = {}
    if rcode == 200:
        user_data = util.json.loads(rbody)
        if user_data.get('openid'):
            logger.debug("Get user info: %s" % rbody)
            data = user_data
        else:
            logger.error('Get user data failed: %s' % rbody)
    else:
        logger.error("Get wx_user_info failed(%s): %s" % (rcode, rbody))

    return data


def back_to(request):
    """
    用于地址跳转，当获取到微信公众号的code之后，携带code参数跳回到指定的url
    使用该接口的主要原因是微信公众号的限制，跳转url必须为指定域名、指定目录下的地址，因此借助此中间url可跳转到其它路径下的地址
    :param request:
    :return:
    """
    code = request.REQUEST.get('code')
    logger.debug('back_to query string: %s' % request.get_full_path())
    back_to_url = request.session.get('back_to', '')
    del request.session['back_to']  # just one time use
    logger.debug("back to URL: %s" % back_to_url)
    redirect_url = "%s%scode=%s" % (back_to_url, "&" if "?" in back_to_url else "?", code)
    logger.debug("redirect to URL: %s" % redirect_url)
    return HttpResponseRedirect(redirect_url)


def fetch_token(refresh=False):
    """
    用于获取微信公众号基础支持的access_token，并在指定有效期内（小于微信给定的7200秒，提前10分钟进行刷新）缓存
    :param refresh: 强制刷新access_token
    :return:
        返回access_token字符串
    """
    cur_time = time.mktime(datetime.datetime.now().timetuple())
    wx_access_token = ''
    is_token_expire = True
    token_file = None
    if os.path.exists(WX_ACCESS_TOKEN_PATH) \
            and os.path.isfile(WX_ACCESS_TOKEN_PATH)\
            and cur_time - os.path.getmtime(WX_ACCESS_TOKEN_PATH) < 7000:  # within 7000 seconds
        try:
            logger.debug('read access token from file: %s' % WX_ACCESS_TOKEN_PATH)
            token_file = open(WX_ACCESS_TOKEN_PATH, 'r')
            token = json.loads(token_file.read())
            wx_access_token = token.get('access_token')
            # 200 seconds before expire, treated as expired
            is_token_expire = (int(token.get('expires_in')) - cur_time) < 200
        except Exception, e:
            logger.error('read access token from file failed: %s' % (e.message or e.args[1]))
            logger.exception(e)
        finally:
            token_file and token_file.close()

    if not wx_access_token or is_token_expire or refresh:
        # no token or token expires, get token again
        data = get_wx_access_token()
        if data.get('access_token'):
            wx_access_token = data.get('access_token')
            wx_access_token_expires = cur_time + int(data.get('expires_in')) - 200
            try:
                token_file = open(WX_ACCESS_TOKEN_PATH, 'wb')
                data['expires_in'] = wx_access_token_expires
                token_file.write(json.dumps(data))
            except Exception, e:
                logger.error('Failed to save access token to file: %s' % (e.message or e.args[1]))
                logger.exception(e)
            finally:
                token_file and token_file.close()
    return wx_access_token


def check_wx_login(request):
    """
    检查微信登录情况，如果已登录，直接返回用户的微信账号信息，否则通过OAuth方式获取授权code，
    :param request:
    :return: 微信用户对象
        {
            "province" : "上海",
            "city" : "浦东新区",
            "subscribe_time" : 1432173278,
            "headimgurl" : "http://wx.qlogo.cn/mmopen/YibJsypTkBadsdfu1FAcW4/0",
            "language" : "zh_CN",
            "openid" : "oVxzgjkewgrwerwqqerqwerf71qI",
            "country" : "中国",
            "remark" : "",
            "sex" : 1,
            "subscribe" : 1,
            "nickname" : "XXXXXX",
            "groupid" : 0
        }
    """
    enduser = request.session.get('enduser') or {}
    wx_user = request.session.get('wx_user') or {}
    open_id = wx_user.get('openid')
    if open_id:  # 用户已验证
        logger.debug('user validated: %s | %s' % (enduser, open_id))
        # return renderutil.css_response(wx_user, cache=False)
        if enduser:
            if 'openid' not in enduser:
                enduser['openid'] = open_id
                request.session['enduser'] = enduser
            return json_response(enduser)

    else:
        if not request.REQUEST.get('code'):
            logger.debug('check_wx_login without code or openid')
            return json_response(enduser)
            # server_url = "%s://%s/api/pingpp/check_wx_login" % (request.scheme, request.get_host())
            # url = _create_oauth_url_for_code(CHANNEL['wx_pub']['APP_ID'], server_url)
            # log.debug('check login and redirect to: %s' % url)
            # return HttpResponseRedirect(url)
            # # 用户未验证，需要code参数获取微信openid
            # log.error('Check wx login failed due to CODE missing.')
            # return renderutil.report_error({'error': '缺少code参数'})
        else:
            # 获取微信用户openid
            open_id = get_wx_openid(CHANNEL['wx_pub']['APP_ID'],
                                    CHANNEL['wx_pub']['APP_SECRET'],
                                    request.REQUEST.get('code'))
            logger.debug('fetch wx_user_openid: %s' % open_id)

            if not open_id:
                # return renderutil.css_response({"error": "获取微信用户ID失败"})
                return json_response({"error": "获取微信用户ID失败"})
            else:
                wx_user = {"openid": open_id}
                request.session['wx_user'] = wx_user

    # if 'name' not in wx_user:
    #     access_token = fetch_token()  # 获取令牌
    #     wx_user = get_wx_user_info(access_token, open_id)  # 获取用户详情
    #     log.debug('fetch wx_user: %s' % json_encode(wx_user))

    # 成功获取微信用户信息后，查询或新增EndUserThirdParty记录
    try:
        ex_user = EndUserExt.objects.get(ex_id=open_id,
                                         ex_id_type=EndUserExt.ID_TYPE_WECHAT_OPENID)
    except EndUserExt.DoesNotExist:
        ex_user = EndUserExt.objects.get(ex_id=open_id,
                                         ex_id_type=EndUserExt.ID_TYPE_WECHAT_OPENID)

    client = get_client(request)
    cur_time = timezone.now()

    if not ex_user.uid:  # 未绑定微信用户与商城用户
        if enduser and enduser.get('uid'):  # 已有账号，则绑定，否则不做操作
            ex_user.uid = enduser.get('uid')
        logger.debug('openid not yet binded: %s | %s' % (enduser, open_id))
    else:
        if not enduser.get('uid'):
            # session中如无用户信息，根据uid获取用户数据放到session
            try:
                logger.debug("Get user profile via openid: %s" % open_id)
                end_user = EndUserExt.objects.get(id=ex_user.uid)
                enduser = {"mobile": end_user.mobile,
                           "name": end_user.name or "",
                           # "nick_name": wx_user.get('nick_name') or end_user.name,
                           # "avatar": wx_user.get('headimgurl'),
                           "uidtoken": end_user.token,
                           "uid": end_user.id}
            except EndUserExt.DoesNotExist:
                logger.debug("EndUserExt not found, uid: %s" % ex_user.uid)

    ex_user.last_login = cur_time
    ex_user.last_login_ip = client.get('ip')
    ex_user.last_login_device = client.get('http_agent')
    ex_user.save()
    logger.debug("save ex_user: %s" % ex_user)

    # enduser['wx_user'] = wx_user
    if not enduser.get('openid'):
        enduser['openid'] = open_id
    # enduser['openid'] = wx_user.get('openid')
    # return renderutil.css_response(wx_user)
    request.session['wx_user'] = wx_user
    request.session['enduser'] = enduser
    logger.debug("enduser in session: %s" % request.session['enduser'])
    return json_response(enduser)

