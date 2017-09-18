# -*- coding: utf-8 -*-
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
from django.utils import timezone
from tms import settings
from basedata.models import Order
from log.models import TaskLog
from tms.config import DAYS_TO_CLOSE_ORDER
from buding.models import bd_sync_products

TASK_NAME = u'20. 商品同步'
now = timezone.now() if settings.USE_TZ else datetime.datetime.now()
start_time = datetime.datetime.now()
print start_time
# target_date = now - datetime.timedelta(days=DAYS_TO_CLOSE_ORDER)
rows = None
# 超期的已收货/退款的订单将被自动关闭
try:
    # orders = Order.objects.filter(order_state__in=[Order.STATE_REFUNDED,
    #                                                # Order.STATE_PARTIAL_REFUNDED,
    #                                                Order.STATE_RECEIVED],
    #                               update_time__lt=target_date).exclude(is_closed=True)
    # rows = orders.update(is_closed=True, close_date=now)
    res = bd_sync_products()
    msg = "Total %s products changed or added. Done!" % res
except Exception, e:
    msg = "Sync products FAILED! %s" % (e.message or e.args[1])

print msg

end_time = datetime.datetime.now()
try:
    TaskLog.objects.create(
        name=TASK_NAME,
        start_time=start_time,
        end_time=end_time,
        exec_result=msg,
        is_ok=rows is None,
        result_file=''
    )
except Exception, e:
    print 'Save task log error: %s' % (e.message or e.args[1])
