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
from log.models import TaskLog
from promote.models import RewardRecord
from basedata.models import Order, update_cascade_reward_record
from django.db.models import Q, F
from config.models import AppSetting
from tms import settings
from util.renderutil import now
from django.db import connection

TASK_NAME = u'伙伴激励收益入账'
NO_REWARDS = u"没有应入账收益记录"
start_time = datetime.datetime.now()
print start_time
rows = None
is_ok = True
# 领取伙伴销售奖励的资质要求
lower_limit = int(AppSetting.get('app.lower_limit_for_cascade_reward', 5))
try:
    # 先检查上月的伙伴激励收益是否有未记录的情形（订单支付时间为上个月）
    # 如果有，补充收益记录
    # 注意：是否添加收益记录以订单是否支付为准
    # sql = """
    #     select order_no from promote_rewardrecord
    #     where achieved_time is NULL
    #     and account_no is NULL
    #     and status = 0
    #     and order_no IN
    #     (select order_no from basedata_order
    #     where order_state = 3
    #     and signoff_date between '2017-04-01' and '2017-05-10'
    #     and ship_type = 'express'
    #     and settle = 0)
    # """
    sql = """
        select order_no from basedata_order
        where order_state = 3
        and signoff_date between '2017-04-01' and '2017-05-10'
        and ship_type <> 'local'
        and split_required = 0
        and settle = 0
    """
    cursor = connection.cursor()
    cursor.execute(sql)
    order_nos = [order_no for order_no, in cursor.fetchall()]
    print u'共有%s笔订单的小伙伴激励收益未结算' % len(order_nos)
    reward_cnt = 0
    if len(order_nos) > 0:
        # orders = Order.objects.filter(order_no__in=order_nos)
        # for order in orders:
        #     print order
        #     update_cascade_reward_record(sender=None, obj=order)
        settle_cnt = RewardRecord.objects.filter(status=RewardRecord.REWARD_TBD,
                                              reward_type=RewardRecord.TYPE_PARTNER_REWARD,
                                              # referrer_id__in=referrers,
                                              create_time__lt='2017-05-01',
                                              create_time__gt='2017-04-01',
                                              order_no__in=order_nos,
                                              account_no__isnull=True)\
                .update(status=RewardRecord.REWARD_ACHIEVED, achieved=F('reward'))
            # 上面是设置收益结算状态，以下逐一将收益入账

        records = RewardRecord.objects.filter(status=RewardRecord.REWARD_ACHIEVED,
                                              reward_type=RewardRecord.TYPE_PARTNER_REWARD,
                                              # referrer_id__in=referrers,
                                              create_time__lt='2017-05-01',
                                              create_time__gt='2017-04-01',
                                              order_no__in=order_nos,
                                              account_no__isnull=True)
        for r in records:
            try:
                res = r.charge(frozen_days=0)
                if res:
                    reward_cnt += 1
            except Exception, e:
                print e.message
                pass

        if reward_cnt > 0:
            msg = u'共结算%s笔' % reward_cnt
            print msg
        else:
            msg = NO_REWARDS

    cursor.close()

