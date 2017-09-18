# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__author__ = 'Winsom'
from tms import settings


# 预览KEY，用于验证，用于创建限时有效的链接
PREVIEW_KEY = 'df86a8fe0c5beb336cd9ede55ac8d5'


# 基础信息
PROVINCES = (
    (u"安徽", u"安徽"),
    (u"澳门", u"澳门"),
    (u"北京", u"北京"),
    (u"重庆", u"重庆"),
    (u"福建", u"福建"),
    (u"甘肃", u"甘肃"),
    (u"广东", u"广东"),
    (u"广西", u"广西"),
    (u"贵州", u"贵州"),
    (u"海南", u"海南"),
    (u"河北", u"河北"),
    (u"河南", u"河南"),
    (u"黑龙江", u"黑龙江"),
    (u"湖北", u"湖北"),
    (u"湖南", u"湖南"),
    (u"吉林", u"吉林"),
    (u"江苏", u"江苏"),
    (u"江西", u"江西"),
    (u"辽宁", u"辽宁"),
    (u"内蒙古", u"内蒙古"),
    (u"宁夏", u"宁夏"),
    (u"青海", u"青海"),
    (u"山东", u"山东"),
    (u"山西", u"山西"),
    (u"陕西", u"陕西"),
    (u"上海", u"上海"),
    (u"四川", u"四川"),
    (u"台湾", u"台湾"),
    (u"天津", u"天津"),
    (u"西藏", u"西藏"),
    (u"香港", u"香港"),
    (u"新疆", u"新疆"),
    (u"云南", u"云南"),
    (u"浙江", u"浙江"),
)
PROVINCES_SET = frozenset((u"安徽", u"澳门", u"北京", u"重庆", u"福建", u"甘肃", u"广东", u"广西", u"贵州", u"海南",
                           u"河北", u"河南", u"黑龙江", u"湖北", u"湖南", u"吉林", u"江苏", u"江西", u"辽宁", u"内蒙古",
                           u"宁夏", u"青海", u"山东", u"山西", u"陕西", u"上海", u"四川", u"台湾", u"天津", u"西藏",
                           u"香港", u"新疆", u"云南", u"浙江"))
UNITS = (
    ('包', '包'),
    ('袋', '袋'),
    ('瓶', '瓶'),
    ('袋', '袋'),
    ('罐', '罐'),
    ('盒', '盒'),
    ('箱', '箱'),
    ('桶', '桶'),
    ('件', '件'),
    ('套', '套'),
    ('散装', '散装')
)

# 订单时效设置
HOURS_TO_REVOKE_ORDER = 1  # hours, 超过该时间未付款的订单将被取消
DAYS_TO_CLOSE_ORDER = 7  # days， 超过该时间的已收货/退款的订单将被自动关闭
DAYS_TO_SIGNOFF_ORDER = 7  # days， 超过该时间的已自提的订单将被自动关闭

# 支付相关配置
PAY_NOT_YET = 0
PAY_AT_STORE = 1  # 线下支付
PAY_VIA_WEIXIN = 2  # 微信
PAY_VIA_ALIPAY = 3  # 支付宝
PAY_VIA_UNIONPAY = 4  # 银联
PAY_NOT_REQUIRED = 998  # 无需付款
PAY_VIA_MIXED = 999  # 混合支付，比如现金不足，使用其它方式支付余额
PAY_VIA_UNKNOWN = 1000  # 混合支付，比如现金不足，使用其它方式支付余额
PAY_TYPES = (
    (PAY_NOT_YET, '未知'),
    (PAY_AT_STORE, '线下支付'),
    (PAY_VIA_WEIXIN, '微信'),
    (PAY_VIA_ALIPAY, '支付宝'),
    (PAY_VIA_UNIONPAY, '银联'),
    (PAY_NOT_REQUIRED, '无需付款'),
    (PAY_VIA_MIXED, '混合支付'),
    (PAY_VIA_UNKNOWN, '未知支付方式'),
)

REWARD_DEFERRED_DAYS = 3  # 默认收益入账后要冻结（到可提现）的时间
# 企业提成比例，百分之X
ENTERPRISE_REWARD_OVERHEAD = 8
GROUP_REWARD_OVERHEAD = 0

# 转发收益提成比例，百分之X
FORWARD_REWARD_RATE = 5

# TODO：to be replaced with huazhu keys
if settings.FAKE_PAYMENT:
    PINGPP_API_KEY = 'sk_test_4mf5uTxxxxxxxxxxxxxxxx'
else:
    PINGPP_API_KEY = 'sk_live_3RTiV3txxxxxxxxxxxxxxx'
