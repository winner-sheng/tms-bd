# -*- coding: utf-8 -*-
# 用于统计用户的积分
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
from django.db import connection
from util.renderutil import logger
from config.models import AppSetting
from credit.models import CreditBook


TASK_NAME = u'检查供应商销售收入任务'
NO_REWARDS = u"没有应记录未记录的收入；"
NO_SUPP_REWARDS = u"没有需要更新的收入；"
start_time = datetime.datetime.now()
logger.info(start_time)
rows = None
is_ok = True

try:
    # delta = AppSetting.get('app.supplier_income_deferred_days', 7)
    # nos = 0
    sql = '''
            select uid, nick_name, real_name, mobile from profile_enduser WHERE uid in
            (select uid from credit_creditbook)
          '''
    cursor = connection.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    f = open("/data/credit_summary.txt", 'w')
    # uids = [row[0] for row in cursor.fetchall()]
    print >> f, "uid, credit, nick_name, real_name, mobile"
    # logger.info(uids)
    # for uid in uids:
    for row in results:
        summary = CreditBook.get_credit_summary(row[0])
        total = summary.get('total')
        print >> f, "%s, %d, %s, %s, %s" % (row[0], total, row[1], row[2], row[3])

    f.close()
    cursor.close()

except Exception as e:
    logger.exception(e)
    is_ok = False
    msg = "Check CreditBook FAILED! %s" % (e.message or e.args[1])
