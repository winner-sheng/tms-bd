# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from util import renderutil
from util.renderutil import report_error, report_ok, json_response, logger
from profile.views import get_user_by_uid
from credit.models import CreditBook, MedalCatalog, UserMedal, UserTitle, RankTitle, RankSeries
from django.views.decorators.cache import cache_page


def fetch_credit_summary(uid):
    """
    根据给定用户uid获取积分及对应级别信息
    :param uid:
    :return:
    """
    result = CreditBook.get_credit_summary(uid)
    title = CreditBook.get_user_title(uid, result['income'])  # 用累计积分收入判断用户级别
    result.update(title)
    return result


@cache_page(30)
def get_credit_summary(request):
    """
    获取用户积分账户总额及对应级别称号
    :param request(GET):
        - uid, 必填，用户uid
    :return:
        成功返回积分总额，如：
        {
            total: 10,              （积分余额）
            expense: 0,             （积分累计总支出，比如用于消费）
            uid: "test_12345678",
            income: 10,             （积分累计总收入，用于判断用户的级别）
            next_level: 1000,       （用户到下一级称号需要的积分，差额为next_level - income）
            rank_title: "练气",      (用户积分对应的称号)
        }
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/get_credit_summary">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return report_error('无效的用户')

    result = fetch_credit_summary(user.uid)
    return renderutil.json_response(result)


@cache_page(30)
def query_credits(request):
    """
    获取用户积分流水
    :param request(GET):
        - uid，用户uid，则只查询用户的积分流水
        - [is_income], 可选，1为是，0为否，不提供或其它值表示所有
        - [since], 可选，日期时间型，入账时间下限（不包含）
        - [before], 可选，日期时间型，入账时间上限（不包含）
        - [pos], 可选，获取的结果可能存在多页时，给定开始选取的位置，默认为0
        - [size], 可选，获取的结果可能存在多页时，确定返回每页记录数，默认为10
    :return:
        成功返回积分流水列表，如：
        [
            {
                create_by: "",  （后台添加时，为操作账号）
                create_time: "2016-11-07 18:30:01",
                expire_time: "2026-11-05 18:30:01", （失效时间，默认为10年有效期）
                extra_data: "", （关联对象数据，一般是主键，比如D161109XXXXXX.表示订单号）
                extra_type: "", （关联对象类型，比如basedata.Order表示订单）
                figure: 10,     (积分数额)
                id: 1,
                is_income: true,    （是否入账，否为扣除）
                scenario: "",       （获取积分的场景）
                source: "测试",       （积分来源说明）
                uid: "test_12345678",   （用户uid）
            }
        ]
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/query_credits">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return report_error('无效的用户')

    req = request.POST if 'POST' == request.method else request.GET
    records = CreditBook.objects.filter(uid=user.uid)
    is_income = req.get('is_income')
    if is_income in [0, '0']:
        records = records.filter(is_income=False)
    elif is_income in [1, '1']:
        records = records.filter(is_income=True)

    # [since], 入账时间下限（不包含）
    if req.get('since'):
        records = records.filter(create_time__gt=req.get('since'))
    # [before], 入账时间上限（不包含）
    if req.get('before'):
        records = records.filter(create_time__lt=req.get('before'))

    start_pos = int(req.get('pos', 0))
    page_size = int(req.get('size', 10))
    # page_size = page_size if 2 < page_size < 20 else 20 if page_size >= 20 else 2
    if req.get('page'):
        start_pos = int(req.get('page')) * page_size

    records = records[start_pos:start_pos + page_size]

    return renderutil.json_response([rec.to_dict() for rec in records])


def set_credit(request):
    """
    设置积分
    :param request （POST）:
        - uid，用户uid，则只查询用户的积分流水
        - [is_income], 可选，是否入账，默认为是，0为否（即扣除积分）
        - figure, 积分数量，即本次授予用户多少积分
        - source, 积分来源，比如某个任务奖励
        - [scenario], 可选，场景，预留
        - [expire_time], 可选，失效时间，默认有效期10年
        - [extra_type, extra_data]， 可选，关联对象
            extra_type， 关联对象类型，比如"basedata.Order"表示订单
            extra_data, 关联对象数据（一般是主键），比如"D161109KDSFUE"表示订单号
    :return:
        成功返回积分总额，如：
        {
            total: 10,
            expense: 0,
            uid: "test_12345678",
            income: 10
        }
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/set_credit">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return report_error('无效的用户')

    req = request.POST
    figure = req.get('figure')
    if not figure or not figure.isdigit() or int(figure) < 1:
        return report_error('无效的积分：%s' % figure)
    source = req.get('source')
    if not source:
        return report_error('请说明积分来源')

    is_income = '0' != req.get('is_income')

    CreditBook.objects.create(uid=user.uid,
                              is_income=is_income,
                              figure=figure,
                              source=source,
                              scenario=req.get('scenario'),
                              expire_time=req.get('expire_time'),
                              extra_type=req.get('extra_type'),
                              extra_data=req.get('extra_data'))

    total = CreditBook.get_credit_summary(user.uid)
    return renderutil.json_response(total)


def get_user_medals(uid):
    """
    获取用户的所有勋章
    :param uid:
    :return:
    """
    user_medals = UserMedal.objects.filter(uid=uid)
    medals = []
    for um in user_medals:
        item = um.medal.to_dict()
        item['grant_time'] = um.grant_time
        item['uid'] = um.uid
        medals.append(item)
    return medals


@cache_page(30)
def get_medals(request):
    """
    获取所有勋章列表
    :param request (GET):
        - [uid], 可选，用户uid，如果指定uid，则返回用户持有的勋章列表，否则返回所有勋章列表
    :return:
        [
            {
                remark: "完善个人实名资料，通过审核并绑定银行卡",  （勋章说明）
                code: "XEYZ",   （勋章编码）
                name: "信而有证",   （勋章名称）
                image: "http://7xs6ch.com2.z0.glb.qiniucdn.com/static/2016/11/09/address.jpg",    （勋章图片）
                image2: "http://7xs6ch.com2.z0.glb.qiniucdn.com/static/2016/11/09/address.jpg",   （勋章未激活时的图片）
                threshold: 1,   （获取勋章的条件阈值）
                grant_time: "2016-11-09 12:42:46",  (授予勋章时间，仅当提供uid参数时有此信息)
                uid: "test_12345678"       （仅当提供uid参数时有此信息）
            }
        ]
    """
    req = request.POST if request.method == 'POST' else request.GET
    if 'uid' in req:
        user = get_user_by_uid(request)
        if not user:
            return report_error('无效的用户')
        medals = get_user_medals(user.uid)
    else:
        medals = MedalCatalog.objects.all()
        medals = [m.to_dict() for m in medals]

    return json_response(medals)


def set_medal(request):
    """
    设置用户勋章
    :param request (POST):
        - uid，用户uid，则只查询用户的积分流水
        - medal, 勋章编码(见get_medals返回的勋章列表)
    :return:
    """
    user = get_user_by_uid(request)
    if not user:
        return report_error('无效的用户')

    req = request.POST
    medal = req.get('medal')
    if not medal:
        return report_error('请提供勋章编码')
    try:
        medal = MedalCatalog.objects.get(code=medal)
    except MedalCatalog.DoesNotExist:
        return report_error('勋章[%s]不存在' % medal)
    else:
        UserMedal.objects.get_or_create(uid=user.uid,
                                        medal_id=medal.id)
        return report_ok()
