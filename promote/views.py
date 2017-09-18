# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Count, Q
from django.db import connection

from profile.views import get_user_by_uid
from .models import RewardRecord, CouponTicket, CouponRule, CouponRuleSet
from util import renderutil
from tms import settings
from util.renderutil import report_error, json_response, day_str, export_csv, now
import json
from django.forms.models import model_to_dict

__author__ = 'winsom'


def get_rewards_summary(request):
    """
    获取用户收益记录简单统计结果
    :param request(GET):
        - uid, 必填，推广用户uid
        - [reward_type], 可选，收益类型，
            * 0 - 销售回佣
            * 1 - 伙伴激励
            * 2 - 企业管理费用
            * 3 - 转发推广回佣，不可提现（废弃）
        - [since], 可选，日期时间型，记录时间（非实际到账）下限（包含）
        - [before], 可选，日期时间型，记录时间（非实际到账）上限（不包含）
    :return:
        成功返回收益记录列表，如：
        {
            pending: {  （0 为待结算）
                rewards: "702.00",   (待结算收益总额)
                rewards_cnt: 16     （待结算收益笔数）
            },
            achieved: {   （1 为已结算）
                rewards: "78.00",    （已结算收益总额（预期金额））
                rewards_cnt: 2,      （已结算收益笔数）
                achieved: "10.00"    （已结算到账总额（到账金额））
            },
            cancelled: {    （2 为已取消）
                rewards: "78.00",  （已取消的收益总额）
                rewards_cnt: 2     （已取消的收益笔数）
            },
            today: {
                reward: "858.00",  (当日收益总额)
                rewards_cnt: 20   （当日收益笔数）
            }
        }
        注意，如果没有相关数据，则相应部分为{}， 如 "achieved": {} (表示没有已结算数据)
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/get_rewards_summary">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error('无效的用户账号！')

    records = RewardRecord.objects.filter(referrer_id=user.uid)
    reward_type = request.REQUEST.get('reward_type')
    if reward_type and reward_type.isdigit():
        records = records.filter(reward_type=int(reward_type))
    # if reward_type and reward_type.isdigit() and int(reward_type) == 3:
    #     records = records.filter(reward_type=3)
    # else:
    #     records = records.filter(reward_type__in=(0, 1, 2))
    # if reward_type and reward_type.isdigit():
    #     records = records.filter(reward_type=int(reward_type))

    # [since], 记录时间（非实际到账）下限（包含）
    if request.REQUEST.get('since'):
        records = records.filter(create_time__gte=request.REQUEST.get('since'))
    # [before], 记录时间（非实际到账）上限（不包含）
    if request.REQUEST.get('before'):
        records = records.filter(create_time__lt=request.REQUEST.get('before'))

    summary = records.values('status').order_by('status')\
        .annotate(rewards=Sum('reward'), achieved=Sum('achieved'), rewards_cnt=Count('reward'))

    result = {'waiting': {}, 'closed': {}, 'canceled': {}}
    for item in summary:
        if item.get('status') == RewardRecord.REWARD_TBD:
            result['waiting']['rewards'] = item.get('rewards')
            result['waiting']['rewards_cnt'] = item.get('rewards_cnt')
        elif item.get('status') == RewardRecord.REWARD_ACHIEVED:
            result['closed']['rewards'] = item.get('rewards')
            result['closed']['rewards_cnt'] = item.get('rewards_cnt')
            result['closed']['achieved'] = item.get('achieved')
            result['closed']['achieved_cnt'] = item.get('achieved_cnt')
        elif item.get('status') == RewardRecord.REWARD_REVOKED:
            result['canceled']['rewards'] = item.get('rewards')
            result['canceled']['rewards_cnt'] = item.get('rewards_cnt')

    # if reward_type and reward_type.isdigit() and int(reward_type) == 3:
    #     summary = RewardRecord.objects.filter(reward_type=3, referrer_id=user.uid, create_time__gte=renderutil.now(settings.USE_TZ))\
    #         .aggregate(rewards=Sum('reward'), rewards_cnt=Count('reward'))
    # else:
    #     summary = RewardRecord.objects.filter(reward_type__in=[0, 1, 2], referrer_id=user.uid, create_time__gte=renderutil.now(settings.USE_TZ))\
    #         .aggregate(rewards=Sum('reward'), rewards_cnt=Count('reward'))

    summary = RewardRecord.objects.filter(referrer_id=user.uid, create_time__gte=renderutil.now(settings.USE_TZ))\
        .aggregate(rewards=Sum('reward'), rewards_cnt=Count('reward'))
    result['today'] = {'reward': summary.get('rewards') or 0, 'rewards_cnt': summary.get('rewards_cnt', 0)}
    result['pending'] = result.get('waiting')
    result['achieved'] = result.get('closed')
    result['cancelled'] = result.get('canceled')
    return renderutil.json_response(result)


def bd_get_rewards_summary(request):
    """
    获取店铺收益记录简单统计结果
    :param request(GET):
        - store_code, 必填，店铺code
        - [reward_type], 可选，收益类型，
            * 0 - 销售回佣
            * 1 - 伙伴激励
            * 2 - 企业管理费用
            * 3 - 转发推广回佣，不可提现（废弃）
        - [since], 可选，日期时间型，记录时间（非实际到账）下限（包含）
        - [before], 可选，日期时间型，记录时间（非实际到账）上限（不包含）
    :return:
        成功返回收益记录列表，如：
        {
            pending: {  （0 为待结算）
                rewards: "702.00",   (待结算收益总额)
                rewards_cnt: 16     （待结算收益笔数）
            },
            achieved: {   （1 为已结算）
                rewards: "78.00",    （已结算收益总额（预期金额））
                rewards_cnt: 2,      （已结算收益笔数）
                achieved: "10.00"    （已结算到账总额（到账金额））
            },
            cancelled: {    （2 为已取消）
                rewards: "78.00",  （已取消的收益总额）
                rewards_cnt: 2     （已取消的收益笔数）
            },
            today: {
                reward: "858.00",  (当日收益总额)
                rewards_cnt: 20   （当日收益笔数）
            }
        }
        注意，如果没有相关数据，则相应部分为{}， 如 "achieved": {} (表示没有已结算数据)
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/get_rewards_summary">查看样例</a>
    """
    # user = get_user_by_uid(request)
    # if not user:
    #     return renderutil.report_error('无效的用户账号！')
    req = request.POST if 'POST' == request.method else request.GET
    store_code = req.get('store_code')
    if not store_code:
        return renderutil.report_error(u'缺少参数：store_code')

    from buding.models import ShopManagerInfo
    # uids = []
    # uss = ShopManagerInfo.objects.filter(shopcode=store_code)
    # for u in uss:
    #     uids.append(u)
    #
    # records = RewardRecord.objects.filter(referrer_id__in=uids)
    records = RewardRecord.objects.filter(store_code=store_code)
    reward_type = request.REQUEST.get('reward_type')
    if reward_type and reward_type.isdigit():
        records = records.filter(reward_type=int(reward_type))
    # if reward_type and reward_type.isdigit() and int(reward_type) == 3:
    #     records = records.filter(reward_type=3)
    # else:
    #     records = records.filter(reward_type__in=(0, 1, 2))
    # if reward_type and reward_type.isdigit():
    #     records = records.filter(reward_type=int(reward_type))

    # [since], 记录时间（非实际到账）下限（包含）
    if request.REQUEST.get('since'):
        records = records.filter(create_time__gte=request.REQUEST.get('since'))
    # [before], 记录时间（非实际到账）上限（不包含）
    if request.REQUEST.get('before'):
        records = records.filter(create_time__lt=request.REQUEST.get('before'))

    summary = records.values('status').order_by('status')\
        .annotate(rewards=Sum('reward'), achieved=Sum('achieved'), rewards_cnt=Count('reward'))

    result = {'waiting': {}, 'closed': {}, 'canceled': {}}
    for item in summary:
        if item.get('status') == RewardRecord.REWARD_TBD:
            result['waiting']['rewards'] = item.get('rewards')
            result['waiting']['rewards_cnt'] = item.get('rewards_cnt')
        elif item.get('status') == RewardRecord.REWARD_ACHIEVED:
            result['closed']['rewards'] = item.get('rewards')
            result['closed']['rewards_cnt'] = item.get('rewards_cnt')
            result['closed']['achieved'] = item.get('achieved')
            result['closed']['achieved_cnt'] = item.get('achieved_cnt')
        elif item.get('status') == RewardRecord.REWARD_REVOKED:
            result['canceled']['rewards'] = item.get('rewards')
            result['canceled']['rewards_cnt'] = item.get('rewards_cnt')

    # if reward_type and reward_type.isdigit() and int(reward_type) == 3:
    #     summary = RewardRecord.objects.filter(reward_type=3, referrer_id=user.uid, create_time__gte=renderutil.now(settings.USE_TZ))\
    #         .aggregate(rewards=Sum('reward'), rewards_cnt=Count('reward'))
    # else:
    #     summary = RewardRecord.objects.filter(reward_type__in=[0, 1, 2], referrer_id=user.uid, create_time__gte=renderutil.now(settings.USE_TZ))\
    #         .aggregate(rewards=Sum('reward'), rewards_cnt=Count('reward'))

    summary = RewardRecord.objects.filter(referrer_id=store_code, create_time__gte=renderutil.now(settings.USE_TZ))\
        .aggregate(rewards=Sum('reward'), rewards_cnt=Count('reward'))
    result['today'] = {'reward': summary.get('rewards') or 0, 'rewards_cnt': summary.get('rewards_cnt', 0)}
    result['pending'] = result.get('waiting')
    result['achieved'] = result.get('closed')
    result['cancelled'] = result.get('canceled')
    return renderutil.json_response(result)


#
# def get_fw_rewards_summary(request):
#     """
#     获取用户转发收益记录简单统计结果
#     :param request(GET):
#         - uid, 必填，推广用户uid
#         - [reward_type], 可选，收益类型，
#             * 0 - 销售回佣
#             * 1 - 伙伴激励
#             * 2 - 企业管理费用
#             * 3 - 转发推广回佣，不可提现
#         - [since], 可选，日期时间型，记录时间（非实际到账）下限（包含）
#         - [before], 可选，日期时间型，记录时间（非实际到账）上限（不包含）
#     :return:
#         成功返回收益记录列表，如：
#         {
#             pending: {  （0 为待结算）
#                 rewards: "702.00",   (待结算收益总额)
#                 rewards_cnt: 16     （待结算收益笔数）
#             },
#             achieved: {   （1 为已结算）
#                 rewards: "78.00",    （已结算收益总额（预期金额））
#                 rewards_cnt: 2,      （已结算收益笔数）
#                 achieved: "10.00"    （已结算到账总额（到账金额））
#             },
#             cancelled: {    （2 为已取消）
#                 rewards: "78.00",  （已取消的收益总额）
#                 rewards_cnt: 2     （已取消的收益笔数）
#             },
#             today: {
#                 reward: "858.00",  (当日收益总额)
#                 rewards_cnt: 20   （当日收益笔数）
#             }
#         }
#         注意，如果没有相关数据，则相应部分为{}， 如 "achieved": {} (表示没有已结算数据)
#         失败返回错误消息{"error": msg}
#
#     eg. <a href="/tms-api/get_rewards_summary">查看样例</a>
#     """
#     user = get_user_by_uid(request)
#     if not user:
#         return renderutil.report_error('无效的用户账号！')
#
#     records = RewardRecord.objects.filter(referrer_id=user.uid)
#     records = records.filter(reward_type=3)
#     reward_type = request.REQUEST.get('reward_type')
#     if reward_type and reward_type.isdigit():
#         records = records.filter(reward_type=int(reward_type))
#
#     # [since], 记录时间（非实际到账）下限（包含）
#     if request.REQUEST.get('since'):
#         records = records.filter(create_time__gte=request.REQUEST.get('since'))
#     # [before], 记录时间（非实际到账）上限（不包含）
#     if request.REQUEST.get('before'):
#         records = records.filter(create_time__lt=request.REQUEST.get('before'))
#
#     summary = records.values('status').order_by('status')\
#         .annotate(rewards=Sum('reward'), achieved=Sum('achieved'), rewards_cnt=Count('reward'))
#
#     result = {'waiting': {}, 'closed': {}, 'canceled': {}}
#     for item in summary:
#         if item.get('status') == RewardRecord.REWARD_TBD:
#             result['waiting']['rewards'] = item.get('rewards')
#             result['waiting']['rewards_cnt'] = item.get('rewards_cnt')
#         elif item.get('status') == RewardRecord.REWARD_ACHIEVED:
#             result['closed']['rewards'] = item.get('rewards')
#             result['closed']['rewards_cnt'] = item.get('rewards_cnt')
#             result['closed']['achieved'] = item.get('achieved')
#             result['closed']['achieved_cnt'] = item.get('achieved_cnt')
#         elif item.get('status') == RewardRecord.REWARD_REVOKED:
#             result['canceled']['rewards'] = item.get('rewards')
#             result['canceled']['rewards_cnt'] = item.get('rewards_cnt')
#
#     summary = RewardRecord.objects.filter(referrer_id=user.uid, create_time__gte=renderutil.now(settings.USE_TZ))\
#         .aggregate(rewards=Sum('reward'), rewards_cnt=Count('reward'), reward_type=3)
#     result['today'] = {'reward': summary.get('rewards') or 0, 'rewards_cnt': summary.get('rewards_cnt', 0)}
#     result['pending'] = result.get('waiting')
#     result['achieved'] = result.get('closed')
#     result['cancelled'] = result.get('canceled')
#     return renderutil.json_response(result)