PINGPP_APP_ID = 'app_GGOe14xxxxxxxxx'
CHANNEL = {
    "wx_pub": {
        "APP_ID": 'wx9663xxxxxxxxxx',
        "APP_SECRET": '25b7379f7xxxxxxxxxxxxxxxxxxxx'
    },
    "alipay_wap": {

    }
}
PAY_TYPE_MAP = {'wx_pub': PAY_VIA_WEIXIN,
                'alipay_wap': PAY_VIA_ALIPAY}

WX_REDIRECT_URL = '%s/tms-api/pingpp/pay_wx_pub' % settings.APP_URL  # http://abu.podinns.com in production
WX_ACCESS_TOKEN_PATH = settings.BASE_DIR + 'public/wx_access_token.json'


# 快递相关，参考http://www.kuaidi100.com/openapi/api_post.shtml
SHIP_QUERY_KEY = "rYDOhgFB4891"
SHIP_QUERY_URL = "http://www.kuaidi100.com/poll"
SHIP_QUERY_CALLBACK = "%s/callback/update_ship_status" % settings.APP_URL
SHIP_STATUS_ONTHEWAY = 0
SHIP_STATUS_PICKED = 1
SHIP_STATUS_TROUBLE = 2
SHIP_STATUS_SIGNOFF = 3
SHIP_STATUS_REJECT = 4
SHIP_STATUS_DISPATCH = 5
SHIP_STATUS_BACKWAY = 6
SHIP_STATUS_UNKNOWN = 99
SHIP_STATUS_MAP = (
    (SHIP_STATUS_UNKNOWN, "未知"),  # 新增自定义，非kuaidi100状态
    (SHIP_STATUS_ONTHEWAY, "在途，即货物处于运输过程中"),
    (SHIP_STATUS_PICKED, "揽件，货物已由快递公司揽收并且产生了第一条跟踪信息"),
    (SHIP_STATUS_TROUBLE, "疑难，货物寄送过程出了问题"),
    (SHIP_STATUS_SIGNOFF, "签收，收件人已签收"),
    (SHIP_STATUS_REJECT, "退签，即货物由于用户拒签、超区等原因退回，而且发件人已经签收"),
    (SHIP_STATUS_DISPATCH, "派件，即快递正在进行同城派件"),
    (SHIP_STATUS_BACKWAY, "退回，货物正处于退回发件人的途中"),
)

SHIP_SUBSCRIBE_CODE_MAP = {
    '701': '拒绝订阅的快递公司',
    '700': '订阅方的订阅数据存在错误（如不支持的快递公司、单号为空、单号超长等）',
    '600': '您不是合法的订阅者（即授权Key出错）',
    '500': '接口服务器错误',
    '501': '重复订阅',
}

# 自有配送，忽略快递单号，不查询物流状态
SELF_SHIP_VENDORS = ['TWOHOU', 'SELF']

# TOKEN for api access
TWOHOU_API_ACCESS_HOST = 'http://oms.twohou.com:8080'
TWOHOU_API_ACCESS_TOKEN = 'dg7F2aKuWTYxcHZeI1PAQtm4pV3wMyCz'
TWOHOU_API_URL_SYNC_PRODUCT = TWOHOU_API_ACCESS_HOST \
                              + '/api/sync/get_products?agent_code=AYG&sync_token='\
                              + TWOHOU_API_ACCESS_TOKEN

TWOHOU_API_URL_SYNC_PRODUCT_HT = TWOHOU_API_ACCESS_HOST \
                              + '/api/sync/get_products?agent_code=HT&sync_token=s1zoMmYkUrCi3wp5jdxyOqbIaPBJVHfZ'

TWOHOU_API_URL_SYNC_PRODUCT_RJ = TWOHOU_API_ACCESS_HOST \
                              + '/api/sync/get_products?agent_code=RJ&sync_token=18YEwIzWTiZkAvU9jlqSXxJtHePfsFnu'

# 消息类型（用于邮件提醒和微信提醒）
MSG_TYPE_ORDER = 0  # 来订单啦
MSG_TYPE_OUTOFTIME = 1  # 订单处理超时
MSG_TYPE_STOCKLOW = 2  # 商品库存低
MSG_TYPE_OTHER = 3  # 其他
MSG_TYPES = (
    (MSG_TYPE_ORDER, "来订单啦"),
    (MSG_TYPE_OUTOFTIME, "订单处理超时"),
    (MSG_TYPE_STOCKLOW, "商品库存低"),
    (MSG_TYPE_OTHER, "其他"),
)
