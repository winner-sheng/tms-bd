# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import urllib2
from tms import settings
import sys
import re
import json
import httplib
import urllib
from util.renderutil import logger
__author__ = 'Winsom'


SIGNATURE = "【布丁】"
SIGNATURE_FXJ = "【土猴特产分享家】"

MOBILE_PATTERN = re.compile(r'^1\d{10,12}$')
def utf8(value):
    if isinstance(value, unicode) and sys.version_info < (3, 0):
        return value.encode('utf-8')
    else:
        return value


# 土猴交易平台短信接口
# NEW_ORDER = "来订单啦！您有一笔新订单{{order_no}}，总金额{{pay_amount}}，用户选购了：{{shop_detail}}。请尽快处理。{{short_url}}"
# STOCK_SHORTAGE = "亲，您的商品 {{product_name}} 库存告急，当前仅剩 {{stock_volume}} 件。请尽快补货哦！"
# STOCK_SHORTAGE = "亲，您的商品 {{product_name}} 库存告急，当前仅剩 {{stock_volume}} 件。请尽快补货哦！"
# REQUEST_REFUND = "亲，订单{{order_no}}申请退货/退款哦。 原因（{{reason}}）。 请及时处理！"
SMS_TEMPLATE_NEW_ORDER = "NEW_ORDER"
SMS_TEMPLATE_STOCK_SHORTAGE = "STOCK_SHORTAGE"
# SMS_TEMPLATE_REVOKE_ORDER = "REVOKE_ORDER"
SMS_TEMPLATE_REQUEST_REFUND = "REQUEST_REFUND"
SMS_ORDER_SHIPPING = "您的包裹%(ship_code)s已经随%(ship_vendor)s向您奔去啦！" \
                     "请关注微信公众号：布丁，回复微信消息%(mobile)s%(order_suffix)s查询详情。"
SMS_NOTE_TO_RECEIVER = "亲，您的朋友赠送给您#%(product)s#礼物，还给您捎来一段话：%(note)s"
SMS_ORDER_SIGNOFF = "亲，感谢您体验我们的特产服务！欢迎关注微信公众号：布丁。" \
                    "获得更多地道中华特产，做旅行特产分享家！"
SMS_ORDER_SHIPPING_FXJ = "您的包裹%(ship_code)s已经随%(ship_vendor)s向您奔去啦！" \
                     "请关注微信公众号：土猴特产分享家，回复微信消息%(mobile)s%(order_suffix)s查询详情。"
SMS_ORDER_SIGNOFF_FXJ = "亲，感谢您体验我们的特产服务！欢迎关注微信公众号：土猴特产分享家。" \
                    "获得更多地道中华特产，做全国特产分享家！"


'''
curl -X POST \
  -H "X-AVOSCloud-Application-Id: g0bbzujeqaeq7vzao9did7y8uzky397jwlm7pc3lmwsksi9f" \
  -H "X-AVOSCloud-Application-Key: kc5l0htl2pw521um4cpal5k73j061pzmtwbi2e413zl23y9x" \
  -H "Content-Type: application/json" \
  -d '{"mobilePhoneNumber": "13817550941", "template":"SMS_TEMPLATE_VERIFICATION_CODE","code":"666666"}' \
  https://api.leancloud.cn/1.1/requestSmsCode
'''


def is_valid_mobile(mobile):
    return not not MOBILE_PATTERN.match(mobile)


class LeanSms(object):
    def __call__(self, mobile, message, data):
        data = data or {}
        url = 'https://api.leancloud.cn/1.1/requestSmsCode'
        data.update({"mobilePhoneNumber": mobile,
                     "template": message})
        req = urllib2.Request(url, json.dumps(data))
        req.add_header('Content-Type', 'application/json')
        req.add_header('X-AVOSCloud-Application-Id', 'nqHl6GGpsotSQiAHNkDER8hw-gzGzoHsz')
        req.add_header('X-AVOSCloud-Application-Key', 'hWvUF2QCuvAeG1EbVj5xvLRx')

        resp = urllib2.urlopen(req)
        result = resp.read()
        return result