def query_rewards(request):
    """
    获取用户收益记录
    :param request(GET):
        - uid, 必填，推广用户uid
        - [source_uid]， 可选，收益来源用户的uid
            如果是销售回佣，则为买家uid，如果是伙伴销售奖励，则为伙伴uid，如果是企业管理费用，则为下属企业uid
        - [status], 可选，收益状态，有如下几种情形：
            * 0  - 待结算
            * 1  - 已到账
            * 2  - 已取消，即订单已取消或退款
        - [reward_type], 可选，收益类型，
            * 0 - 销售回佣
            * 1 - 伙伴激励
            * 2 - 企业管理费用
            * 3 - 转发推广回佣，不可提现
        - [activity_code], 可选，活动代码
        - [order_no], 可选，订单号
        - [account_no], 可选，账户流水号
        - [since], 可选，日期时间型，记录时间（非实际到账）下限（包含）
        - [before], 可选，日期时间型，记录时间（非实际到账）上限（不包含）
        - [update_since], 可选，日期时间型，更新时间（非实际到账）下限（包含）
        - [pos], 可选，获取的结果可能存在多页时，给定开始选取的位置，默认为0
        - [size], 可选，获取的结果可能存在多页时，确定返回每页记录数，默认为10
    :return:
        成功返回收益记录列表，如：
            [
                {
                    status: 0,
                    update_time: null,
                    activity_code: null,
                    order_no: "D160411KMSQWV",
                    achieved: "0.00",  （到账数额）
                    achieved_time: null,  （到账时间，为空表示未到账）
                    create_time: "2016-04-11 18:11:59",
                    referrer_id: "184813c81d2540e68f80ac19210c6413",
                    reward: "0.00" , （预期收益金额）
                    reward_type: 0,  （收益类型）
                },
            ]
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/query_rewards">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error('无效的用户账号！')

    records = RewardRecord.objects.filter(referrer_id=user.uid)
    status = request.REQUEST.get('status')
    if status and status.isdigit():
        records = records.filter(status=int(status))

    if 'source_uid' in request.REQUEST:
        records = records.filter(source_uid=request.REQUEST.get('source_uid'))

    reward_type = request.REQUEST.get('reward_type')
    if reward_type and reward_type.isdigit():
        records = records.filter(reward_type=int(reward_type))

    if request.REQUEST.get('activity_code'):
        records = records.filter(activity_code=request.REQUEST.get('activity_code'))

    if request.REQUEST.get('order_no'):
        records = records.filter(order_no=request.REQUEST.get('order_no'))

    if request.REQUEST.get('account_no'):
        records = records.filter(account_no=request.REQUEST.get('account_no'))

    # [since], 记录时间（非实际到账）下限（包含）
    if request.REQUEST.get('since'):
        records = records.filter(create_time__gte=request.REQUEST.get('since'))
    # [before], 记录时间（非实际到账）上限（不包含）
    if request.REQUEST.get('before'):
        records = records.filter(create_time__lt=request.REQUEST.get('before'))

    # [before], 记录时间（非实际到账）下限（包含）
    if request.REQUEST.get('update_since'):
        records = records.filter(update_time__gte=request.REQUEST.get('update_since'))

    start_pos = int(request.REQUEST.get('pos', 0))
    page_size = int(request.REQUEST.get('size', 10))
    # page_size = page_size if 2 < page_size < 20 else 20 if page_size >= 20 else 2
    if request.REQUEST.get('page'):
        start_pos = int(request.REQUEST.get('page')) * page_size

    records = records[start_pos:start_pos + page_size]

    return renderutil.json_response(records)


def bd_query_rewards(request):
    """
    获取店铺收益记录
    :param request(GET):
        - store_code, 必填，店铺code
        - [source_uid]， 可选，收益来源用户的uid
            如果是销售回佣，则为买家uid，如果是伙伴销售奖励，则为伙伴uid，如果是企业管理费用，则为下属企业uid
        - [status], 可选，收益状态，有如下几种情形：
            * 0  - 待结算
            * 1  - 已到账
            * 2  - 已取消，即订单已取消或退款
        - [reward_type], 可选，收益类型，
            * 0 - 销售回佣
            * 1 - 伙伴激励
            * 2 - 企业管理费用
            * 3 - 转发推广回佣，不可提现
        - [activity_code], 可选，活动代码
        - [order_no], 可选，订单号
        - [account_no], 可选，账户流水号
        - [since], 可选，日期时间型，记录时间（非实际到账）下限（包含）
        - [before], 可选，日期时间型，记录时间（非实际到账）上限（不包含）
        - [update_since], 可选，日期时间型，更新时间（非实际到账）下限（包含）
        - [pos], 可选，获取的结果可能存在多页时，给定开始选取的位置，默认为0
        - [size], 可选，获取的结果可能存在多页时，确定返回每页记录数，默认为10
    :return:
        成功返回收益记录列表，如：
            [
                {
                    status: 0,
                    update_time: null,
                    activity_code: null,
                    order_no: "D160411KMSQWV",
                    achieved: "0.00",  （到账数额）
                    achieved_time: null,  （到账时间，为空表示未到账）
                    create_time: "2016-04-11 18:11:59",
                    referrer_id: "184813c81d2540e68f80ac19210c6413",
                    reward: "0.00" , （预期收益金额）
                    reward_type: 0,  （收益类型）
                },
            ]
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/query_rewards">查看样例</a>
    """
    # user = get_user_by_uid(request)
    # if not user:
    #     return renderutil.report_error('无效的用户账号！')
    req = request.POST if 'POST' == request.method else request.GET
    store_code = req.get('store_code')
    if not store_code:
        return renderutil.report_error(u'缺少参数：store_code')

    records = RewardRecord.objects.filter(referrer_id=store_code)
    status = request.REQUEST.get('status')
    if status and status.isdigit():
        records = records.filter(status=int(status))

    if 'source_uid' in request.REQUEST:
        records = records.filter(source_uid=request.REQUEST.get('source_uid'))

    reward_type = request.REQUEST.get('reward_type')
    if reward_type and reward_type.isdigit():
        records = records.filter(reward_type=int(reward_type))

    if request.REQUEST.get('activity_code'):
        records = records.filter(activity_code=request.REQUEST.get('activity_code'))

    if request.REQUEST.get('order_no'):
        records = records.filter(order_no=request.REQUEST.get('order_no'))

    if request.REQUEST.get('account_no'):
        records = records.filter(account_no=request.REQUEST.get('account_no'))

    # [since], 记录时间（非实际到账）下限（包含）
    if request.REQUEST.get('since'):
        records = records.filter(create_time__gte=request.REQUEST.get('since'))
    # [before], 记录时间（非实际到账）上限（不包含）
    if request.REQUEST.get('before'):
        records = records.filter(create_time__lt=request.REQUEST.get('before'))

    # [before], 记录时间（非实际到账）下限（包含）
    if request.REQUEST.get('update_since'):
        records = records.filter(update_time__gte=request.REQUEST.get('update_since'))

    start_pos = int(request.REQUEST.get('pos', 0))
    page_size = int(request.REQUEST.get('size', 10))
    # page_size = page_size if 2 < page_size < 20 else 20 if page_size >= 20 else 2
    if request.REQUEST.get('page'):
        start_pos = int(request.REQUEST.get('page')) * page_size

    records = records[start_pos:start_pos + page_size]

    return renderutil.json_response(records)


@login_required
def export_reward_order(request):
    """
    导出收益关联订单列表 (GET)
    :param request:
        - ids, 获得收益的用户uid列表
        - [format]，输出格式
    :return:
    """
    if not request.user.is_superuser and not request.user.is_staff:
        return report_error("对不起，访问未授权！")
    try:
        ids = request.REQUEST.get("ids")
        if not ids:
            return report_error('参数信息不完整')
        elif ids == 'all' and not request.user.is_superuser:
            return report_error("对不起，访问未授权！")

        id_list = []
        if ids == 'select_across':  # across selected in one page
            id_list = request.session.get('selected_for_export', [])
            if 'selected_for_export' in request.session:
                del request.session['selected_for_export']
        elif ids != 'all':
            id_list = ids.split(',')

        output_format = request.REQUEST.get('format', 'csv')  # 默认导出csv格式
        sql = '''
            select pr.order_no, bo.order_state, bo.pay_amount, bo.pay_date, bo.order_date,
                pr.reward, pr.achieved, pr.achieved_time, pr.`status`, pr.account_no,
                pe.real_name, pe.mobile, pe.nick_name, pe.gender, pr.referrer_id as uid
            from promote_rewardrecord as pr
            inner join basedata_order as bo on pr.order_no = bo.order_no
            inner JOIN `profile_enduser` as `pe` ON pr.`referrer_id` = pe.`uid`
        '''
        if len(id_list) > 0:
            sql = '%s where pr.`order_no` in ("%s")' % (sql, '", "'.join(id_list))
            # sql = '%s where pr.`order_no` in ("%s") and pr.reward_type in (0,1,2)' % (sql, '", "'.join(id_list))
        cursor = connection.cursor()
        cursor.execute(sql)
        qs = cursor.fetchall()
        data = []
        from basedata.models import Order
        from promote.models import RewardRecord
        from profile.models import EndUser
        states_dict = dict(Order.ORDER_STATES)
        status_dict = dict(RewardRecord.REWARD_STATUS)
        gender_dict = dict(EndUser.GENDER_TYPES)
        for r in qs:
            # data.append([r.order_no, states_dict.get(r.order_state), r.pay_amount, r.pay_date, r.order_date,
            #              r.reward, r.achieved, r.achieved_time, status_dict.get(r.status), r.account_no,
            #              r.real_name, r.mobile, r.nick_name, gender_dict.get(r.gender), r.uid])
            data.append([r[0], states_dict.get(r[1]), r[2], r[3], r[4],
                         r[5], r[6], r[7], status_dict.get(r[8]), r[9],
                         r[10], r[11], r[12], gender_dict.get(r[13]), r[14]])
        if output_format == 'json':
            return json_response(data)
        else:

            data.insert(0, (u'订单号', u'订单状态', u'支付金额', u'支付日期', u'创建日期',
                            u'预期收益', u'结算金额', u'结算时间', u'收益状态', u'资金流水',
                            u'用户姓名', u'手机号', u'昵称', u'性别', u'UID'))
            file_name = "reward_order_%s.csv" % day_str()
            return export_csv(file_name, data)
    except ObjectDoesNotExist:
        return report_error('没有数据')


@login_required
def export_coupon_tickets(request):
    """
    导出指定优惠活动的所有券码
    :param request:
        - ids, 活动id列表
        - [format]，输出格式
    :return:
    """
    if not request.user.is_superuser \
            and not request.user.has_perm('promote.add_couponrule') \
            and not request.user.has_perm('promote.change_couponrule'):
        return renderutil.report_error("对不起，访问未授权！")

    ids = request.GET.get("ids")
    if not ids:
        return renderutil.report_error('参数信息不完整')
    if ids == 'all':
        if not request.user.is_superuser and \
                not request.user.has_perm('basedata.can_manage_order'):
            return renderutil.report_error("对不起，访问未授权！")
        rules = CouponRule.objects.all()
    elif ids == 'select_across':  # across selected in one page
        rules = CouponRule.objects.filter(code__in=request.session.get('selected_for_export', []))
        if 'selected_for_export' in request.session:
            del request.session['selected_for_export']
    else:
        id_list = ids.split(',')
        rules = CouponRule.objects.filter(code__in=id_list)

    if 'json' == format:
        data = []
        for rule in rules:
            rule.generate_all()
            data.append({'rule': rule.to_dict(),
                         'tickets': rule.tickets.all().values_list('code', 'get_time', 'consume_time', 'order_no')})
        return renderutil.json_response(data)
    else:
        header = ['优惠券编码', '领取时间', '消费时间', '应用于订单号']
        all_tickets = []
        for rule in rules:
            rule.generate_all()
            all_tickets.append(['%s[%s]' % (rule.name, rule.code)])
            all_tickets.append(header)
            tickets = rule.tickets.all().values_list('code', 'get_time', 'consume_time', 'order_no')
            all_tickets.extend(tickets)
        all_tickets.append(['--------------END-------------'])

        file_name = 'coupon_tickets_%s.xls' % day_str()
        return renderutil.export_excel(file_name, all_tickets)


def is_coupon_ok(request):
    """
    用于判断给定优惠券是否可用，如果指定订单号，则检查是否可用于指定订单，如果指定商品编码，则检查是否可用于该商品
    :param request (GET):
        - uid, 优惠券用户的uid
        - coupon, 优惠券编码，如果多个可以用逗号分隔
        - [order_no | prd_no, pcs | shop_data], 订单号 | 商品编码，商品数量（默认为1）|  商品购物清单
             shop_data，购买商品数据，数组（注意，传参时需要先把数组转成json字符串，如'[{"pcs": 2, "code": "P1603065T3D89"}]'）
                * code, 商品编码
                * [pcs], 购买数量，默认为1
    :return:
        成功返回优惠券编码及是否可用的结果，可用为true，不可用为不可用的原因，如下：
        {"SGTVN4G6QRZPSD8A": true， "SGTVN4G6QRZSFEFE": "优惠券已过期"}

        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/is_coupon_ok">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error('无效的用户账号！')

    REQ = renderutil.render_request(request)
    code = REQ.get('coupon')
    if not code:
        return report_error('请提供优惠券编码')

    codes = code.split(',')
    coupons = CouponTicket.objects.filter(code__in=codes, consumer=user.uid)
    result = {}
    order_no = REQ.get('order_no')
    prd_no = REQ.get('prd_no')
    shop_data = REQ.get('shop_data')
    if order_no:
        from basedata.models import Order
        try:
            order = Order.objects.get(order_no=order_no, buyer_id=user.uid)
            order = order.to_dict()
        except Order.DoesNotExist:
            return renderutil.report_error(u'找不到订单[%s]' % order_no)
        else:
            for c in coupons:
                res = c.is_applicable_to_order_obj(order=order)
                result[c.code] = res
    elif prd_no:
        from basedata.models import Product
        pcs = int(REQ.get('pcs', 1))
        try:
            product = Product.objects.get(code=prd_no)
            product = product.to_dict()
        except Product.DoesNotExist:
            return report_error(u'找不到商品[%s]' % prd_no)
        else:
            for c in coupons:
                res = c.is_applicable_to_product(product, pcs)
                result[c.code] = res
    elif shop_data:
        if isinstance(shop_data, basestring):
            try:
                shop_data = json.loads(shop_data)
            except:
                return report_error('无效的购物数据：%s' % shop_data)

        prds = {}
        for item in shop_data:
            prds[item.get('code')] = item.get('pcs', 1)

        from basedata.models import Product
        products = Product.objects.filter(code__in=prds.keys())
        prds_checked = [{"product": prd.to_dict(), "pcs": prds[prd.code]} for prd in products]

        for c in coupons:
            result[c.code] = c.is_applicable_to_products(prds_checked)

    else:
        for c in coupons:
            res = c.is_valid()
            result[c.code] = res

    if len(result) < len(codes):
        delta = set(codes).difference(result.keys())
        for d in delta:
            result[d] = u'找不到优惠券%s' % d

    return json_response(result)


