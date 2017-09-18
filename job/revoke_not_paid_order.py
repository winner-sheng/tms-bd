# -*- coding: utf-8 -*-
# 每10分钟允许一次，撤销超过1个小时未付款的订单
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
from tms.config import HOURS_TO_REVOKE_ORDER
from util.renderutil import now

TASK_NAME = u'16. 超时未付款订单自动废弃'
start_time = datetime.datetime.now()
print TASK_NAME, '@', start_time

target_date = now(settings.USE_TZ) - datetime.timedelta(hours=HOURS_TO_REVOKE_ORDER)
rows = None
# 超过24小时未支付的订单将被自动取消
try:
    orders = Order.objects.filter(order_state=Order.STATE_TO_PAY,
                                  create_time__lt=target_date,
                                  is_closed=False)
    rows = orders.update(order_state=Order.STATE_OBSOLETE, close_date=now(settings.USE_TZ))
    msg = u"共取消%s笔未付款订单!" % rows
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
