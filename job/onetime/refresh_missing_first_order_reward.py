# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

PROJECT_PATH = os.path.abspath('%s/../../..' % __file__)
DJANGO_SETTINGS = "tms.settings"

import sys
print('Python %s on %s' % (sys.version, sys.platform))
import django
print('Django %s' % django.get_version())
sys.path.insert(0, PROJECT_PATH)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS)
print sys.path
if 'setup' in dir(django):
    django.setup()

from django.db import connection
from profile.models import UserAccountBook

sql = """
    select a.referrer_id, a.order_no, a.pay_date, c.nick_name, c.real_name, a.buyer_id from basedata_order as a
    join
    (select referrer_id, min(pay_date) as min_pay_date
    from basedata_order
    where referrer_id is not null
    and not exists(select uid, type, account_desc
    from profile_useraccountbook
    where type ='bonus'
     and account_desc like '首单奖励%' and uid=referrer_id)
    group by referrer_id
    having month(min_pay_date) = 6) as b on a.referrer_id = b.referrer_id and a.pay_date = b.min_pay_date
    join profile_enduser as c on a.referrer_id=c.uid;
"""
cursor = connection.cursor()
cursor.execute(sql)
cnt = 0
success_cnt = 0
for record in cursor.fetchall():
    cnt += 1
    if UserAccountBook.objects.filter(uid=record[0],
                                      type='bonus',  # 首单双赢奖励
                                      account_desc__startswith=u'首单奖励'
                                      ).exists():
        pass  # no duplicate bonus
    else:
        UserAccountBook.objects.create(uid=record[0],
                                       type='bonus',  # 首单双赢奖励
                                       figure=20,
                                       account_desc=u'首单奖励[%s]' % record[1],
                                       extra_type='basedata.Order',
                                       extra_data=record[1],
                                       create_time=record[2])
        success_cnt += 1
        print record[1], ' referred by ', record[0], ' @ ', record[2], ' rewarded'

print "Total ", cnt, ' missing, ', success_cnt, ' fixed'