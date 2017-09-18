# -*- coding: utf-8 -*-
# 用于检查应有收益，却没有记录的异常情况
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
from basedata.models import Order, bd_update_reward_record, update_cascade_reward_record
from django.db import connection


TASK_NAME = u'检查订单收益任务'
NO_REWARDS = u"没有应记录未记录的收益"
start_time = datetime.datetime.now()
print start_time
rows = None
is_ok = True
try:
    delta = 31 if len(sys.argv) == 1 else sys.argv[1]
    print 'checking orders paid in past %s days' % delta
    sql = '''
        select a.order_no from basedata_order as a
         left join promote_rewardrecord as b on a.order_no = b.order_no
        where a.referrer_id is not null
        and a.pay_date > DATE_ADD(CURDATE(), INTERVAL -%s DAY)
        and a.order_state not in (0, 4, 5, 96, 98, 999)
        and b.order_no is null
    '''
    cursor = connection.cursor()
    cursor.execute(sql, [delta])
    order_nos = [row[0] for row in cursor.fetchall()]
    print order_nos
    if len(order_nos) > 0:
        orders = Order.objects.filter(order_no__in=order_nos)
        err = []
        for order in orders:
            try:
                bd_update_reward_record(sender=Order, obj=order)
                # update_cascade_reward_record(sender=Order, obj=order)
            except Exception, e:
                print e
                err.append("%s: %s" % (order.order_no, e.message))

        msg = "共刷新%s笔订单的收益，失败%s笔" % (len(order_nos), len(err))
        if len(err) > 0:
            is_ok = False
            msg += ":" + "\n".join(err)
    else:
        msg = NO_REWARDS
except Exception, e:
    is_ok = False
    msg = "Check reward FAILED! %s" % (e.message or e.args[1])

end_time = datetime.datetime.now()
try:
    latest = TaskLog.objects.filter(name=TASK_NAME).last()
    if latest and latest.start_time > (datetime.datetime.now() - datetime.timedelta(hours=1)) \
            and latest.exec_result == NO_REWARDS:
        pass  # do not log task status one more time in an hour, if no emails
    else:
        TaskLog.objects.create(
            name=TASK_NAME,
            start_time=start_time,
            end_time=end_time,
            exec_result=msg,
            is_ok=is_ok,
            result_file=''
        )
except Exception, e:
    print 'Save task log error: %s' % (e.message or e.args[1])
