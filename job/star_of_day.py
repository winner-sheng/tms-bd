# -*- coding: utf-8 -*-
"""
每日幸运星活动
每日幸运星是指每天抽取5位有成交记录的导游，给予20元的赏金奖励，短期活动，6月1日开始，为期一个月。
"""
import os
PROJECT_PATH = os.path.abspath('%s/../..' % __file__)
DJANGO_SETTINGS = "tms.settings"

import sys
print('Python %s on %s' % (sys.version, sys.platform))
import django
print('Django %s' % django.get_version())
sys.path.insert(0, PROJECT_PATH)
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS)
print sys.path
if 'setup' in dir(django):
    django.setup()

import datetime
from log.models import TaskLog
from basedata.models import Order
from profile.models import UserAccountBook
from tms import settings
from util.renderutil import now, day_str
import random
import requests
from collections import OrderedDict
from util.jsonall import json_encode


# 活动有效期 2016-06-01 ~ 2016-06-30，第二天开始处理
if datetime.datetime.now() < datetime.datetime(2016, 6, 2) \
        or datetime.datetime.now() > datetime.datetime(2016, 7, 2):
    print u'活动尚未开始或已经结束'
    quit()

day_delta = 1 if len(sys.argv) == 1 else int(sys.argv[1])  # 默认计算前一天的奖励
sh_index = 0 if len(sys.argv) <= 2 else int(sys.argv[1])  # 默认计算前一天的奖励
TASK_NAME = u'每日幸运星活动'
NO_DEALT_ORDER = u"没有成交的订单"
BONUS = 20
DUMMY = False  # if DUMMY, do not create record of UserAccountBook
start_time = datetime.datetime.now()
print start_time
rows = None
is_ok = True
cur_time = now(settings.USE_TZ)
today = datetime.date(cur_time.year, cur_time.month, cur_time.day)
period = (today - datetime.timedelta(days=day_delta),
          today - datetime.timedelta(days=day_delta-1))
day = period[0].strftime('%Y-%m-%d')
print u'抽奖日: %s' % day
json_output = "%sstar_of_day/%s" % (settings.STATIC_ROOT, day)
try:
    if not DUMMY and UserAccountBook.objects.filter(type='bonus',
                                                    extra_type='datetime.date',
                                                    extra_data=day).exists():
        raise ValueError(u'%s已有抽奖记录，不能重复抽奖' % day)

    invalid_states = (Order.STATE_TO_PAY, Order.STATE_OBSOLETE, Order.STATE_REVOKED,
                      Order.STATE_CUSTOMER_SERVICE, Order.STATE_REFUNDED, Order.STATE_RETURN)
    records = Order.objects.filter(pay_date__range=period).exclude(order_state__in=invalid_states)\
        .order_by('pay_date').values_list('order_no', 'pay_date', 'referrer_id')
    # record_dict = dict(records)
    data_dict = OrderedDict()
    for order_no, pay_date, referrer_id in records:
        if referrer_id not in data_dict:
            data_dict[referrer_id] = (order_no, pay_date.strftime('%Y-%m-%d %H:%M:%S'))

    result = {'day': day}
    result['total'] = len(data_dict)
    if result['total'] > 5:
        try:
            if sh_index == 0:
                req = requests.get('http://hq.sinajs.cn/list=sh000001')
                index = round(float(req.content.split(',')[2]))  # 2为昨日收盘价，3为今日收盘价
                result['sh-index'] = int(index)
            else:
                result['sh-index'] = sh_index
            result['data'] = data_dict.items()
            lucky_no = result['sh-index']
            ids = data_dict.keys()
            ids.extend(ids[:5])
            ids.insert(0, None)
            m = lucky_no % result['total']
            m = result['total'] if m == 0 else m
            result['stars'] = ids[m:m+5]
        except:
            raise ValueError(u'获取上证指数失败！')
    else:
        result['data'] = data_dict.items()
        result['stars'] = data_dict.keys()


    # {
    #     'total' : 1,  （当天参与抽奖总人数，不重复累计）
    #     'data' : [('test_123456789', ('D160523RZLQKW', '2016-05-23 00:00:28'))],  (所有用户uid及当日首单订单号、付款时间列表)
    #     'day' : '2016-05-23', (抽奖日，一般次日凌晨抽前一天的，此处抽奖日是指前一天的日期)
    #     'sh-index': 2880, (上证指数，如果总数不超过5个，则不取该数)
    #     'stars' : ['test_123456789']  (中奖者uid列表)
    # }

    print "saving result to %s" % json_output
    writer = open(json_output, 'wb+')
    writer.write(json_encode(result))
    writer.close()

    # samples = set([referrer_id for order_no, referrer_id in records])
    # stars = []
    # if len(samples) <= 5:
    #     stars = samples
    # else:
    #     stars = random.sample(samples, 5)

    if not DUMMY:
        for star_uid in result['stars']:
            UserAccountBook.objects.create(uid=star_uid,
                                           type='bonus',
                                           figure=BONUS,
                                           account_desc=u'每日幸运星（%s）' % day,
                                           extra_type='datetime.date',
                                           extra_data=day)

    rows = len(result['stars'])
    if rows > 0:
        msg = u'从%s人中抽取%s人获得[%s]幸运星奖励￥%s' % (len(result['data']), rows, day, BONUS)
    else:
        msg = NO_DEALT_ORDER
except Exception, e:
    is_ok = False
    msg = u"每日幸运星抽奖失败: %s" % (e.message or e.args[1])

print msg

end_time = datetime.datetime.now()
try:
    latest = TaskLog.objects.filter(name=TASK_NAME).last()
    if not DUMMY:
        TaskLog.objects.create(
            name=TASK_NAME,
            start_time=start_time,
            end_time=end_time,
            exec_result=msg,
            is_ok=is_ok,
            result_file=json_output
        )
except Exception, e:
    print 'Save task log error: %s' % (e.message or e.args[1])


