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
from basedata.models import Order, bd_update_reward_record, bd_update_cascade_reward_record
from django.db import connection
from util.renderutil import logger


TASK_NAME = u'检查订单收益任务'
NO_REWARDS = u"没有应记录未记录的收益；"
NO_CASCADE_REWARDS = u"没有应记录未记录的伙伴激励；"
start_time = datetime.datetime.now()
logger.info(start_time)
rows = None
is_ok = True
try:
    # delta = 7 if len(sys.argv) == 1 else sys.argv[1]
    # print 'checking orders paid in past %s days' % delta
    print 'checking orders paid in past days'
    # 裸价下单订单不计算导游提成
    sql = '''
            select a.order_no from basedata_order as a
             left join promote_rewardrecord as b on a.order_no = b.order_no
            where a.referrer_id is not null
            and a.order_state not in (0, 4, 5, 96, 98, 999)
            and b.order_no is null
            and a.split_required = 0
            and a.settle = 0
            and a.order_date > '2017-08-23'
            and a.store_code in (select code from buding_saleshop)
    '''
    # and a.pay_date > DATE_ADD(CURDATE(), INTERVAL -%sDAY)
    cursor = connection.cursor()
    # cursor.execute(sql, [delta])
    cursor.execute(sql)
    order_nos = [row[0] for row in cursor.fetchall()]
    logger.info(order_nos)
    if len(order_nos) > 0:
        orders = Order.objects.filter(order_no__in=order_nos, split_required=False)
        err = []
        for order in orders:
            try:
                bd_update_reward_record(sender=Order, obj=order)
                # bd_update_cascade_reward_record(sender=Order, obj=order)
            except Exception as e:
                logger.exception(e)
                err.append("%s: %s" % (order.order_no, e.message))

        msg = "共刷新%s笔订单的直接收益，失败%s笔；" % (len(order_nos), len(err))
        if len(err) > 0:
            is_ok = False
            msg += ":" + "\n".join(err)
    else:
        msg = NO_REWARDS

    # cursor.close()

    # 本地配送、裸价下单订单不计算二级分佣
#     select
#     a.order_no
#     from basedata_order as a
#
#     join
#     profile_enduser as c
#     on
#     a.referrer_id = c.uid and c.referrer is not null
#     left
#     join
#     promote_rewardrecord as b
#     on
#     a.order_no = b.order_no and b.referrer_id = c.referrer
# where
# a.referrer_id is not null
# and a.order_state not in (0, 4, 5, 96, 98, 999)
# and b.order_no is null
# and a.settle = 0
# and a.split_required = 0
# and a.order_date > '2017-08-23'
# and a.store_code in (select
# code
# from buding_saleshop)
#     sql = '''
#             select a.order_no from basedata_order as a
#              left join promote_rewardrecord as b on a.order_no = b.order_no
#             where a.referrer_id is not null
#             and a.order_state not in (0, 4, 5, 96, 98, 999)
#             and b.order_no is null
#             and a.split_required = 0
#             and a.settle = 0
#             and a.order_date > '2017-08-23'
#             and a.store_code in (select code from buding_saleshop)
#     '''
#     cursor = connection.cursor()
    # cursor.execute(sql, [delta])
    # cursor.execute(sql)
    # order_nos = [row[0] for row in cursor.fetchall()]
    # logger.info(order_nos)
    if len(order_nos) > 0:
        orders = Order.objects.filter(order_no__in=order_nos, split_required=False)
        err = []
        for order in orders:
            try:
                bd_update_cascade_reward_record(sender=Order, obj=order)
            except Exception as e:
                logger.exception(e)
                err.append("%s: %s" % (order.order_no, e.message))

        msg += "共刷新%s笔订单的伙伴，失败%s笔" % (len(order_nos), len(err))
        if len(err) > 0:
            is_ok = False
            msg += ":" + "\n".join(err)
    else:
        msg += NO_CASCADE_REWARDS
    print msg
    cursor.close()
    logger.debug(msg)
except Exception as e:
    logger.exception(e)
    is_ok = False
    msg = "Check reward FAILED! %s" % (e.message or e.args[1])

end_time = datetime.datetime.now()
try:
    latest = TaskLog.objects.filter(name=TASK_NAME, is_ok=True).last()
    if latest and latest.start_time > (datetime.datetime.now() - datetime.timedelta(hours=1)) \
            and NO_REWARDS in latest.exec_result and NO_CASCADE_REWARDS in latest.exec_result:
        logger.info("ignore task log")
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
except Exception as e:
    logger.exception(e)
    logger.info('Save task log error: %s' % (e.message or e.args[1]))