#     # 先取用户列表中包含推荐人的记录，且满足推荐人在上月有至少5单成交（有付款，未退款）的订单，
#     # 且被推荐人在上月有被用户签收的订单
#     sql = """
#             SELECT a.uid, a.referrer
#             FROM profile_enduser AS a
#             WHERE a.referrer IS NOT NULL
#             %s
#             AND EXISTS(
#                 SELECT order_no from basedata_order as c
#                 WHERE c.referrer_id = a.uid AND
#                 signoff_date BETWEEN DATE_ADD(CURDATE()- DAY(CURDATE())+1, INTERVAL -12 MONTH)
#                             AND DATE_ADD(CURDATE(), INTERVAL - DAY(CURDATE())+1 DAY)
#                 and c.order_state not in (0, 4, 5, 96, 98, 999)
#             );
#         """
#     cursor = connection.cursor()
#     if lower_limit > 0:
#         sql %= """
#         AND EXISTS (
#                 SELECT referrer_id, COUNT(order_no) AS cnt
#                 FROM basedata_order AS b
#                 WHERE b.referrer_id = a.referrer AND
#                 pay_date BETWEEN DATE_ADD(CURDATE()- DAY(CURDATE())+1, INTERVAL -1 MONTH)
#                             AND DATE_ADD(CURDATE(), INTERVAL - DAY(CURDATE())+1 DAY)
#                 and b.order_state not in (0, 4, 5, 96, 98, 999)
#                 GROUP BY b.referrer_id
#                 HAVING cnt >= %s)
#         """
#         cursor.execute(sql, (lower_limit,))
#     else:
#         sql %= ''
#         cursor.execute(sql)
#     cur_time = now(settings.USE_TZ)
#     if cur_time.month == 1:  # 跨年处理
#         cur_month = 12
#         cur_year = cur_time.year-1
#     else:
#         cur_month = cur_time.month-1
#         cur_year = cur_time.year
#     date_range = (datetime.date(2016, 6, 1),
#                   datetime.date(cur_time.year, cur_time.month, 1))
#     cur_month_start = datetime.date(cur_time.year, cur_time.month, 1)
#     # date_range = (datetime.date(cur_time.year, cur_time.month-1, 1),
#     #               datetime.date(cur_time.year, cur_time.month, 1))
#     # cur_month_start = datetime.date(cur_time.year, cur_time.month, 1)
#
#     reward_cnt = referrer_cnt = 0
#     referrers_dict = dict([(uid, referrer) for uid, referrer in cursor.fetchall()])
#     referrers = set(referrers_dict.values())
#     # 获取已签收订单号
#     order_nos = Order.objects.filter(signoff_date__range=date_range,
#                                      order_state=Order.STATE_RECEIVED,
#                                      referrer_id__in=referrers_dict.keys()).values_list('order_no', flat=True)
#     referrer_cnt = len(referrers)
#     cancelled_cnt = 0
#     if lower_limit > 0:
#         # 只撤销已签收的订单收益，未签收的顺延到下个结算周期
#         # 取未满5单的推广人对应的收益订单列表
#         sql = """
#             SELECT bo2.order_no # , a.uid, a.referrer, bo.cnt
#                 FROM profile_enduser AS a
#                 join (
#                     SELECT referrer_id, COUNT(order_no) AS cnt
#                     FROM basedata_order AS b
#                     where pay_date BETWEEN DATE_ADD(CURDATE()- DAY(CURDATE())+1, INTERVAL -6 MONTH)
#                                 AND DATE_ADD(CURDATE(), INTERVAL - DAY(CURDATE())+1 DAY)
#                     and b.order_state not in (0, 4, 5, 96, 98, 999)
#                     GROUP BY b.referrer_id
#                     having cnt < %s
#                     ) as bo on bo.referrer_id = a.referrer
#                 join (
#                     SELECT referrer_id, order_no from basedata_order as c
#                     WHERE signoff_date BETWEEN DATE_ADD(CURDATE()- DAY(CURDATE())+1, INTERVAL -6 MONTH)
#                                 AND DATE_ADD(CURDATE(), INTERVAL - DAY(CURDATE())+1 DAY)
#                     and c.order_state not in (0, 4, 5, 96, 98, 999)
#                 ) as bo2 on bo2.referrer_id = a.uid
#                 WHERE a.referrer IS NOT NULL;
#             """
#         cursor = connection.cursor()
#         cursor.execute(sql, (lower_limit,))
#         cancelled_order_nos = [order_no for order_no, in cursor.fetchall()]
#         cancelled = RewardRecord.objects.filter(status=RewardRecord.REWARD_TBD,
#                                                 reward_type=RewardRecord.TYPE_PARTNER_REWARD,
#                                                 # create_time__lt=cur_month_start,
#                                                 order_no__in=cancelled_order_nos)
#         cancelled_cnt = cancelled.update(status=RewardRecord.REWARD_REVOKED,
#                                          achieved=0,
#                                          achieved_time=now(settings.USE_TZ),
#                                          memo=u'撤销原因：未达到活动要求（个人当月推广成交不满%s单）' % lower_limit)
#     # 只结算已签收的订单
#     settle_cnt = RewardRecord.objects.filter(status=RewardRecord.REWARD_TBD,
#                                              reward_type=RewardRecord.TYPE_PARTNER_REWARD,
#                                              referrer_id__in=referrers,
#                                              # create_time__lt=cur_month_start,
#                                              order_no__in=order_nos)\
#         .update(status=RewardRecord.REWARD_ACHIEVED, achieved=F('reward'))
#     # 上面是设置收益结算状态，以下逐一将收益入账
#     records = RewardRecord.objects.filter(status=RewardRecord.REWARD_ACHIEVED,
#                                           reward_type=RewardRecord.TYPE_PARTNER_REWARD,
#                                           referrer_id__in=referrers,
#                                           create_time__lt=cur_month_start,
#                                           order_no__in=order_nos,
#                                           account_no__isnull=True)
#     for r in records:
#         try:
#             res = r.charge()
#             if res:
#                 reward_cnt += 1
#         except Exception, e:
#             print e.message
#             pass
#
#     if referrer_cnt > 0:
#         msg = u'共结算%s笔、成功入账%s笔、撤销%s笔收益，涉及%s个推广人' % \
#               (settle_cnt, reward_cnt, cancelled_cnt, referrer_cnt)
#     else:
#         msg = NO_REWARDS
except Exception, e:
    is_ok = False
    msg = u"Check reward FAILED! %s" % (e.message or e.args[1])
#
# print msg
#
# end_time = datetime.datetime.now()
# try:
#     TaskLog.objects.create(
#         name=TASK_NAME,
#         start_time=start_time,
#         end_time=end_time,
#         exec_result=msg,
#         is_ok=is_ok,
#         result_file=''
#     )
# except Exception, e:
#     print 'Save task log error: %s' % (e.message or e.args[1])