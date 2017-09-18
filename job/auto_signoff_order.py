# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
PROJECT_PATH = os.path.abspath('%s/../..' % __file__)
DJANGO_SETTINGS = "tms.settings"

import sys
print(u'Python %s on %s' % (sys.version, sys.platform))
import django
print(u'Django %s' % django.get_version())
sys.path.insert(0, PROJECT_PATH)
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS)
print sys.path
if 'setup' in dir(django):
    django.setup()

import datetime
from tms import settings
from basedata.models import Order
from log.models import TaskLog
from tms.config import DAYS_TO_SIGNOFF_ORDER
from util.renderutil import now, logger
from config.models import AppSetting


TASK_NAME = u'1. 自动签收 - 自提商品'
start_time = datetime.datetime.now()
print TASK_NAME, '@', start_time

target_date = now(settings.USE_TZ) - datetime.timedelta(hours=DAYS_TO_SIGNOFF_ORDER)
rows = None
try:
    orders = Order.objects.filter(order_state=Order.STATE_RECEIVED_BYSELF,
                                  ship_date__lt=target_date,
                                  is_closed=False)
    cnt = 0
    failed = 0
    for order in orders:
        try:
            order.ship_signoff('已自动签收')
            cnt += 1
        except Exception, e:
            failed += 1
            logger.exception(e)

    msg = u"共成功签收%s笔自提货订单，失败%s笔!" % (cnt, failed)
except Exception, e:
    msg = u"操作失败：%s" % (e.message or e.args[1])

print msg

# 发货后15天未签收的渠道订单自动签收，add by sz, 06/24
TASK_NAME = u'2. 自动签收 - 渠道订单'
target_date = now(settings.USE_TZ) - datetime.timedelta(days=15)
rows = None
try:
    orders = Order.objects.filter(order_state=Order.STATE_SHIPPED,
                                  ship_date__lt=target_date,
                                  is_closed=False,
                                  agent_id__isnull=False)
    cnt = 0
    failed = 0
    order_nos = ''
    for order in orders:
        try:
            # order.ship_signoff('已自动签收')
            order.order_state = Order.STATE_RECEIVED
            order.ship_status = '超时，已自动签收'
            order.update_time = now(settings.USE_TZ)
            order.save()
            cnt += 1
            order_nos += order.order_no
            order_nos += ','
        except Exception, e:
            failed += 1
            logger.exception(e)

    msg = u"共成功签收%s笔已超时签收订单，失败%s笔!%s" % (cnt, failed, order_nos)
except Exception, e:
    msg = u"操作失败：%s" % (e.message or e.args[1])

print msg
if len(msg) > 20480:
    msg = msg[0:20479]

end_time = datetime.datetime.now()
try:
    TaskLog.objects.create(
        name=TASK_NAME,
        start_time=start_time,
        end_time=end_time,
        exec_result=msg,
        is_ok=u'失败' in msg,
        result_file=''
    )
except Exception, e:
    # logger.exception(e)
    print u'Save task log error: %s' % (e.message or e.args[1])


TASK_NAME = u'3. 自动签收 - 本地配送订单'  # 48小时后，可进系统设置中修改
start_time = datetime.datetime.now()
print TASK_NAME, '@', start_time

# 默认发货后超过48小时自动签收
target_date = now(settings.USE_TZ) - datetime.timedelta(hours=AppSetting.get('app.hours_to_signoff_local_order', 48))
# target_date = now(settings.USE_TZ)
rows = None
try:
    orders = Order.objects.filter(order_state__in=[Order.STATE_SHIPPED, Order.STATE_RECEIVED_BYSELF],
                                  ship_type=Order.SHIP_VIA_LOCAL,
                                  ship_date__lt=target_date,
                                  is_closed=False)
    cnt = 0
    failed = 0
    for order in orders:
        try:
            order.ship_signoff('已自动签收')
            cnt += 1
        except Exception, e:
            failed += 1
            logger.exception(e)

    msg = u"共成功签收%s笔订单，失败%s笔!" % (cnt, failed)
except Exception, e:
    msg = u"操作失败：%s" % (e.message or e.args[1])

print msg

end_time = datetime.datetime.now()
try:
    TaskLog.objects.create(
        name=TASK_NAME,
        start_time=start_time,
        end_time=end_time,
        exec_result=msg,
        is_ok=u'失败' in msg,
        result_file=''
    )
except Exception, e:
    # logger.exception(e)
    print u'Save task log error: %s' % (e.message or e.args[1])
