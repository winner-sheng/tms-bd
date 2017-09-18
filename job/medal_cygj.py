# -*- coding: utf-8 -*-
"""
勋章任务，财源广进，订单推广成交额达到10000的获得此勋章，并奖励6666积分
"""
from __future__ import unicode_literals

import datetime
import os
import sys

import django

PROJECT_PATH = os.path.abspath('%s/../..' % __file__)
DJANGO_SETTINGS = "tms.settings"

print('Python %s on %s' % (sys.version, sys.platform))
print('Django %s' % django.get_version())
sys.path.insert(0, PROJECT_PATH)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS)
print sys.path
if 'setup' in dir(django):
    django.setup()

from django.db import connection
from util.renderutil import logger
from credit.models import UserMedal, MedalCatalog, CreditBook
from log.models import TaskLog

TASK_NAME = u'14. 勋章任务 - 财源广进'
start_time = datetime.datetime.now()
latest = TaskLog.objects.filter(name=TASK_NAME, is_ok=True).last()
since_date = latest.start_time if latest else None

print start_time
rows = None
is_ok = True
medal_code = 'CYGJ'
try:
    try:
        medal = MedalCatalog.objects.get(code=medal_code)
    except:
        is_ok = False
        msg = "勋章[%s]不存在" % medal_code
    else:
        sql = """
        select sum(a.pay_amount) as amount, referrer_id
        from basedata_order as a
        where a.order_state not in (0, 98, 999) %s
        and not exists (
            select uid from credit_usermedal as c
            join credit_medalcatalog as d on c.medal_id = d.id
            where uid = a.referrer_id and d.code = 'CYGJ')
        group by referrer_id
        having amount >=10000
        """
        params = {}
        if since_date:
            sql %= "and referrer_id in (select distinct referrer_id from basedata_order where pay_date > %(since_date)s) "
            params['since_date'] = since_date
        else:
            sql %= ''

        cursor = connection.cursor()
        cursor.execute(sql, params)
        users = [row for row in cursor.fetchall()]
        medal_records = [UserMedal(uid=row[1], medal_id=medal.id) for row in users]
        UserMedal.objects.bulk_create(medal_records)
        credit_books = [CreditBook(uid=row[1], figure=6666, source='完成%s奖励' % TASK_NAME) for row in users]
        CreditBook.objects.bulk_create(credit_books)
        cursor.close()
        msg = '成功为%s人授予%s勋章' % (len(medal_records), medal.name)
except Exception, e:
    logger.exception(e)
    is_ok = False
    msg = u"%s执行失败: %s" % (TASK_NAME, e.message or e.args[1])

print msg
end_time = datetime.datetime.now()
try:
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