def query_coupons(request):
    """
    查询指定用户持有的优惠券列表
    :param request (GET):
        - uid, 领取用户的uid
        - [rules], 可选，优惠活动编码，多个活动编码用英文逗号分隔，查询用户持有的指定活动的优惠券
        - [is_expired]，如果为1取已失效的，否则默认取未失效的， 如果为all则取所有的
        - [is_consumed]，如果为1取已使用的，否则默认取未使用的，如果为all则取所有的
        - [pos], 可选，起始偏移量，默认为0
        - [size]，可选，一次获取多少条数据，默认为10，取值范围2~20
        - [order_no | shop_data], 订单号 | 商品购物清单，用于筛选适用的优惠券
             shop_data，购买商品数据，数组（注意，传参时需要先把数组转成json字符串，如'[{"pcs": 2, "code": "P1603065T3D89"}]'）
                * code, 商品编码
                * [pcs], 购买数量，默认为1
        - [group, [onlycount]], 可选，是否分组返回，默认不分组，所有优惠券平铺在结果数组里，如果为1则按照优惠活动分组返回
            * onlycount, 是否只返回优惠券数量，默认返回优惠券列表，1为不返回，其它返回

    :return:
        成功返回优惠券列表，如果group为1，则以优惠活动分组返回优惠券列表，如下：
        [
            {
            allow_addon: false,
            applied_to_first_order: false,
            applied_to_products: "TEST-001",
            applied_to_stores: "",
            applied_to_suppliers: "",
            code: "TEST-160601",
            discount: 10,
            end_time: "2030-06-01 00:00:00",
            image: "http://7xs6ch.com2.z0.glb.qiniucdn.com/static/2016/05/11/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2016-05-11_%E4%B8%8B%E5%8D%883.20.18.png",
            is_active: true,
            link_page: null,
            most_tickets: 10,
            name: "满100减10元",
            pub_number: 1000,
            repeatable: false,
            start_time: "2016-06-01 00:00:00",
            threshold: 100,
            tickets_onetime: 1,
            coupons: [
                {
                    code: "SG5ETPB6XNC8ZURA",
                    order_no: null,
                    consumer: "test_12345678",
                    rule: "TEST-160601",
                    id: 73300,
                    get_time: "2016-06-27 11:43:27",
                    consume_time: null,
                    is_expired: false,
                    dispatcher: null
                },
                {
                    code: "SG54JRZEWU3DCP5A",
                    order_no: null,
                    consumer: "test_12345678",
                    rule: "TEST-160601",
                    id: 73204,
                    get_time: "2016-06-27 11:43:27",
                    consume_time: null,
                    is_expired: false,
                    dispatcher: null
                }
            ]
        }
        否则，返回值参见fetch_coupons接口文档

        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/query_coupons">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号！')

    req = renderutil.render_request(request)
    records = CouponTicket.objects.filter(consumer=user.uid)
    if '1' == req.get('is_expired'):
        records = records.filter(Q(is_expired=True) | Q(rule__end_time__lte=now(settings.USE_TZ)))
    elif 'all' == req.get('is_expired'):
        pass
    else:
        records = records.filter(Q(is_expired=False) & Q(rule__end_time__gt=now(settings.USE_TZ)))

    if req.get('rules'):
        rule_codes = req.get('rules').split(',')
        records = records.filter(rule__code__in=rule_codes)

    if '1' == req.get('is_consumed'):
        records = records.filter(order_no__isnull=False)
    elif 'all' == req.get('is_consumed'):
        pass
    else:
        records = records.filter(order_no__isnull=True)

    start_pos = int(req.get('pos', 0))
    page_size = int(req.get('size', 10))
    # page_size = page_size if 2 < page_size < 20 else 20 if page_size >= 20 else 2
    if req.get('page'):
        start_pos = int(req.get('page')) * page_size

    result = []
    coupons = records[start_pos:start_pos+page_size]

    order_no = req.get('order_no')
    shop_data = req.get('shop_data')
    if order_no:
        from basedata.models import Order
        try:
            order = Order.objects.get(order_no=order_no, buyer_id=user.uid)
            order = order.to_dict()
        except Order.DoesNotExist:
            return renderutil.report_error(u'找不到订单[%s]' % order_no)
        else:
            for c in coupons:
                if c.is_applicable_to_order_obj(order=order):
                    result.append(c)
    elif shop_data:
        if isinstance(shop_data, basestring):
            try:
                shop_data = json.loads(shop_data)
            except:
                return report_error('无效的购物数据：%s' % shop_data)

        prds = {}
        for item in shop_data:
            prds[item.get('code')] = item.get('pcs', 1)

        from basedata.models import Product
        products = Product.objects.filter(code__in=prds.keys())
        prds_checked = [{"product": prd.to_dict(), "pcs": prds[prd.code]} for prd in products]

        for c in coupons:
            if c.is_applicable_to_products(prds_checked) is True:
                result.append(c)
    else:
        for c in coupons:
            if c.is_valid():
                result.append(c)

    if req.get('group') == "1" or req.get('group') == 1:
        # group by rule
        rule_map = {}
        for c in result:
            if c.rule.code not in rule_map:
                rule_map[c.rule.code] = c.rule.simple()
                rule_map[c.rule.code]['coupons'] = []
            rule_map[c.rule.code]['coupons'].append(model_to_dict(c))
        result = rule_map.values()
    else:
        result = [c.to_dict() for c in result]
    return json_response(result)


def fetch_coupons(request):
    """
    领取优惠券
    :param request (GET):
        - uid, 领取用户的uid
        - rule_set | rules,
            * rule_set, 活动套餐编码
            * rules，优惠活动编码及数量（用英文逗号分隔，如果不提供数量，默认为优惠活动配置的一次可获取数量），多个活动可用|分隔，如
            "A-160505-UJX,2|A-160505-JFR,2|A-160505-MHD,1"表示派发三种优惠券，并分别派发2张，2张和1张
    :return:
        成功返回优惠券列表。以下几种情形可能返回的优惠券数量会少于要求的，甚至为[]：
            * 找不到对应的优惠活动
            * 指定的优惠活动没有足够多的可用数量优惠券或已发完
            * 用户已领取的优惠券数量超过可领取的最大值
        {
            tickets: [
                {
                    code: "SE5JX4SKT7NELV6B",  (优惠券编码)
                    order_no: null, （应用于目标订单号，没有表示未被使用）
                    consumer: "afebfaa8457d4e0aaeb1b7a317d9493e", (领用人，没有表示未被领用)
                    rule: {  （优惠规则）
                        image: "http://7xs6ch.com2.z0.glb.qiniucdn.com/static/2016/04/26/coupon.jpg",  （优惠券图片）
                        code: "A-160505-EJB",
                        name: "满200减10元",
                        applied_to_stores: "",
                        pub_number: 100,
                        start_time: "2016-05-05 11:10:00",
                        allow_addon: false,  （是否允许与其他购物优惠规则叠加使用）
                        is_active: true,
                        discount: 10,  （优惠金额）
                        repeatable: false,  （同一订单是否允许使用多张优惠）
                        end_time: "2016-06-30 00:00:00",
                        threshold: 200,  （订单最小购物金额限制，0表示不限）
                        applied_to_suppliers: "",
                        applied_to_products: "",
                        applied_to_first_order: false
                    },
                    id: 116,
                    get_time: "2016-04-27 14:49:39", （领用时间）
                    consume_time: null,  （消费时间）
                    is_expired: false,  （是否过期失效）
                    dispatcher: null   （保留，分发者）
                }
            ],
            failures: [
                ["A-160505-EJB", "满200减10元", "每人限领5张"],
                ["abc", null, "优惠活动[abc]不存在"]
            ]
        }

        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/fetch_coupons">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error('无效的用户账号！')

    REQ = renderutil.render_request(request)
    rule_set = REQ.get('rule_set')
    code = REQ.get('rules')
    # codes_dict = {}
    codes = []
    if rule_set:
        try:
            rs = CouponRuleSet.objects.get(code=rule_set)
            cur_time = now(settings.USE_TZ)
            if not rs.start_time or rs.start_time > cur_time or (rs.end_time and rs.end_time < cur_time):
                return report_error('优惠活动组合[%s]无效' % rule_set)
            rules = rs.rules.all()
            codes = [(r.rule.code, r.number) for r in rules]
        except CouponRuleSet.DoesNotExist:
            return report_error('找不到该优惠活动组合[%s]' % rule_set)
    elif code:
        rule_codes = code.split('|')
        for c in rule_codes:
            c_size = c.split(',', 1)
            codes.append((c_size[0], None if len(c_size) == 1 else c_size[1]))
    else:
        return report_error('请指明优惠活动或优惠活动组合')

    tickets = []
    err = []
    rules = CouponRule.objects.filter(code__in=[code for code, size in codes])
    rules_dict = dict([(r.code, r) for r in rules])
    for code, size in codes:
        if code not in rules_dict:
            err.append((code, None, '优惠活动[%s]不存在' % code))
        else:
            rule = rules_dict[code]
            try:
                tickets.extend(rule.fetch_coupons(user.uid, size))
            except ValueError, e:
                err.append((code, rule.name, e.message))

    # rules = CouponRule.objects.filter(code__in=codes_dict.keys())
    # for rule in rules:
    #     try:
    #         ts = rule.fetch_tickets(consumer=user.uid, size=int(codes_dict.get(rule.code, 1)))
    #         tickets.extend(ts)
    #     except ValueError, e:
    #         err.append(e.message)

    return json_response({"tickets": tickets, "failures": err})


