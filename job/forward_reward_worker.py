# -*- coding: utf-8 -*-
# 用于检查商品转发收益任务
# import urllib2
# import urllib

import os
PROJECT_PATH = os.path.abspath('%s/../..' % __file__)
DJANGO_SETTINGS = "tms.settings"

import sys
print('Python %s on %s' % (sys.version, sys.platform))
import django
print('Django %s' % django.get_version())
sys.path.insert(0, PROJECT_PATH)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS)
print sys.path

import datetime
from log.models import TaskLog, WechatMsgLog
from django.db import connection
from util.renderutil import logger
from config.models import AppSetting
from profile.models import UserAccountBook, EndUser
from credit.models import CreditBook
from basedata.models import OrderItem

import socket
# IS_LOCAL_DEV = socket.gethostname() == 'YYPC'
IS_LOCAL_DEV = socket.gethostname() in ['localhost', 'ShengdeMacBook-Air.local', 'YYPC', 'ShengdeAir']  # 'YYPC'
IS_REMOTE_DEV = socket.gethostname() in ['twohou-hotel', 'iZ23tgnmxyaZ']  # iZ23tgnmxyaZ
WECHAT_MSG_URL = 'http://abuhome.podinns.com/itravelbuy-api/onInformShareGetIntegral?%s'

# if IS_LOCAL_DEV:
#     WECHAT_MSG_URL = 'http://192.168.10.132:4000/itravelbuy-api/onInformShareGetIntegral?%s'
# elif IS_REMOTE_DEV:
#     WECHAT_MSG_URL = 'http://test2.itravelbuy.twohou.com/itravelbuy-api/onInformShareGetIntegral?%s'

TASK_NAME = u'9. 商品转发收益任务'
NO_REWARDS = u"没有需记录的转发收益"
NO_CASCADE_REWARDS = u"没有应记录未记录的伙伴激励"
start_time = datetime.datetime.now()
logger.info(start_time)
rows = None
is_ok = True
msg = ''
orders = ''
# uids = ''
n = 0

rate = AppSetting.get('app.forward_reward_rate', 5.0)

try:
    delta = 7 if len(sys.argv) == 1 else sys.argv[1]
    print 'checking forward_reward for orders signoff_date in past %s days' % delta
    #  提取delta天前以签收的订单项（包含了转发者信息的）
    if IS_LOCAL_DEV or IS_REMOTE_DEV:
        sql = '''
                select id, referrer_id, deal_price, settle_price, pcs, forward_uid, order_id, product_id from basedata_orderitem
                where basedata_orderitem.order_id in
                (select order_no from basedata_order as b
                where order_state = 3
                and ship_type <> 'local')
                and LENGTH(basedata_orderitem.forward_uid) > 0
                and has_rewarded = 0
                and referrer_id <> forward_uid
              '''
    else:
        sql = '''
                select id, referrer_id, deal_price, settle_price, pcs, forward_uid, order_id, product_id from basedata_orderitem
                where basedata_orderitem.order_id in
                (select order_no from basedata_order as b
                where signoff_date < DATE_ADD(CURDATE(), INTERVAL -%s DAY)
                and order_state = 3
                and ship_type <> 'local')
                and LENGTH(basedata_orderitem.forward_uid) > 0
                and has_rewarded = 0
                and referrer_id <> forward_uid
              '''
    cursor = connection.cursor()
    if IS_LOCAL_DEV or IS_REMOTE_DEV:
        cursor.execute(sql)
    else:
        cursor.execute(sql, [delta])
    results = cursor.fetchall()
    # f = open("/data/credit_summary.txt", 'w')
    # uids = [row[0] for row in cursor.fetchall()]
    # print >> f, "uid, credit, nick_name, real_name, mobile"
    # logger.info(uids)
    # for uid in uids:
    for row in results:
        item_id = row[0]
        referrer_id = row[1]
        deal_price = row[2]
        settle_price = row[3]
        pcs = row[4]
        forward_uid = row[5]
        order_id = row[6]
        product_id = row[7]

        credit = int(rate * float(deal_price) * pcs + 0.5)
        settle_cost = credit * 1.0 / 100

        user = EndUser.objects.get(uid=forward_uid)
        username = "%s/%s" % (user.real_name or '-', user.nick_name or user.ex_nick_name or '-')

        UserAccountBook.objects.create(uid=referrer_id,
                                       type='deduct',  # 扣除转发分佣
                                       figure=settle_cost,
                                       is_income=False,
                                       account_desc=u'订单[%s]中的商品[%s],扣除游客转发分佣给[%s]' % (order_id, product_id, username),
                                       extra_type='basedata.Order',
                                       extra_data=order_id)

        CreditBook.objects.create(uid=forward_uid,
                                  figure=credit,
                                  is_income=True,
                                  source=u'您分享的商品[%s],生成订单[%s],获得积分' % (product_id, order_id),
                                  extra_type='basedata.Order',
                                  extra_data=order_id)

        WechatMsgLog.put_in_queue(uid=forward_uid,
                                  subject=u'积分变动提醒',
                                  body=u'您分享的商品[%s], 生成订单[%s], 获得积分: %d' % (product_id, order_id, credit)
                                  )

        # # 定义一个要提交的数据数组(字典)
        # data = {}
        # data['uid'] = forward_uid
        # data['integral'] = str(credit)
        # # 定义post的地址
        # # url = 'http://192.168.10.132:4000/itravelbuy-api/onInformShareGetIntegral?%s'
        # # url = 'http://test2.itravelbuy.twohou.com/itravelbuy-api/onInformShareGetIntegral?%s'
        # # url = 'http://abuhome.podinns.com/itravelbuy-api/onInformShareGetIntegral?%s'
        # get_data = urllib.urlencode(data)
        # # 提交，发送数据
        # req = urllib2.urlopen(WECHAT_MSG_URL % get_data)
        # # 获取提交后返回的信息
        # content = req.read()

        order_item = OrderItem.objects.get(id=item_id)
        order_item.has_rewarded = True
        order_item.reward_time = datetime.datetime.now()
        order_item.save()

        n += 1
        orders += '[%s/%s];' % (order_id, product_id)

    #
    #
    #     summary = CreditBook.get_credit_summary(row[0])
    #     total = summary.get('total')
    #     print >> f, "%s, %d, %s, %s, %s" % (row[0], total, row[1], row[2], row[3])
    #
    # f.close()

    if n > 0:
        msg = "共刷新%d笔订单的转发收益: %s" % (n, orders)
    else:
        msg = NO_REWARDS
    cursor.close()

except Exception as e:
    logger.exception(e)
    is_ok = False
    msg = "Check forward_reward FAILED! %s" % (e.message or e.args[1])

end_time = datetime.datetime.now()

# http://192.168.10.132:4000/itravelbuy-api/onInformShareGetIntegral?uid=686358eac965405c9721f7ba387e037c&integral=222

try:
    TaskLog.objects.create(
        name=TASK_NAME,
        start_time=start_time,
        end_time=end_time,
        exec_result=msg,
        is_ok=is_ok,
        result_file=''
    )
except Exception as e:
    logger.exception(e)
    logger.info('Save task log error: %s' % (e.message or e.args[1]))
