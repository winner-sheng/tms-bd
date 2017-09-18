# -*- coding: utf-8 -*-
# 用于检查供应商销售收入任务
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
# from basedata.models import Order, update_reward_record, update_cascade_reward_record
from django.db import connection
from util.renderutil import logger
from config.models import AppSetting
from vendor.models import SupplierSalesIncome


TASK_NAME = u'检查供应商销售收入任务'
NO_REWARDS = u"没有应记录未记录的收入；"
NO_SUPP_REWARDS = u"没有需要更新的收入；"
start_time = datetime.datetime.now()
logger.info(start_time)
rows = None
is_ok = True

if start_time < datetime.datetime(2017, 5, 10, 0, 0, 0):
    print 'run date is wrong, will be started after 2017-05-10.'
    exit()

try:
    delta = AppSetting.get('app.supplier_income_deferred_days', 7)
    nos = 0
    sql = '''
            select a.order_no from basedata_order as a
            left join vendor_suppliersalesincome as b on a.order_no = b.order_no
            where a.signoff_date > '2017-05-01'
            and a.signoff_date < DATE_ADD(CURDATE(), INTERVAL -%s DAY)
            and a.order_state not in (0, 4, 5, 96, 98, 999)
            and a.agent_id is NULL
            and b.status = 1
    '''
    cursor = connection.cursor()
    cursor.execute(sql, [delta])
    order_nos = [row[0] for row in cursor.fetchall()]
    logger.info(order_nos)
    if len(order_nos) > 0:
        supp_sis = SupplierSalesIncome.objects.filter(order_no__in=order_nos)
        err = []
        for supp_si in supp_sis:
            try:
                supp_si.charge()
                nos += 1
            except Exception as e:
                logger.exception(e)
                err.append("%s: %s" % (supp_si.order_no, e.message))

        msg = "共刷新%s笔供应商收入；" % nos
        if len(err) > 0:
            is_ok = False
            msg += ":" + "\n".join(err)
    else:
        msg = NO_REWARDS
    cursor.close()

    logger.debug(msg)
except Exception as e:
    logger.exception(e)
    is_ok = False
    msg = "Check SupplierSalesIncome charge_back FAILED! %s" % (e.message or e.args[1])

end_time = datetime.datetime.now()
try:
    latest = TaskLog.objects.filter(name=TASK_NAME, is_ok=True).last()
    if latest and latest.start_time > (datetime.datetime.now() - datetime.timedelta(hours=1)) \
            and NO_REWARDS in latest.exec_result and NO_SUPP_REWARDS in latest.exec_result:
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