def get_coupon_ruleset(request):
    """
    获取指定的优惠活动套餐
    :param request:
        - code, 优惠活动组合(领券用)编码
        - [uid], 用户uid，如果指定该参数，则返回此用户已获取的套餐内对应优惠活动的优惠券数量
    :return:
        成功返回
        {
            "code" : "S161123THY",
            "description" : ""
            "end_time" : "2016-11-24 18:11:00",
            "image" : "",
            "link_page" : "",
            "name" : "特惠套餐",
            "start_time" : "2016-11-23 17:38:00",
            - "rules" : [       (优惠活动列表)
                 -
                {
                    "claimed" : 1,      （此类优惠券已领取数量）
                    "number" : 1,      （此类优惠券可领取数量）
                    "allow_addon" : false,
                    "allow_dynamic" : true,
                    "applied_to_first_order" : false,
                    "applied_to_products" : "TEST-001"
                    "applied_to_stores" : "",
                    "applied_to_suppliers" : "",
                    "code" : "TEST-160602",
                    "coupon_image" : 229,
                    "description" : "<p>满50减10元券</p>",
                    "discount" : 10,
                    "dynamic_days" : 30,
                    "end_time" : "2030-06-01 00:00:00",
                    "format" : "",
                    "image" : "http://7xs6ch.com2.z0.glb.qiniucdn.com/static/2016/05/11/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2016-05-11_%E4%B8%8B%E5%8D%883.20.18.png",
                    "is_active" : true,
                    "link_page" : null,
                    "list_order" : 0,
                    "most_tickets" : 10,
                    "name" : "满50减10元",
                    "pub_number" : 1000,
                    "repeatable" : false,
                    "start_time" : "2016-06-01 00:00:00",
                    "threshold" : 50,
                    "tickets_available" : 990,
                    "tickets_claimed" : 10,
                    "tickets_onetime" : 1,
                },
                ...
            ],
        }
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/get_coupon_ruleset">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    rule_set = req.get('code')
    if not rule_set:
        return report_error('请提供优惠活动组合编码')

    try:
        rs = CouponRuleSet.objects.get(code=rule_set)
        cur_time = now(settings.USE_TZ)
        if not rs.start_time or rs.start_time > cur_time or (rs.end_time and rs.end_time < cur_time):
            return report_error('套餐[%s]无效' % rule_set)
        res = rs.to_dict()
        if 'uid' in req:
            user = get_user_by_uid(request)
            if not user:
                pass  # ignore return report_error('无效的用户账号！')
            else:
                rule_ids = [r['code'] for r in res['rules']]
                coupon_claimed = CouponTicket.objects.filter(consumer=user.uid, rule_id__in=rule_ids)\
                    .values_list('rule_id').annotate(Count('id'))
                claimed_dict = dict(coupon_claimed)
                for r in res['rules']:
                    r['claimed'] = claimed_dict.get(r['code'], 0)

        return json_response(res)
    except CouponRuleSet.DoesNotExist:
        return report_error('找不到该优惠活动组合[%s]' % rule_set)


def query_coupon_rules(request):
    """
    查询可用的优惠券活动（即规则），可用的包括已开始和未开始的已生效活动
    :param request (GET):
        - code, 优惠活动编码，不指定则返回所有可用的，如果有多个，则用逗号分隔
        - [pos], 可选，起始偏移量，默认为0
        - [size]，可选，一次获取多少条数据，默认为10，取值范围2~20
    :return:
        成功返回可用或匹配的优惠券活动列表（注意，如果使用code查询，没有匹配的话返回[]而不是错误消息）
            [
                {
                    allow_addon: false,  (是否允许与其他购物优惠规则叠加使用)
                    applied_to_first_order: false, (仅当用户未下过单时使用（不含已取消的订单）)
                    applied_to_products: "",  (限制用于指定商品清单，填写商品编号，多个商品用英文逗号分隔)
                    applied_to_stores: "",  (限制用于指定店铺，填写店铺编号，多个店铺用英文逗号分隔)
                    applied_to_suppliers: "",  （限制用于指定供应商，填写供应商编码，多个供应商用英文逗号分隔）
                    code: "A-160426-ULY",  （活动编码）
                    coupon_image: 157,  （活动图片id）
                    description: "满100减10元优惠",  （活动描述）
                    discount: 5,  （优惠金额）
                    end_time: "2016-04-28 00:00:00"  （活动截止时间）
                    format: "",  （保留，用于定义优惠券编码格式，目前均为自动生成）
                    image: "http://7xs6ch.com2.z0.glb.qiniucdn.com/static/2016/04/26/coupon.jpg",  （优惠券图片）
                    is_active: true,  （是否可用）
                    link_page: null,    （外链活动页面url）
                    most_tickets: 15,  (同一用户最多可领取数量)
                    name: "满百减10元",  （活动名称）
                    pub_number: 100,  （优惠券发行数量）
                    repeatable: false,  （同一订单是否允许使用多张优惠）
                    start_time: null,   （活动k开始时间
                    threshold: 100,  （订单最小购物金额限制(元)）
                    tickets_available: 105,  （当前可用优惠券数量）
                    tickets_claimed: 0,   （已被领取的优惠券数量）
                    tickets_onetime: 3,   （一次默认可领取优惠券数量）
                }
            ]
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/query_coupon_rules">查看样例</a>
    """
    REQ = renderutil.render_request(request)
    code = REQ.get('code')
    codes = code.split(',') if code else []
    cur_date = now(settings.USE_TZ)

    records = CouponRule.objects.filter(is_active=True, end_time__gt=cur_date)
    if len(codes) > 0:
        records = records.filter(code__in=codes)

    start_pos = int(REQ.get('pos', 0))
    page_size = int(REQ.get('size', 10))
    # page_size = page_size if 2 < page_size < 20 else 20 if page_size >= 20 else 2
    if REQ.get('page'):
        start_pos = int(REQ.get('page')) * page_size
    records = records[start_pos:start_pos+page_size]

    result = [r.to_dict() for r in records]
    return json_response(result)


def transfer_reward(request):
    """
    已停用，请使用transfer_order
    转移收益记录给指定用户（及关联订单和相应资金流水）
    :param request （POST）:
        - uid, 转移目标的用户UID
        - rewards, 要转移的收益id列表，多笔收益以英文逗号分隔
    :return:
        成功返回
        {
        "order_cnt": 2,     （转移的订单数量）
        "account_cnt": 1,   （转移的资金流水笔数）
        "reward_cnt": 2,    （转移的收益笔数）
        "errors": []        （转移时出现的错误消息）
        }

        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/transfer_order">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号！')

    rewards = request.POST.get('rewards')
    if not rewards:
        return report_error(u'请指定要转移的收益')

    return json_response(RewardRecord.transfer_reward(user.uid, rewards))


def use_haoli_coupon(request):
    """
    在指定订单中使用优惠券(仅用于土猴好礼)
    :param request(POST):
        - uid, 用户uid
        - haoli_order_no, 订单号
        - coupon, 优惠券编码
    :return:
        成功返回{"result": "ok"}
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/haoli/use_haoli_coupon">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return report_error('无效的用户账号！')

    order_no = request.POST.get('haoli_order_no')
    if not order_no:
        return report_error('缺少订单号')
    coupon = request.POST.get('coupon')
    if not coupon:
        return report_error('缺少优惠券编码')

    try:
        coupon = CouponTicket.objects.get(code=coupon)
        if coupon.consumer != user.uid:
            return report_error('该用户无权使用此优惠券')
        is_valid = coupon.is_valid()
        if is_valid is True:
            coupon.order_no = order_no
            coupon.save()
            return renderutil.report_ok()
        else:
            return report_error(is_valid)
    except CouponTicket.DoesNotExist:
        return report_error('优惠券无效')
    except ValueError, e:
        return report_error(e.message)