class Zz253Sms(object):
    # 服务地址
    host = 'sms.253.com'
    # 端口号
    port = 80
    # 版本号
    version = "v1.1"
    # 查账户信息的URI
    balance_get_uri = "/msg/QueryBalance"
    # 智能匹配模版短信接口的URI
    sms_send_uri = "/msg/HttpBatchSendSM"
    # 创蓝账号
    account = "N1410803"
    # 创蓝密码
    password = "SPnF3Lf6Ip6db9"
    # 签名
    signature = '【爱游购】'
    # signature_FXJ = '【土猴特产分享家】'


    @staticmethod
    def get_user_balance():
        """
        取账户余额
        """
        conn = httplib.HTTPConnection(Zz253Sms.host, port=Zz253Sms.port)
        conn.request('GET', Zz253Sms.balance_get_uri + "?account=" + Zz253Sms.account + "&pswd=" + Zz253Sms.password)
        response = conn.getresponse()
        response_str = response.read()
        conn.close()
        return response_str

    def __call__(self, mobile, message, data=None, agent_id=None):
        sig = SIGNATURE_FXJ if agent_id == 12 else SIGNATURE
        if data and isinstance(data, dict):
            message %= data
        params = urllib.urlencode({'account': Zz253Sms.account,
                                   'pswd': Zz253Sms.password,
                                   'msg': "%s%s" % (sig, message),
                                   'mobile': mobile,
                                   'needstatus': True,
                                   'extno': ''})

        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        conn = httplib.HTTPConnection(Zz253Sms.host, port=Zz253Sms.port, timeout=30)
        conn.request("POST", Zz253Sms.sms_send_uri, params, headers)
        response = conn.getresponse()
        response_str = response.read()
        conn.close()
        return response_str

    @staticmethod
    def send_sms(text, mobile):
        """
        能用接口发短信
            代码	说明
            0	提交成功
            101	无此用户
            102	密码错
            103	提交过快（提交速度超过流速限制）
            104	系统忙（因平台侧原因，暂时无法处理提交的短信）
            105	敏感短信（短信内容包含敏感词）
            106	消息长度错（>536或<=0）
            107	包含错误的手机号码
            108	手机号码个数错（群发>50000或<=0;单发>200或<=0）
            109	无发送额度（该用户可用短信数已使用完）
            110	不在发送时间内
            111	超出该账户当月发送额度限制
            112	无此产品，用户没有订购该产品
            113	extno格式错（非数字或者长度不对）
            115	自动审核驳回
            116	签名不合法，未带签名（用户必须带签名的前提下）
            117	IP地址认证错,请求调用的IP地址不是系统登记的IP地址
            118	用户没有相应的发送权限
            119	用户已过期
            120	测试内容不是白名单
        """
        sig = SIGNATURE_FXJ if agent_id == 12 else SIGNATURE
        params = urllib.urlencode({'account': Zz253Sms.account,
                                   'pswd': Zz253Sms.password,
                                   'msg': "%s%s" % (sig, text),
                                   'mobile': mobile,
                                   'needstatus': True,
                                   'extno': ''})
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        conn = httplib.HTTPConnection(Zz253Sms.host, port=Zz253Sms.port, timeout=30)
        conn.request("POST", Zz253Sms.sms_send_uri, params, headers)
        response = conn.getresponse()
        response_str = response.read()
        conn.close()
        return response_str


SMS_MESSENGER = Zz253Sms


def send_sms(mobile, template, data=None, agent_id=None):
    if settings.FAKE_SMS:
        return True

    if isinstance(mobile, list):
        mobiles = mobile
    elif ',' in mobile:
        mobiles = mobile.split(',')
    else:
        mobiles = [mobile]

    mobiles = set(mobiles)
    err = []
    for m in mobiles:
        if not is_valid_mobile(m):
            err.append("手机号[%s]无效" % m)
            continue
        try:
            print SMS_MESSENGER()(m, template, data, agent_id)
        except Exception, e:
            logger.exception(e)
            err.append('发送短信到[%s]失败：%s' % (m, e.message))

    return len(err) == 0 or err


if __name__ == '__main__':
    mobile = "188xxxxxxxx"
    text = "【创蓝文化】您的验证码是1234"

    # 查账户余额
    print(Zz253Sms.get_user_balance())
    # 调用智能匹配模版接口发短信
    print(Zz253Sms.send_sms(text, mobile))