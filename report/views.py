# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response
from django.db import connection

from tms import settings
from util.renderutil import json_response, report_ok, report_error, export_csv, export_excel, day_str, logger, now
from report.models import RewardSummary, TmsReport
from basedata.models import Order
from vendor.models import SupplierManager
from profile.views import get_user_by_uid
from decimal import Decimal
from datetime import datetime
import json


@login_required
def export_reward(request):
    """
    导出收益列表
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

        records = RewardSummary.objects.all()
        if ids == 'select_across':  # across selected in one page
            records = records.filter(uid__in=request.session.get('selected_for_export', []))
            del request.session['selected_for_export']
        elif ids != 'all':
            id_list = ids.split(',')
            records = records.filter(uid__in=id_list)

        output_format = request.REQUEST.get('format', 'excel')  # 默认导出excel格式

        records = records.values_list('real_name', 'nick_name', 'mobile', 'total_cnt', 'settled_reward',
                                      'must_settled_reward', 'not_settled_reward', 'revoked_reward',
                                      'uid', 'ex_nick_name',)
        if output_format == 'json':
            return json_response(records)
        else:
            data = [(u"姓名", u"昵称", u"手机", u"收益总笔数", u"已结算收益", u"已结算未入账收益",
                     u"未结算收益", u"已撤销收益", u"用户ID", u"昵称（第三方）", )]
            data.extend(records)
            file_name = "reward_%s.xls" % day_str()
            return export_excel(file_name, data)
    except ObjectDoesNotExist:
        return report_error('没有数据')


class Report(object):
    name = '报表'
    description = ''  # 报表描述
    group = None  # 分组名称
    permission = 'report'
    output_template = 'admin/report/data_block.html'
    output_template_str = None
    input_template = ''
    input_template_str = None
    max_size = 500
    field_names = None  # use immutable list
    _sql = ''
    _data = []
    _summary_sql = ''
    _summary_data = []
    _params = {}
    _user = None
    _dict = {}

    def __init__(self, user=None, **kwargs):
        """
        初始化
        """
        super(Report, self).__init__()
        self._user = user
        self._dict = kwargs

    def has_permission(self):
        """
        判断用户是否有访问权限
        """
        return self._user and self._user.has_module_perms('report')

    @property
    def summary(self):
        if self._summary_data:
            return self._summary_data
        else:
            cursor = connection.cursor()
            cursor.execute(self._summary_sql, self._params)
            self._summary_data = cursor.fetchone()

            return self._summary_data

    @property
    def data(self):
        if self._data:
            return self._data
        else:
            cursor = connection.cursor()
            cursor.execute(self._sql, self._params)
            for row in cursor.fetchall():
                self._data.append(row)

            return self._data

@login_required
# @cache_page(30, key_prefix="tms.api")
def report(request):
    """
    查看统计报表
    :param request:
    :return:
        {
            orderBy : 4,    (排序字段)
            header : [
                "支付金额",
                "商品总额",
                "商品优惠",
                "邮费",
                "邮费优惠",
                "商品总数",
                "包裹总数"
            ],
            data : [[   （数据）
                    "99.00",
                    "99.00",
                    "0.00",
                    "0.00",
                    "0.00",
                    1,
                    1
                ], ...],
            isAsc : false,  （是否升序）
            summary : [     （汇总数据）
                "218382.00",
                "222890.00",
                "4560.00",
                "52.00",
                "0.00",
                "2136",
                "1611"
            ]
        }

    """
    if not request.user.is_superuser and not request.user.has_module_perms('report'):
        return report_error('访问未授权！')

    reports = [
        ('订单', None),
        ('order_income_by_pay', order_income_by_pay,),
        ('order_income_by_signoff', order_income_by_signoff,),
        ('order_monthly_summary', order_monthly_summary,),
        ('order_daily_summary', order_daily_summary,),
        ('order_hourly_summary', order_hourly_summary,),
        ('order_summary_by_state', order_summary_by_state,),
        ('order_summary_by_province', order_summary_by_province,),
        ('order_summary_by_agent', order_summary_by_agent,),
        ('商品', None),
        ('product_sales', product_sales,),
        ('product_sales_by_supplier', product_sales_by_supplier,),
        ('product_sales_by_agent', product_sales_by_agent,),
        ('用户', None),
        ('user_daily_summary', user_daily_summary,),
        ('user_reward_report', user_reward_report,),
        ('user_reward_report_local', user_reward_report_local,),
        ('user_reward_report_express', user_reward_report_express,),
        ('user_referrer_summary', user_referrer_summary,),
        ('user_cumulated_referrer_summary', user_cumulated_referrer_summary,),
        ('user_cascade_reward', user_cascade_reward,),
        ('user_reorder_differ_day', user_reorder_differ_day,),
        ('user_credits_report', user_credits_report,),
        ('credits_distribution', credits_distribution,),
        ('财务', None),
        ('account_book_summary', account_book_summary,),
        ('finance_margin_detail', finance_margin_detail,),
        ('finance_sale_report', finance_sale_report,),
        ('finance_purchase_report', finance_purchase_report,),
        ('finance_supplier_detail', finance_supplier_detail,),
    ]

    req = request.POST if 'POST' == request.method else request.GET
    if not req.get('type'):
        accessable = []
        for k, v in reports:
            if callable(v):
                if not request.user.has_perm(v.permission):
                    continue
                accessable.append((k, v.name))
            else:
                accessable.append((k, None))

        return render_to_response('admin/report/report.html', {"reports": accessable})
    else:
        reports = dict(reports)
        result = {}
        report_type = req.get('type')
        report = reports.get(report_type)
        if callable(report) and request.user.has_perm(report.permission):
            try:
                result = report(user=request.user, filter=req)
            except Exception, e:
                logger.exception(e)
                return report_error(e.message)
            # result = reports[report_type](request)
        else:
            logger.error('无效的报表：%s' % report_type)

        if 'export' == req.get('action'):
            res = [result.get('header')]
            res += result.get('data')
            res.append(result.get('summary'))
            if 'csv' in req:
                file_name = "%s_%s.csv" % (report_type, day_str())
                return export_csv(file_name, res)
            else:
                file_name = "%s_%s.xls" % (report_type, day_str())
                return export_excel(file_name, res)
        else:
            return json_response(result)


def query(request):
    """
    查询指定用户可见的报表清单
    :param request(GET):
        - uid, 用户uid（需已绑定后台管理账号，否则报错“未绑定管理账号或管理账号无效”）
        - [pos], 可选，起始偏移量，默认为0
        - [size]，可选，一次获取多少条数据，默认为10，取值范围2~20
        - [start_since], 可选，即报表数据开始时间(包含)，提供该参数后只返回统计周期在指定时间之后开始的报表
        - [end_before], 可选，即报表数据结束时间（不包含），提供该参数后只返回统计周期在指定时间之前结束的报表
        - [is_sent], 可选，是否已发送通知
            * 1，是
            * 0， 否
            * all, 全部（默认）
        - [is_confirmed], 可选，是否已被确认，（已废弃，请改用status）
            * 1，是
            * 0， 否
            * all, 全部（默认）
        - [status], 可选，审核状态
            * 0, 待审核
            * 1, 已确认
            * 2，有疑问
            * all, 全部（默认）
    :return:
        成功返回
        [
            {
                is_confirmed: false,
                title: "[南湾果园]订单收入/退款统计（20160901 - 20160916）",
                start_time: "2016-09-01 00:00:00",
                is_sent: false,
                end_time: "2016-09-16 00:00:00",
                report_type: "order_income_by_signoff",
                id: 15
            }
        ]
        失败返回{error: msg}

    eg. <a href="/tms-api/report/query">查看样例</a>
    """
    user = get_user_by_uid(request, as_internal=True)
    if not user:
        return report_error('无效的用户账号！')
    elif not hasattr(user, 'internal_user') or not getattr(user, 'internal_user'):
        return report_error('未绑定管理账号或管理账号无效')

    if user.internal_user.is_superuser:
        records = TmsReport.objects.all()
    else:
        suppliers = SupplierManager.objects.filter(user=user.internal_user).values_list('supplier_id', flat=True)
        records = TmsReport.objects.filter(owner__in=["SUP-%s" % sup for sup in suppliers])

    if 'start_since' in request.REQUEST:
        records = records.filter(start_time__gte=request.REQUEST.get('start_since'))
    if 'end_before' in request.REQUEST:
        records = records.filter(end_time__lt=request.REQUEST.get('end_before'))
    if request.REQUEST.get('is_sent') == '1':
        records = records.filter(is_sent=True)
    elif request.REQUEST.get('is_sent') == '0':
        records = records.filter(is_sent=False)

    if 'status' in request.REQUEST and'all' != request.REQUEST.get('status'):
        records = records.filter(status=request.REQUEST.get('status'))
    # TODO: to be removed, 暂时保留以便兼容线上版本
    if request.REQUEST.get('is_confirmed') == '1':
        records = records.filter(status=TmsReport.STATUS_CONFIRMED)
    elif request.REQUEST.get('is_confirmed') == '0':
        records = records.exclude(status=TmsReport.STATUS_CONFIRMED)

    start_pos = int(request.REQUEST.get('pos', 0))
    page_size = int(request.REQUEST.get('size', 10))
    # page_size = page_size if 2 < page_size < 20 else 20 if page_size >= 20 else 2
    if request.REQUEST.get('page'):
        start_pos = int(request.REQUEST.get('page')) * page_size
    records = records[start_pos:start_pos+page_size]

    return json_response([r.to_dict() for r in records])


def get(request):
    """
    查看统计报表
    :param request(GET):
        - uid, 用户uid（需已绑定后台管理账号，否则报错“未绑定管理账号或管理账号无效”）,用于校验用户访问权限
        - id, 报表id
        - [action，[csv|excel]]，可选，默认为json
            * json，以json格式返回
            * export，导出文件，当要求导出时，默认返回excel格式文件，可提供参数csv以返回csv格式的文件

    :return:
        返回指定格式数据，json格式数据形如（不同报表包含的列数据不同）：
        {
            bill_total: "12300.00",         (账单总额，等于应付货款+运费总额-运费优惠-退款金额（不超过货款以退款金额为准，超过货款则以货款为准）)
            confirmed_by: null,             （确认人uid）
            confirmed_time: null,                       （是否已被owner确认）
            create_time: "2016-09-18 20:36:28",         （报表创建时间）
            data:       （报表数据，二维数组转存的字符串）
                "[["145.00", "155.00", "10.00", "0.00", "0.00", 2, 1], ...]",
            end_time: "2016-09-16 00:00:00",            （报表统计周期的截止时间）
            header:     （报表统计字段标题）
                "["支付金额", "商品总额", "商品优惠", "邮费", "邮费优惠", "商品总数", "包裹总数"]",
            id: 15
            is_confirmed: false,             （是否已被owner确认）
            is_sent: false,                             （是否已发送通知给相关方）
            memo: null,                                  （备注）
            owner: "SUP-1",         （组合值，形如"类型-对象id"。可以是供应商，如SUP-<supplier_id>，也可能是用户，如UID-<end_user_uid>等）
            report_type: "order_income_by_signoff",     (报表类型)
            start_time: "2016-09-01 00:00:00",         （报表统计周期的开始时间）
            summary:    （报表汇总数据，可能有数据，也可能只是空数组）
                "["12012.00", "12297.00", "305.00", "20.00", "0.00", "131", "57"]",
            title: "[南湾果园]订单收入/退款统计（20160901 - 20160916）",
        }

    eg. <a href="/tms-api/report/get">查看样例</a>
    """
    user = get_user_by_uid(request, as_internal=True)
    if not user:
        return report_error('无效的用户账号！')
    elif user.internal_user is None:
        return report_error('未绑定管理账号或管理账号无效')

    if not request.REQUEST.get('id'):
        return report_error('未指定报表！')
    else:
        try:
            report = TmsReport.objects.get(id=request.REQUEST.get('id'))
            if not user.internal_user.is_superuser:
                if report.owner[:4] == "SUP-" and \
                        not SupplierManager.objects.filter(supplier_id=report.owner[4:],
                                                           user_id=user.internal_user.id).exists():
                    return report_error('没有访问权限！')

            summary = json.loads(report.summary)
            # 区分账单数据版本，版本2比1多一列“供应商退款”
            if report.version == 1:
                shipfee_total = Decimal(summary[8] or 0) - Decimal(summary[9] or 0)
                bill_total = Decimal(summary[13] or 0) + shipfee_total - Decimal(summary[14] or 0)
            else:
                # shipfee_total = Decimal(summary[1][4] or 0) - Decimal(summary[1][5] or 0)
                bill_total = Decimal(summary[0][1] or 0)

            if 'export' == request.REQUEST.get('action'):
                res = [json.loads(report.header)]
                res += json.loads(report.data)
                if report.version == 1:
                    res.append(('账单总额', bill_total))
                else:
                    res.append(summary)

                if 'csv' in request.REQUEST:
                    file_name = "%s_%s.csv" % (report.owner, day_str())
                    return export_csv(file_name, res)
                else:
                    file_name = "%s_%s.xls" % (report.owner, day_str())
                    return export_excel(file_name, res)
            else:
                report = report.to_dict(detail=True)
                report['bill_total'] = bill_total
                return json_response(report)
        except TmsReport.DoesNotExist:
            return report_error('找不到该报表(ID:%s)' % request.REQUEST.get('id'))


def feedback(request):
    """
    查看统计报表
    :param request(POST):
        - uid, 用户uid（需已绑定后台管理账号，否则报错“未绑定管理账号或管理账号无效”）,用于校验用户访问权限
        - id, 报表id
        - is_confirmed, 是否认可（已确认的报表不可再修改），1为是，其它为否
        - [memo]，可选，备注信息

    :return:
        成功返回{result: ok}, 失败返回{error: msg}

    eg. <a href="/tms-api/report/feedback">查看样例</a>
    """
    if request.user.is_anonymous():
        user = get_user_by_uid(request, as_internal=True)
        if not user:
            return report_error('无效的用户账号！')
        elif user.internal_user is None:
            return report_error('未绑定管理账号或管理账号无效')
        rp_owner = user.internal_user
    else:
        rp_owner = request.user

    if not request.POST.get('id'):
        return report_error('未指定报表！')
    else:
        try:
            rp = TmsReport.objects.get(id=request.POST.get('id'))
            if not rp_owner.is_superuser:
                if rp.owner[:4] == "SUP-" and \
                        not SupplierManager.objects.filter(supplier_id=rp.owner[4:],
                                                           user_id=rp_owner.id).exists():
                    return report_error('没有访问权限！')
            elif rp.status == TmsReport.STATUS_CONFIRMED:
                return report_error('已确认过的报表不可修改！')

            rp.status = TmsReport.STATUS_CONFIRMED if '1' == request.POST.get('is_confirmed') else TmsReport.STATUS_QUESTION
            rp.memo = request.POST.get('memo')
            rp.confirmed_by = rp_owner.username
            rp.confirmed_time = now(settings.USE_TZ)
            rp.save()
            return report_ok()
        except TmsReport.DoesNotExist:
            return report_error('找不到该报表(ID:%s)' % request.POST.get('id'))


# class OrderIncomePerPayReport(Report):
#     name = '订单收入/退款统计（按付款时间）'
#     field_names = (u'订单号', u'订单状态', u'订单简介', u'付款时间', u'签收时间', u'支付金额', u'商品总额', u'购物优惠',
#                    u'邮费', u'邮费优惠', u'商品总数', u'包裹总数', u'供应商', u'供货价', u'退款金额', u'退款时间',)
#
#     def __init__(self, user=None, **kwargs):
#         """
#         初始化
#         """
#         super(OrderIncomePerPayReport, self).__init__(user=user, **kwargs)
#
#         sql = """
#             select a.order_no, a.order_state,
#             (select group_concat(concat('[', x.product_id, ']', y.name, '(￥', x.deal_price ,')', '*', x.pcs) separator ';<br>')
#                 from basedata_orderitem as x
#                 join basedata_product as y
#                 on x.product_id = y.code
#                 where x.order_id=a.order_no) as brief,
#             a.pay_date, a.signoff_date, a.pay_amount as pay_amount,
#             a.shop_amount,
#             a.shop_amount_off, a.ship_fee, a.ship_fee_off, a.pcs_amount, a.package_pcs,
#             b.name,
#             (select sum(x.cost * x.pcs) as cost
#                 from basedata_orderitem as x
#                 where x.order_id=a.order_no) as cost,
#             a.refunded_fee, a.refund_date
#             from basedata_order as a
#              left join vendor_supplier as b on a.supplier_id = b.id
#              where a.pay_date is not null %s
#             """
#         kwargs = kwargs or {}
#         conditions = []
#         params = []
#         if kwargs.get('from'):
#             conditions.append(' and pay_date >= %s')
#             params.append(kwargs.get('from'))
#         if kwargs.get('to'):
#             conditions.append(' and pay_date < %s')
#             params.append(kwargs.get('to'))
#         # if 'export' != request.GET.get('action'):
#         #     limit = request.GET.get('size', 20)
#         #     pos = request.GET.get('pos', 0)
#         #     sql += ' limit %s offset %s;'
#         #     params.extend([limit, pos])
#
#         data = [(u'订单号', u'订单状态', u'订单简介', u'付款时间', u'签收时间', u'支付金额', u'商品总额', u'商品优惠',
#                  u'邮费', u'邮费优惠', u'商品总数', u'包裹总数', u'供应商', u'供货价', u'退款金额', u'退款时间',)]
#
#         order_by = int(kwargs.get('orderBy', 4))
#         sql += " order by %s" % order_by
#         is_asc = 'isAsc' in kwargs
#         sql += " asc" if is_asc else " desc"
#         sql_condition = ''.join(conditions)
#         self._sql = sql % sql_condition
#         self._params = params
#         logger.debug(self._sql)
#
#         summary_sql = """
#             select sum(a.pay_amount), sum(a.shop_amount), sum(a.shop_amount_off), sum(a.ship_fee), sum(a.ship_fee_off),
#             sum(a.pcs_amount), sum(a.package_pcs), sum(x.cost * x.pcs), sum(a.refunded_fee)
#             from basedata_order as a
#             join (select c.order_no, sum(if(x.cost, x.cost * x.pcs, y.cost * x.pcs)) as cost
#                 from basedata_order as c
#                 join basedata_orderitem as x on c.order_no = x.order_id
#                 join basedata_product as y on x.product_id = y.code
#                 group by c.order_no) as b on a.order_no = b.order_no
#                 where a.pay_date is not null %s
#             """
#         self._summary_sql = summary_sql % sql_condition


def order_periodical_summary(request):
    """
    按指定时段统计指定状态的订单汇总数据
    :param request (GET):
        - [agent_id], 可选，渠道id，默认为布丁（无值的时候）
        - [from_date], 可选，统计周期开始时间
        - [to_date]，可选，统计周期截止时间，默认为当前时间
        - [states], 订单状态(默认统计成交的订单，不包含维权的)，可以是多个状态值的集合，用英文逗号分隔，如“2,3,5”
        - [group_by], 可选'month'（按月）, 'day'（按日）, 'week'（按周）, 'year'(按年)， "merge'（汇总），默认按月统计

    :return:
        成功返回如下列表:
        [
            {
                "order_period": "2016-04",
                "order_cnt": 260,   （成交的订单数，不含维权订单）
                "agent_id": null,
                "order_amount": "51688.00"  （成交的订单总额，不含维权订单）
            },
            {
                "order_period": "2016-05",
                "order_cnt": 920,
                "agent_id": null,
                "order_amount": "141808.00"
            },
        ]
        注意：如果某个时段没有数据，则不会出现在列表中

    eg. <a href="/tms-api/report/order_periodical_summary">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    from_date = req.get('from_date')
    to_date = req.get('to_date')
    agent_id = req.get('agent_id')
    states = req.get('states')
    if states:
        states = states.split(',')
    else:
        states = (Order.STATE_SHIPPED,
                  Order.STATE_RECEIVED_BYSELF,
                  Order.STATE_RECEIVED,
                  Order.STATE_TO_SHIP,
                  Order.STATE_TO_PACK,
                  Order.STATE_TO_CLAIM, )
    states = [str(s) for s in states if isinstance(s, int) or (isinstance(s, basestring) and s.isdigit())]
    group_by = req.get('group_by')

    group_dict = {'month': '%Y-%m', 'day': '%Y-%m-%d', 'week': '%Y-w%v', 'year': '%Y', 'merge': ''}
    sql = """
        select agent_id,
            %(group)s
            count(order_no) as order_cnt,
            sum(pay_amount) as order_amount
            from basedata_order
        where order_state in (%(states)s) %(condition)s
        %(group2)s
        """
    conditions = []
    params = {}  # 拼接sql使用
    sql_params = {}  # 执行sql传参
    if agent_id:
        conditions.append(' and agent_id = %(agent_id)s')
        sql_params['agent_id'] = agent_id
    else:
        conditions.append(' and agent_id is null')

    if group_by != 'merge':
        params['group'] = " DATE_FORMAT(pay_date, %(format)s) as order_period, "
        params['group2'] = ' group by 2'
        sql_params['format'] = group_dict.get(group_by) or group_dict.get('month')
    else:
        params['group'] = "'-', "
        params['group2'] = ""

    params['states'] = ','.join(states)
    if from_date:
        conditions.append(' and pay_date >= %(from_date)s')
        sql_params['from_date'] = from_date
    if to_date:
        conditions.append(' and pay_date < %(to_date)s')
        sql_params['to_date'] = to_date
    params['condition'] = ''.join(conditions)
    header = ['agent_id', 'order_period', 'order_cnt', 'order_amount']

    sql %= params
    logger.debug(sql)
    cursor = connection.cursor()
    cursor.execute(sql, sql_params)
    data = [dict(zip(header, row)) for row in cursor.fetchall()]
    return json_response(data)


def order_income_by_pay(user=None, filter=None, supplier=None):
    """
    订单收入/退款统计（列表）
    :param request:
    :return:
    """
    state_dict = dict(Order.ORDER_STATES)
    sql = """
        select a.order_no, if(c.name is null, '布丁', c.name) as agent, a.order_state,
        (select group_concat(concat('[', x.product_id, ']', y.name, '(￥', x.deal_price ,')', '*', x.pcs) separator ';<br>')
            from basedata_orderitem as x
            join basedata_product as y
            on x.product_id = y.code
            where x.order_id=a.order_no) as brief,
        a.pay_date, a.signoff_date, a.pay_amount, a.balance_payment, a.credits_expense,
        a.shop_amount,
        a.shop_amount_off, a.ship_fee, a.ship_fee_off, a.pcs_amount, a.package_pcs,
        b.name, (select sum(if(x.cost, x.cost * x.pcs, y.cost * x.pcs))  as cost
            from basedata_orderitem as x
            join basedata_product as y
            on x.product_id = y.code
            where a.order_no = x.order_id),
        a.refunded_fee, a.refund_date
        from basedata_order as a
         left join vendor_supplier as b on a.supplier_id = b.id
         left join vendor_salesagent as c on a.agent_id = c.id
         where a.pay_date is not null %s
        """
    conditions = []
    params = []
    if filter.get('from'):
        conditions.append(' and pay_date >= %s')
        params.append(filter.get('from'))
    if filter.get('to'):
        conditions.append(' and pay_date < %s')
        params.append(filter.get('to'))

    if supplier:
        conditions.append(' and a.supplier_id = %s')
        params.append(supplier.id)
    elif user:
        if not user.is_superuser and user.has_perm('basedata.as_supplier'):
            conditions.append(' and a.supplier_id = %s')
            suppliers = SupplierManager.objects.filter(user=user).values_list('supplier_id', flat=True)
            if len(suppliers) > 0:
                params.append(suppliers[0])  # 暂只支持一个用户属于一家供应商
            else:
                params.append('')
    else:
        raise ValueError('必须指明供应商或用户')
    # if 'export' != filter.get('action'):
    #     limit = filter.get('size', 20)
    #     pos = filter.get('pos', 0)
    #     sql += ' limit %s offset %s;'
    #     params.extend([limit, pos])

    header = (u'订单号', '渠道', u'订单状态', u'订单简介', u'付款时间', u'签收时间', u'支付金额', u'余额支付', u'积分扣抵',
              u'商品总额', u'商品优惠', u'邮费', u'邮费优惠', u'商品总数', u'包裹总数',
              u'供应商', u'供货价', u'退款金额', u'退款时间',)
    data = []

    order_by = int(filter.get('orderBy', 5))
    order_by = order_by if 0 < order_by <= len(header) else 5
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql_condition = ''.join(conditions)
    sql = sql % sql_condition
    logger.debug(sql)
    cursor = connection.cursor()
    cursor.execute(sql, params)
    for row in cursor.fetchall():
        row = list(row)
        row[2] = state_dict.get(row[2], u'未知')
        data.append(row)

    summary_sql = """
        select '-', '-', '-', '-', '-', '-',
        sum(a.pay_amount), sum(a.shop_amount), sum(a.shop_amount_off), sum(a.ship_fee), sum(a.ship_fee_off),
        sum(a.pcs_amount), sum(a.package_pcs), '-', b.cost,
            sum(a.refunded_fee), '-', '-'
        from basedata_order as a,
            (select sum(if(x.cost, x.cost * x.pcs, y.cost * x.pcs)) as cost
            from basedata_order as a
            join basedata_orderitem as x on a.order_no = x.order_id
            join basedata_product as y on x.product_id = y.code
            where a.pay_date is not null %s) as b
        where a.pay_date is not null %s
        """
    summary_sql = summary_sql % (sql_condition, sql_condition)
    cursor.execute(summary_sql, params*2)
    summary_row = cursor.fetchone()

    return {"data": data,
            "header": header,
            "summary": summary_row,
            "orderBy": order_by,
            "isAsc": is_asc}


order_income_by_pay.name = '订单收入/退款统计（按付款时间）'
order_income_by_pay.permission = 'report.view_order_income_by_pay'


def order_income_by_signoff(user=None, filter=None, supplier=None):
    """
    订单收入/退款统计（列表，按签收时间）
    :param request:
    :return:
    """
    state_dict = dict(Order.ORDER_STATES)
    sql = """
        select a.order_no, if(c.name is null, '布丁', c.name) as agent, a.order_state,
        (select group_concat(concat('[', x.product_id, ']', y.name, '(￥', x.deal_price ,')', '*', x.pcs) separator ';<br>')
            from basedata_orderitem as x
            join basedata_product as y
            on x.product_id = y.code
            where x.order_id=a.order_no) as brief,
        a.pay_date, a.signoff_date, a.pay_amount, a.balance_payment, a.credits_expense,
        a.shop_amount,
        a.shop_amount_off, a.ship_fee, a.ship_fee_off, a.pcs_amount, a.package_pcs,
        b.name, (select sum(if(x.cost, x.cost * x.pcs, y.cost * x.pcs))  as cost
            from basedata_orderitem as x
            join basedata_product as y
            on x.product_id = y.code
            where a.order_no = x.order_id),
        a.refunded_fee, a.refund_date
        from basedata_order as a
         left join vendor_supplier as b on a.supplier_id = b.id
         left join vendor_salesagent as c on a.agent_id = c.id
         where a.signoff_date is not null %s
        """
    cursor = connection.cursor()
    conditions = []
    params = {}
    from_date = filter.get('from')
    to_date = filter.get('to')
    if from_date:
        conditions.append(' and (signoff_date >= %(from_date)s or refund_date >= %(from_date)s)')
        params['from_date'] = from_date
    if to_date:
        conditions.append(' and (signoff_date < %(to_date)s or refund_date < %(to_date)s)')
        params['to_date'] = to_date
    if supplier:
        conditions.append(' and a.supplier_id = %(supplier_id)s')
        params['supplier_id'] = supplier.id
    elif user:
        if not user.is_superuser and user.has_perm('basedata.as_supplier'):
            conditions.append(' and a.supplier_id = %(supplier_id)s')
            suppliers = SupplierManager.objects.filter(user=user).values_list('supplier_id', flat=True)
            if len(suppliers) > 0:
                params['supplier_id'] = suppliers[0]  # 暂只支持一个用户属于一家供应商
            else:
                params['supplier_id'] = ''
    else:
        raise ValueError('必须指明供应商或用户')
    # if 'export' != filter.get('action'):
    #     limit = filter.get('size', 20)
    #     pos = filter.get('pos', 0)
    #     sql += ' limit %s offset %s;'
    #     params.extend([limit, pos])

    header = (u'订单号', '渠道', u'订单状态', u'订单简介', u'付款时间', u'签收时间', u'支付金额', u'余额支付', u'积分扣抵',
              u'商品总额', u'商品优惠', u'邮费', u'邮费优惠', u'商品总数', u'包裹总数',
              u'供应商', u'供货价', u'退款金额', u'退款时间',)
    data = []
    order_by = int(filter.get('orderBy', 6))
    order_by = order_by if 0 < order_by <= len(header) else 6
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql_condition = ''.join(conditions)
    sql = sql % sql_condition
    logger.debug(sql)
    cursor.execute(sql, params)
    for row in cursor.fetchall():
        row = list(row)
        row[2] = state_dict.get(row[2], u'未知')
        data.append(row)

    summary_sql = """
        select '-', '-', '-', '-', '-', '-', sum(a.pay_amount), sum(a.shop_amount),
        sum(a.shop_amount_off), sum(a.ship_fee), sum(a.ship_fee_off), sum(a.pcs_amount), sum(a.package_pcs),
        '-',
        b.cost,
        sum(a.refunded_fee), '-'
        from basedata_order as a,
        (select sum(if(x.cost, x.cost * x.pcs, y.cost * x.pcs)) as cost
            from basedata_order as a    # 注意为了重用a.supplier_id的参数，此处别名与主SQL的重复
            join basedata_orderitem as x on a.order_no = x.order_id
            join basedata_product as y on x.product_id = y.code
            where signoff_date is not null %s) as b
        where a.signoff_date is not null %s
        """
    summary_sql = summary_sql % (sql_condition, sql_condition)
    cursor.execute(summary_sql, params)
    summary_row = cursor.fetchone()

    return {"data": data,
            "header": header,
            "summary": summary_row,
            "orderBy": order_by,
            "isAsc": is_asc}


order_income_by_signoff.name = '订单收入/退款统计（按签收时间）'
order_income_by_signoff.permission = 'report.view_order_income_by_signoff'


def order_summary_by_state(user=None, filter=None, supplier=None):
    """
    订单汇总统计（按订单状态统计金额，单量等）
    :param request:
    :return:
    """
    sql = """
        select a.order_state,
            count(order_no) as order_cnt,
            sum(a.pay_amount+a.balance_payment+a.credits_expense/100) as pay_amount,
            avg(a.pay_amount+a.balance_payment+a.credits_expense/100) as avg_amount,
            avg(a.ship_fee-a.ship_fee_off) as avg_ship_fee,
            sum(a.shop_amount) as shop_amount,
            sum(a.ship_fee-a.ship_fee_off) as sum_ship_fee,
            sum(a.shop_amount_off+a.ship_fee_off) as sum_pay_off
        from basedata_order as a
        where a.master_order_id is null %s
        group by a.order_state
        """
    cursor = connection.cursor()
    conditions = []
    params = []
    if filter.get('from'):
        conditions.append(' and pay_date >= %s')
        params.append(filter.get('from'))
    if filter.get('to'):
        conditions.append(' and pay_date < %s')
        params.append(filter.get('to'))

    header = (u'订单状态', u'订单数', u'订单总额（￥）', u'客单价（￥）', u'邮费/单(￥)',
              u'购物总额（￥，不含优惠）', u'邮费总额(￥)', u'优惠总额(￥)', )
    data = []
    order_by = int(filter.get('orderBy', 3))
    order_by = order_by if 0 < order_by <= len(header) else 3
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql = sql % ''.join(conditions)
    logger.debug(sql)
    cursor.execute(sql, params)
    state_dict = dict(Order.ORDER_STATES)
    for row in cursor.fetchall():
        row = list(row)
        row[0] = state_dict.get(row[0], u'未知')
        row[2] = row[2].quantize(Decimal('1.00'))
        row[3] = row[3].quantize(Decimal('1.00'))
        row[4] = row[4].quantize(Decimal('1.00'))
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


order_summary_by_state.name = '订单销售统计（按状态）'
order_summary_by_state.permission = 'report.view_order_summary_by_state'


def order_summary_by_province(user=None, filter=None, supplier=None):
    """
    订单汇总统计（按订单收件省份）
    :param request:
    :return:
    """
    sql = """
        select a.ship_province,
            count(order_no) as order_cnt,
            sum(a.pay_amount+a.balance_payment+a.credits_expense/100) as pay_amount,
            count(if(a.order_state in (4, 5, 96), a.order_no, null)) as refund_cnt,
            sum(if(a.order_state in (4, 5, 96), a.pay_amount+a.balance_payment+a.credits_expense/100, 0)) as may_refund,
            avg(a.pay_amount+a.balance_payment+a.credits_expense/100) as avg_amount,
            avg(a.ship_fee-a.ship_fee_off) as avg_ship_fee,
            sum(a.shop_amount) as shop_amount,
            sum(a.ship_fee-a.ship_fee_off) as sum_ship_fee,
            sum(a.shop_amount_off+a.ship_fee_off) as sum_pay_off
        from basedata_order as a
        where a.master_order_id is null and a.order_state not in (0, 98, 999)
        AND (a.agent_id <>7 or a.agent_id is NULL)
        %s
        group by a.ship_province
        """
    cursor = connection.cursor()
    conditions = []
    params = []
    if filter.get('from'):
        conditions.append(' and pay_date >= %s')
        params.append(filter.get('from'))
    if filter.get('to'):
        conditions.append(' and pay_date < %s')
        params.append(filter.get('to'))

    header = (u'收件省份', u'订单数', u'订单总额（￥）', '维权单数', '维权总额（￥）', u'客单价（￥）',
              u'邮费金额/单(￥)', '购物总额（￥，不含优惠）', u'邮费总额(￥)', u'优惠总额(￥)', )
    data = []
    order_by = int(filter.get('orderBy', 3))
    order_by = order_by if 0 < order_by <= len(header) else 3
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql = sql % ''.join(conditions)
    logger.debug(sql)
    cursor.execute(sql, params)
    for row in cursor.fetchall():
        row = list(row)
        row[2] = row[2].quantize(Decimal('1.00'))
        row[4] = row[4].quantize(Decimal('1.00'))
        row[5] = row[5].quantize(Decimal('1.00'))
        row[6] = row[6].quantize(Decimal('1.00'))
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


order_summary_by_province.name = '订单销售统计（按省份）'
order_summary_by_province.permission = 'report.view_order_summary_by_province'


def order_summary_by_agent(user=None, filter=None, supplier=None):
    """
    订单汇总统计（按渠道）
    :param request:
    :return:
    """
    sql = """
        select if(d.name is null, '布丁', d.name) as agent,
            count(order_no) as order_cnt,
            sum(a.pay_amount+a.balance_payment+a.credits_expense/100) as pay_amount,
            count(if(a.order_state in (4, 5, 96), a.order_no, null)) as refund_cnt,
            sum(if(a.order_state in (4, 5, 96), a.pay_amount+a.balance_payment+a.credits_expense/100, 0)) as may_refund,
            avg(a.pay_amount+a.balance_payment+a.credits_expense/100) as avg_amount,
            avg(a.ship_fee-a.ship_fee_off) as avg_ship_fee,
            sum(a.shop_amount) as shop_amount,
            sum(a.ship_fee-a.ship_fee_off) as sum_ship_fee,
            sum(a.shop_amount_off+a.ship_fee_off) as sum_pay_off
        from basedata_order as a
        left join vendor_salesagent as d on d.id = a.agent_id
        where a.master_order_id is null and a.order_state not in (0, 98, 999) %s
        group by d.id
        """
    cursor = connection.cursor()
    conditions = []
    params = []
    if filter.get('from'):
        conditions.append(' and pay_date >= %s')
        params.append(filter.get('from'))
    if filter.get('to'):
        conditions.append(' and pay_date < %s')
        params.append(filter.get('to'))

    header = (u'销售渠道', u'订单数', u'成交总额（￥）', '维权单数', '维权总额（￥）', u'客单价（￥）',
              u'邮费金额/单(￥)', u'购物总额（￥，不含优惠）', u'邮费总额(￥)', u'优惠总额(￥)', )
    data = []
    order_by = int(filter.get('orderBy', 3))
    order_by = order_by if 0 < order_by <= len(header) else 3
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql = sql % ''.join(conditions)
    logger.debug(sql)
    cursor.execute(sql, params)
    for row in cursor.fetchall():
        row = list(row)
        row[2] = row[2].quantize(Decimal('1.00'))
        row[4] = row[4].quantize(Decimal('1.00'))
        row[5] = row[5].quantize(Decimal('1.00'))
        row[6] = row[6].quantize(Decimal('1.00'))
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


order_summary_by_agent.name = '订单销售统计（按渠道）'
order_summary_by_agent.permission = 'report.view_order_summary_by_agent'


def order_daily_summary(user=None, filter=None, supplier=None):
    """
    每日订单销售统计（按日期统计成交金额，单量等）
    :param request:
    :return:
    """
    sql = """
        select DATE_FORMAT(pay_date, '%%%%Y-%%%%m-%%%%d') as order_pay_date,
        count(order_no) as order_cnt, %(seg_user_summary)s
        sum(a.pay_amount+a.balance_payment+a.credits_expense/100) as pay_amount,
        count(if(a.order_state in (4, 5, 96), a.order_no, null)) as refund_cnt,
        sum(if(a.order_state in (4, 5, 96), a.pay_amount+a.balance_payment+a.credits_expense/100, 0)) as may_refund,
        avg(a.pay_amount+a.balance_payment+a.credits_expense/100) as avg_amount,
        sum(a.shop_amount) as shop_amount,
        sum(a.shop_amount_off) as shop_amount_off,
        sum(a.ship_fee) as sum_ship_fee,
        sum(a.ship_fee_off) as sum_ship_fee_off,
        avg(a.ship_fee - a.ship_fee_off) as avg_ship_fee
        from basedata_order as a %(seg_join_user)s
        where a.master_order_id is null and a.order_state not in (0, 98, 999)
        AND (a.agent_id <>7 or a.agent_id is NULL)
        %(condition2)s
        group by order_pay_date
        """
    cursor = connection.cursor()
    conditions1 = []
    conditions2 = []
    params = {}
    from_date = filter.get('from')
    to_date = filter.get('to')
    if from_date:
        conditions1.append(' and register_time >= %(from_date)s')
        conditions2.append(' and a.pay_date >= %(from_date)s')
        params['from_date'] = filter.get('from')
    if to_date:
        conditions1.append(' and register_time < %(to_date)s')
        conditions2.append(' and a.pay_date < %(to_date)s')
        params['to_date'] = filter.get('to')

    seg_user_summary = ''
    seg_join_user = ''
    is_supplier = not user.is_superuser and user.has_perm('basedata.as_supplier')
    if is_supplier:
        conditions2.append(' and a.supplier_id = %(supplier_id)s')
        suppliers = SupplierManager.objects.filter(user=user).values_list('supplier_id', flat=True)
        if len(suppliers) > 0:
            params['supplier_id'] = suppliers[0]  # 暂只支持一个用户属于一家供应商
        else:
            params['supplier_id'] = ''
    else:
        seg_user_summary = "b.user_cnt, count(order_no)/ b.user_cnt as order_rate,"
        seg_join_user = """
            left join (
                select DATE_FORMAT(register_time, '%%%%Y-%%%%m-%%%%d') as reg_day, count(uid) as user_cnt
                from profile_enduser
                where true %(condition1)s
                group by reg_day
                ) as b on b.reg_day = DATE_FORMAT(a.pay_date, '%%%%Y-%%%%m-%%%%d')
        """ % {"condition1": ''.join(conditions1)}

    sql = sql % {"condition2": ''.join(conditions2),
                 "seg_user_summary": seg_user_summary,
                 'seg_join_user': seg_join_user}
    header = (u'付款日期', u'订单数', '新用户数', '订单/用户比', u'订单总额（￥）', '维权单数', '维权总额（￥）',
              u'客单价（￥）', u'购物总额（￥）', u'商品优惠（￥）', u'邮费总额(￥)', u'邮费优惠(￥)',
              u'支付邮费/单(￥)')
    if is_supplier:
        header = (u'付款日期', u'订单数', u'订单总额（￥）', '维权单数', '维权总额（￥）', u'客单价（￥）',
                  u'购物总额（￥）', u'商品优惠（￥）', u'邮费总额(￥)', u'邮费优惠(￥)', u'支付邮费/单(￥)')
    data = []
    order_by = int(filter.get('orderBy', 1))
    order_by = order_by if 0 < order_by <= len(header) else 1
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    logger.debug(sql)
    cursor.execute(sql, params)
    for row in cursor.fetchall():
        row = list(row)
        if is_supplier:
            row[2] = row[2].quantize(Decimal('1.00'))
            row[4] = row[4].quantize(Decimal('1.00'))
            row[5] = row[5].quantize(Decimal('1.00'))
            row[10] = row[10].quantize(Decimal('1.00'))
        else:
            row[6] = row[6].quantize(Decimal('1.00'))
            row[4] = row[4].quantize(Decimal('1.00'))
            row[7] = row[7].quantize(Decimal('1.00'))
            row[12] = row[12].quantize(Decimal('1.00'))
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


order_daily_summary.name = '订单销售统计（每日）'
order_daily_summary.permission = 'report.view_order_daily_summary'


def order_monthly_summary(user=None, filter=None, supplier=None):
    """
    每月订单销售统计（按日期统计成交金额，单量等）
    :param request:
    :return:
    """
    sql = """
        select DATE_FORMAT(pay_date, '%%%%Y-%%%%m') as order_pay_month,
        count(order_no) as order_cnt, %(seg_user_summary)s
        sum(a.pay_amount+a.balance_payment+a.credits_expense/100) as pay_amount,
        avg(a.pay_amount) as avg_amount,
        sum(a.shop_amount) as shop_amount,
        sum(a.shop_amount_off) as shop_amount_off,
        sum(a.ship_fee) as sum_ship_fee,
        sum(a.ship_fee_off) as sum_ship_fee_off,
        avg(a.ship_fee - a.ship_fee_off) as avg_ship_fee
        from basedata_order as a %(seg_join_user)s
        where a.master_order_id is null
            and a.order_state not in (0, 98, 999)
            AND (a.agent_id <>7 or a.agent_id is NULL)
            %(condition2)s
        group by order_pay_month
        """
    cursor = connection.cursor()
    conditions1 = []
    conditions2 = []
    params = {}
    from_date = filter.get('from')
    to_date = filter.get('to')
    if from_date:
        conditions1.append(' and register_time >= %(from_date)s')
        conditions2.append(' and a.pay_date >= %(from_date)s')
        params['from_date'] = filter.get('from')
    if to_date:
        conditions1.append(' and register_time < %(to_date)s')
        conditions2.append(' and a.pay_date < %(to_date)s')
        params['to_date'] = filter.get('to')

    seg_user_summary = ''
    seg_join_user = ''
    is_supplier = not user.is_superuser and user.has_perm('basedata.as_supplier')
    if is_supplier:
        conditions2.append(' and a.supplier_id = %(supplier_id)s')
        suppliers = SupplierManager.objects.filter(user=user).values_list('supplier_id', flat=True)
        if len(suppliers) > 0:
            params['supplier_id'] = suppliers[0]  # 暂只支持一个用户属于一家供应商
        else:
            params['supplier_id'] = ''
    else:
        seg_user_summary = "b.user_cnt, count(order_no)/ b.user_cnt as order_rate,"
        seg_join_user = """
            left join (
                select DATE_FORMAT(register_time, '%%%%Y-%%%%m') as reg_month, count(uid) as user_cnt
                from profile_enduser
                where true %(condition1)s
                group by reg_month
                ) as b on b.reg_month = DATE_FORMAT(a.pay_date, '%%%%Y-%%%%m')
        """ % {"condition1": ''.join(conditions1)}

    sql = sql % {"condition2": ''.join(conditions2),
                 "seg_user_summary": seg_user_summary,
                 'seg_join_user': seg_join_user}
    header = (u'付款日期', u'订单数', '新用户数', '订单/用户比', u'订单总额（￥）', u'客单价（￥）',
              u'购物总额（￥）', u'商品优惠（￥）', u'邮费总额(￥)', u'邮费优惠(￥)', u'支付邮费/单(￥)')
    if is_supplier:
        header = (u'付款日期', u'订单数', u'订单总额（￥）', u'客单价（￥）',
                  u'购物总额（￥）', u'商品优惠（￥）', u'邮费总额(￥)', u'邮费优惠(￥)', u'支付邮费/单(￥)')
    data = []
    order_by = int(filter.get('orderBy', 1))
    order_by = order_by if 0 < order_by <= len(header) else 1
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    logger.debug(sql)
    cursor.execute(sql, params)
    for row in cursor.fetchall():
        row = list(row)
        if is_supplier:
            row[3] = row[3].quantize(Decimal('1.00'))
            row[4] = row[4].quantize(Decimal('1.00'))
            row[8] = row[8].quantize(Decimal('1.00'))
        else:
            row[4] = row[4].quantize(Decimal('1.00'))
            row[5] = row[5].quantize(Decimal('1.00'))
            row[10] = row[10].quantize(Decimal('1.00'))
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


order_monthly_summary.name = '订单销售统计（每月）'
order_monthly_summary.permission = 'report.view_order_monthly_summary'


def order_hourly_summary(user=None, filter=None, supplier=None):
    """
    每日订单销售统计（按时间统计成交金额，单量等）
    :param request:
    :return:
    """
    sql = """
        select hour(pay_date) as order_pay_hour,
        count(order_no) as order_cnt, b.user_cnt,
        count(order_no)/ b.user_cnt as order_rate,
        sum(a.pay_amount+a.balance_payment+a.credits_expense/100) as pay_amount,
        count(if(a.order_state in (4, 5, 96), a.order_no, null)) as refund_cnt,
        sum(if(a.order_state in (4, 5, 96), a.pay_amount+a.balance_payment+a.credits_expense/100, 0)) as may_refund,
        avg(a.pay_amount+a.balance_payment+a.credits_expense/100) as avg_amount,
        sum(a.shop_amount) as shop_amount,
        sum(a.shop_amount_off) as shop_amount_off,
        sum(a.ship_fee) as sum_ship_fee,
        sum(a.ship_fee_off) as sum_ship_fee_off,
        avg(a.ship_fee - a.ship_fee_off) as avg_ship_fee
        from basedata_order as a
        left join (
            select hour(register_time) as reg_hour, count(uid) as user_cnt
            from profile_enduser
            where true %s
            group by reg_hour
            ) as b on b.reg_hour = hour(a.pay_date)
        where a.master_order_id is null
            and a.order_state not in (0, 98, 999)
            AND (a.agent_id <>7 or a.agent_id is NULL)
            %s
        group by order_pay_hour
        """
    cursor = connection.cursor()
    conditions = []
    conditions2 = []
    params = []
    from_date = filter.get('from')
    to_date = filter.get('to')
    if from_date:
        conditions.append(' and register_time >= %s')
        conditions2.append(' and a.pay_date >= %s')
        params.append(filter.get('from'))
    if to_date:
        conditions.append(' and register_time < %s')
        conditions2.append(' and a.pay_date < %s')
        params.append(to_date)

    params *= 2
    sql = sql % (''.join(conditions), ''.join(conditions2))

    header = (u'付款时间', u'订单数', '新用户数', '订单/用户比', u'订单总额（￥）', '维权单数', '维权总额（￥）',
              u'客单价（￥）', u'购物总额（￥）', u'商品优惠（￥）', u'邮费总额(￥)', u'邮费优惠(￥)',
              u'支付邮费/单(￥)')
    data = []
    order_by = int(filter.get('orderBy', 1))
    order_by = order_by if 0 < order_by <= len(header) else 1
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    logger.debug(sql)
    cursor.execute(sql, params)
    for row in cursor.fetchall():
        row = list(row)
        row[6] = row[6].quantize(Decimal('1.00'))
        row[4] = row[4].quantize(Decimal('1.00'))
        row[7] = row[7].quantize(Decimal('1.00'))
        row[12] = row[12].quantize(Decimal('1.00'))
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


order_hourly_summary.name = '订单销售统计（分时）'
order_hourly_summary.permission = 'report.view_order_hourly_summary'


def account_book_summary(user=None, filter=None, supplier=None):
    """
    用户资金账户统计
    :param request:
    :return:
    """
    sql = """
        select b.real_name,
           if(b.nick_name is null, if(b.ex_nick_name is null, '', b.ex_nick_name), b.nick_name) as nick_name,
           sum(if(is_income=1, 1, 0)) as income_cnt,
           sum(if(is_income=1, figure, 0)) as income,
            sum(if(is_income=1, 0, 1)) as expense_cnt,
            sum(if(is_income=1, 0, -figure)) as expense,
            sum(if(is_income=1, figure, -figure)) as total,
            (select sum(amount) from profile_withdrawrequest
                where status=0 and uid=a.uid) as withdraw_tbd,
            (select sum(amount) from profile_withdrawrequest
                where status=1 and uid=a.uid) as withdraw_done,
            a.uid, b.mobile, b.id_card
            from profile_useraccountbook as a
             left join profile_enduser as b on a.uid = b.uid
            group by a.uid
    """
    cursor = connection.cursor()
    params = []
    # if filter.get('from'):
    #     sql += ' and pay_date >= %s'
    #     params.append(filter.get('from'))
    # if filter.get('to'):
    #     sql += ' and pay_date < %s'
    #     params.append(filter.get('to'))
    # if 'export' != filter.get('action'):
    #     limit = filter.get('size', 20)
    #     pos = filter.get('pos', 0)
    #     sql += ' limit %s offset %s;'
    #     params.extend([limit, pos])
    header = (u'姓名', u'昵称', u'收入（笔数）', u'收入金额（￥）', u'支出（笔数）', u'支出金额（￥）',
               u'账户余额（￥）', u'提现处理中（￥）', u'已提现（￥）', u'用户UID', u'手机', u'身份证号', )
    data = []
    order_by = int(filter.get('orderBy', 4))
    order_by = order_by if 0 < order_by <= len(header) else 4
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    logger.debug(sql)
    cursor.execute(sql, params)
    for row in cursor.fetchall():
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


account_book_summary.name = '用户资金账户统计'
account_book_summary.permission = 'report.view_account_book_summary'


def product_sales(user=None, filter=None, supplier=None):
    """
    商品销售统计
    :param request:
    :return:
    """
    sql = """
        select b.code, b.name, d.name as supplier, b.retail_price, b.retail_price-b.settle_price as margin,
        (b.retail_price-b.settle_price) * 100/b.retail_price as margin_ratio,
        sum(if(c.order_state in (1, 2, 3, 11, 12, 97, 13), a.pcs * a.deal_price, 0)) as sold_amount,
        sum(if(c.order_state in (4, 5, 96), a.pcs * a.deal_price, 0)) as cs_amount,
        sum(if(c.order_state in (1, 2, 3, 11, 12, 97, 13), a.pcs, 0)) as sold_pcs,
        count(distinct c.order_no) as total_order_cnt,
        count(distinct if(c.order_state in (1, 2, 3, 11, 12, 97, 13), c.order_no, null)) as order_cnt,
        # count(distinct if(c.order_state in (0, 98, 999), c.order_no, null)) as unpaid_order_cnt,
        count(distinct if(c.order_state in (4, 5, 96), c.order_no, null)) as cs_order_cnt
        from basedata_orderitem as a
        join basedata_product as b on a.product_id = b.code
        join basedata_order as c on a.order_id = c.order_no
        left join vendor_supplier as d on b.supplier_id = d.id
        where 1 = 1 %s
        group by b.code
        """
    cursor = connection.cursor()
    conditions = []
    params = []
    if filter.get('from'):
        conditions.append(' and c.pay_date >= %s')
        params.append(filter.get('from'))
    if filter.get('to'):
        conditions.append(' and c.pay_date < %s')
        params.append(filter.get('to'))
    if not user.is_superuser and user.has_perm('basedata.as_supplier'):
        conditions.append(' and b.supplier_id = %s')
        suppliers = SupplierManager.objects.filter(user=user).values_list('supplier_id', flat=True)
        if len(suppliers) > 0:
            params.append(suppliers[0])  # 暂只支持一个用户属于一家供应商
        else:
            params.append('')

    header = (u'商品编码', u'名称', u'供货商', '布丁零售价', '利润空间', '利润率%', u'成交总额（￥）',  '维权总额（￥）',
              u'销售数量', u'订单总笔数', u'订单成交笔数', u'维权订单笔数')
    data = []  # u'未支付订单笔数',

    order_by = int(filter.get('orderBy', 6))
    order_by = order_by if 0 < order_by <= len(header) else 6
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql = sql % ''.join(conditions)
    logger.debug(sql)
    cursor.execute(sql, params)
    for row in cursor.fetchall():
        row = list(row)
        row[5] = '%.1f' % (row[5] or 0)
        data.append(row)

    summary_sql = """
        select '-', '-', '-', '-', '-', '-',
        sum(if(c.order_state in (1, 2, 3, 11, 12, 97, 13), a.pcs * a.deal_price, 0)) as sold_amount,
        sum(if(c.order_state in (4, 5, 96), a.pcs * a.deal_price, 0)) as cs_amount,
        sum(if(c.order_state in (1, 2, 3, 11, 12, 97, 13), a.pcs, 0)) as sold_pcs,
        count(distinct c.order_no) as total_order_cnt,
        count(distinct if(c.order_state in (1, 2, 3, 11, 12, 97, 13), c.order_no, null)) as order_cnt,
        # count(distinct if(c.order_state in (0, 98, 999), c.order_no, null)) as unpaid_order_cnt,
        count(distinct if(c.order_state in (4, 5, 96), c.order_no, null)) as cs_order_cnt
        from basedata_orderitem as a
        join basedata_product as b on a.product_id = b.code
        join basedata_order as c on a.order_id = c.order_no
        left join vendor_supplier as d on b.supplier_id = d.id
        where 1 = 1
        AND (c.agent_id <>7 or c.agent_id is NULL)
        %s
        """
    summary_sql = summary_sql % ''.join(conditions)
    cursor.execute(summary_sql, params)
    summary_row = cursor.fetchone()

    return {"data": data,
            "header": header,
            "summary": summary_row,
            "orderBy": order_by,
            "isAsc": is_asc}


product_sales.name = '商品销售统计（按商品）'
product_sales.permission = 'report.view_product_sales'


def product_sales_by_supplier(user=None, filter=None, supplier=None):
    """
    商品销售统计-按供应商
    :param request:
    :return:
    """
    sql = """
        select d.name as supplier,
        (select concat(count(if(x.`status` = 1, code, null)), '/', count(code))
            from basedata_product as x where x.supplier_id = d.id) as product_cnt,
        sum(if(c.order_state in (1, 2, 3, 11, 12, 97, 13), a.pcs * a.deal_price, 0)) as sold_amount,
        sum(if(c.order_state in (1, 2, 3, 11, 12, 97, 13), a.pcs * b.cost, 0)) as sold_cost,
        sum(if(c.order_state in (1, 2, 3, 11, 12, 97, 13), c.ship_fee, 0)) as ship_fee_cost,
        sum(if(c.order_state in (1, 2, 3, 11, 12, 97, 13), a.pcs, 0)) as sold_pcs,
        count(distinct c.order_no) as total_order_cnt,
        count(distinct if(c.order_state in (1, 2, 3, 11, 12, 97, 13), c.order_no, null)) as order_cnt,
        count(distinct if(c.order_state in (0, 98, 999), c.order_no, null)) as unpaid_order_cnt,
        count(distinct if(c.order_state in (4, 5, 96), c.order_no, null)) as cs_order_cnt
        from basedata_orderitem as a
        join basedata_product as b on a.product_id = b.code
        join basedata_order as c on a.order_id = c.order_no
        left join vendor_supplier as d on d.id = c.supplier_id
        where 1 = 1
        AND (c.agent_id <>7 or c.agent_id is NULL)
        %s
        group by d.id
        """
    cursor = connection.cursor()
    conditions = []
    params = []
    if filter.get('from'):
        conditions.append(' and c.pay_date >= %s')
        params.append(filter.get('from'))
    if filter.get('to'):
        conditions.append(' and c.pay_date < %s')
        params.append(filter.get('to'))

    header = (u'供货商', u'商品数（上架/总数）', u'销售总额（￥）', u'供货价（￥）', u'运费总额（￥）', u'销售数量',
              u'订单总笔数', u'订单成交笔数', u'未支付订单笔数', u'维权订单笔数')
    data = []
    order_by = int(filter.get('orderBy', 4))
    order_by = order_by if 0 < order_by <= len(header) else 4
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql = sql % ''.join(conditions)
    logger.debug(sql)
    cursor.execute(sql, params)
    for row in cursor.fetchall():
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


product_sales_by_supplier.name = '商品销售统计（按供应商）'
product_sales_by_supplier.permission = 'report.view_product_sales_by_supplier'


def product_sales_by_agent(user=None, filter=None, supplier=None):
    """
    商品销售统计-按销售渠道
    :param request:
    :return:
    """
    sql = """
        select b.code, b.name, if(d.name is null, '布丁', d.name) as agent,
        sum(if(c.order_state in (1, 2, 3, 11, 12, 97, 13), a.pcs * a.deal_price, 0)) as sold_amount,
        sum(if(c.order_state in (4, 5, 96), a.pcs * a.deal_price, 0)) as cs_amount,
        sum(if(c.order_state in (1, 2, 3, 11, 12, 97, 13), a.pcs * b.cost, 0)) as sold_cost,
        sum(if(c.order_state in (1, 2, 3, 11, 12, 97, 13), c.ship_fee, 0)) as ship_fee_cost,
        count(distinct a.product_id) as product_cnt,
        sum(if(c.order_state in (1, 2, 3, 11, 12, 97, 13), a.pcs, 0)) as sold_pcs,
        count(distinct c.order_no) as total_order_cnt,
        count(distinct if(c.order_state in (1, 2, 3, 11, 12, 97, 13), c.order_no, null)) as order_cnt,
        count(distinct if(c.order_state in (0, 98, 999), c.order_no, null)) as unpaid_order_cnt,
        count(distinct if(c.order_state in (4, 5, 96), c.order_no, null)) as cs_order_cnt
        from basedata_orderitem as a
        join basedata_product as b on b.code = a.product_id
        join basedata_order as c on a.order_id = c.order_no
        left join vendor_salesagent as d on d.id = c.agent_id
        where 1 = 1 %s
        group by b.code, d.id
        """
    cursor = connection.cursor()
    conditions = []
    params = []
    if filter.get('from'):
        conditions.append(' and c.pay_date >= %s')
        params.append(filter.get('from'))
    if filter.get('to'):
        conditions.append(' and c.pay_date < %s')
        params.append(filter.get('to'))

    header = ('商品编码', '商品名称', u'销售渠道', u'成交总额（￥）', '维权总额（￥）',
              u'供货价（￥）', u'运费总额（￥）', u'成交商品种数',
              u'销售数量', u'订单总笔数', u'订单成交笔数', u'未支付订单笔数', u'维权订单笔数')
    data = []
    order_by = int(filter.get('orderBy', 4))
    order_by = order_by if 0 < order_by <= len(header) else 4
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql = sql % ''.join(conditions)
    logger.debug(sql)
    cursor.execute(sql, params)
    for row in cursor.fetchall():
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


product_sales_by_agent.name = '商品销售统计（按渠道）'
product_sales_by_agent.permission = 'report.view_product_sales_by_agent'


def user_daily_summary(user=None, filter=None, supplier=None):
    """
    每日注册数统计
    :param request:
    :return:
    """
    # 由于python字符串格式化的问题，sql中'%Y-%m-%d'要写为'%%%%Y-%%%%m-%%%%d'
    sql = """
        select DATE_FORMAT(register_time, '%%%%Y-%%%%m-%%%%d') as reg_day, count(uid) as user_cnt,
            sum(if(referrer is null, 0, 1)) as referred_cnt
            from profile_enduser
            where 1=1 %s
            group by reg_day
        """
    cursor = connection.cursor()
    conditions = []
    params = []
    if filter.get('from'):
        conditions.append(' and register_time >= %s')
        params.append(filter.get('from'))
    if filter.get('to'):
        conditions.append(' and register_time < %s')
        params.append(filter.get('to'))

    header = (u'日期', u'新独立用户数', u'新推荐导游数', )
    data = []
    order_by = int(filter.get('orderBy', 1))
    order_by = order_by if 0 < order_by <= len(header) else 1
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql = sql % ''.join(conditions)
    logger.debug(sql)
    # if len(params) > 0:
    cursor.execute(sql, params)
    # else:
    #     cursor.execute(sql)
    for row in cursor.fetchall():
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


user_daily_summary.name = '用户注册统计（每日）'
user_daily_summary.permission = 'report.view_user_daily_summary'


def user_reorder_differ_day(user=None, filter=None, supplier=None):
    """
    用户非同日二次下单统计
    :param request:
    :return:
    """
    # 由于python字符串格式化的问题，sql中'%Y-%m-%d'要写为'%%%%Y-%%%%m-%%%%d'
    sql = """
        select a.buyer_id,
            concat(if(b.nick_name is null, if(b.ex_nick_name is null, '', b.ex_nick_name), b.nick_name), '/', if(b.real_name is null, '', b.real_name)) as name,
            count(a.order_no) as cnt, sum(a.pay_amount+a.balance_payment+a.credits_expense/100) as order_amount,
            sum(if(a.order_state in (0, 98, 999), 0, a.pay_amount+a.balance_payment+a.credits_expense/100)) as real_pay,
            sum(if(a.order_state in (0, 98, 999), a.pay_amount+a.balance_payment+a.credits_expense/100, 0)) as not_pay,
            sum(if(a.order_state in (4, 5, 96), a.pay_amount+a.balance_payment+a.credits_expense/100, 0)) as may_refund,
        min(a.pay_date) as min_pay_date, max(a.pay_date) as max_pay_date
        from basedata_order as a
        join profile_enduser as b on a.buyer_id = b.uid
        where TRUE %s
        group by a.buyer_id
        having cnt > 1 and datediff(max(a.pay_date), min(a.pay_date)) > 0
        """
    cursor = connection.cursor()
    conditions = []
    params = []
    if filter.get('from'):
        conditions.append(' and a.pay_date >= %s')
        params.append(filter.get('from'))
    if filter.get('to'):
        conditions.append(' and a.pay_date < %s')
        params.append(filter.get('to'))

    header = (u'用户uid', '姓名/昵称', '订单总数', '订单总额', '实付总额', '未付总额', '退款总额',
              '首次付款时间', '最近付款时间' )
    data = []
    order_by = int(filter.get('orderBy', 3))
    order_by = order_by if 0 < order_by <= len(header) else 3
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql = sql % ''.join(conditions)
    logger.debug(sql)
    # if len(params) > 0:
    cursor.execute(sql, params)
    # else:
    #     cursor.execute(sql)
    for row in cursor.fetchall():
        row = list(row)
        row[3] = row[3].quantize(Decimal('1.00'))
        row[4] = row[4].quantize(Decimal('1.00'))
        row[5] = row[5].quantize(Decimal('1.00'))
        row[6] = row[6].quantize(Decimal('1.00'))
        data.append(list(row))

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


user_reorder_differ_day.name = '用户非同日二次下单统计'
user_reorder_differ_day.permission = 'report.user_reorder_differ_day'


def user_reward_report(user=None, filter=None, supplier=None):
    """
    用户收益统计
    :param request:
    :return:
    """
    # 由于python字符串格式化的问题，sql中'%Y-%m-%d'要写为'%%%%Y-%%%%m-%%%%d'
    sql = """
        SELECT `b`.`real_name` AS `real_name`,
        if(b.nick_name is null, if(b.ex_nick_name is null, '', b.ex_nick_name), b.nick_name) as nick_name,
        (select count(order_no) from basedata_order as bo
          where bo.referrer_id = a.referrer_id
          and bo.order_state not in (0, 4, 5, 96, 98, 999) %(order_con)s) as direct_order_cnt,
        (select sum(pay_amount+balance_payment+credits_expense/100) from basedata_order as bo
          where bo.referrer_id = a.referrer_id
          and bo.order_state not in (0, 4, 5, 96, 98, 999) %(order_con)s) as direct_order_amount,
        (select count(order_no) from basedata_order as bo
          where bo.referrer_id = a.referrer_id
          and bo.order_state in (4, 5, 96) %(order_con)s) as cs_direct_order_cnt,
        (select sum(pay_amount+balance_payment+credits_expense/100) from basedata_order as bo
          where bo.referrer_id = a.referrer_id
          and bo.order_state in (4, 5, 96) %(order_con)s) as cs_direct_order_amount,
        count(distinct c.order_no) as order_cnt,
        SUM(IF((`a`.`status` <> 2),c.pay_amount+c.balance_payment+c.credits_expense/100,0)) AS `order_amount`,
        count(distinct if(c.order_state in (4, 5, 96), a.order_no, null)) as 'cs_order_cnt',
        COUNT(a.id) AS `reward_cnt`,
        SUM(IF((`a`.`status` <> 2),`a`.`reward`,0)) AS `total_reward`,
        SUM(IF((`a`.`status` = 0),`a`.`reward`,0)) AS `not_settled_reward`,
        SUM(IF((`a`.`status` = 1),`a`.`achieved`,0)) AS `settled_reward`,
        SUM(IF((`a`.`status` = 2),`a`.`reward`,0)) AS `revoked_reward`,
        `a`.`referrer_id` AS `uid`, `b`.`mobile` AS `mobile`
        FROM `promote_rewardrecord` `a`
        JOIN `profile_enduser` `b` ON((`a`.`referrer_id` = `b`.`uid`))
        join basedata_order as c on a.order_no = c.order_no
        where 1=1 %(reward_con)s
        GROUP BY `a`.`referrer_id`
        """
    cursor = connection.cursor()
    conditions = {'order_con': '', 'reward_con': ''}
    params = {}
    if filter.get('from'):
        conditions['order_con'] += ' and bo.pay_date >= %(from_date)s'
        conditions['reward_con'] += ' and a.create_time >= %(from_date)s'
        params['from_date'] = filter.get('from')
    if filter.get('to'):
        conditions['order_con'] += ' and bo.pay_date < %(to_date)s'
        conditions['reward_con'] += ' and a.create_time < %(to_date)s'
        params['to_date'] = filter.get('to')

    header = (u'姓名', u'昵称', '直接促成订单数（不含维权）', '直接促成订单总额（不含维权）',
              '直接促成订单数（仅维权）', '直接促成订单总额（仅维权）',
              u'收益订单成交数', u'收益订单成交总额（￥）', u'维权单数', u'收益笔数', u'总收益（￥）',
              u'未结算收益（￥）', u'已结算收益（￥）', u'已撤销收益（￥）', u'用户UID', u'手机号')
    data = []
    order_by = int(filter.get('orderBy', 8))
    order_by = order_by if 0 < order_by <= len(header) else 8
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql = sql % conditions
    # if len(params) > 0:
    logger.debug(sql)
    cursor.execute(sql, params)
    # else:
    #     cursor.execute(sql)
    for row in cursor.fetchall():
        row = list(row)
        if row[3]:
            row[3] = row[3].quantize(Decimal('1.00'))
        if row[5]:
            row[5] = row[5].quantize(Decimal('1.00'))
        if row[7]:
            row[7] = row[7].quantize(Decimal('1.00'))
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


user_reward_report.name = '用户收益统计'
user_reward_report.permission = 'report.view_user_reward_summary'


def user_reward_report_local(user=None, filter=None, supplier=None):
    """
    用户收益统计(本地配送)
    :param request:
    :return:
    """
    # 由于python字符串格式化的问题，sql中'%Y-%m-%d'要写为'%%%%Y-%%%%m-%%%%d'
    sql = """
        SELECT `b`.`real_name` AS `real_name`,
        if(b.nick_name is null, if(b.ex_nick_name is null, '', b.ex_nick_name), b.nick_name) as nick_name,
        (select count(order_no) from basedata_order as bo
          where bo.referrer_id = a.referrer_id
          and bo.order_state not in (0, 4, 5, 96, 98, 999) %(order_con)s) as direct_order_cnt,
        (select sum(pay_amount+balance_payment+credits_expense/100) from basedata_order as bo
          where bo.referrer_id = a.referrer_id
          and bo.order_state not in (0, 4, 5, 96, 98, 999) %(order_con)s) as direct_order_amount,
        (select count(order_no) from basedata_order as bo
          where bo.referrer_id = a.referrer_id
          and bo.order_state in (4, 5, 96) %(order_con)s) as cs_direct_order_cnt,
        (select sum(pay_amount+balance_payment+credits_expense/100) from basedata_order as bo
          where bo.referrer_id = a.referrer_id
          and bo.order_state in (4, 5, 96) %(order_con)s) as cs_direct_order_amount,
        count(distinct c.order_no) as order_cnt,
        SUM(IF((`a`.`status` <> 2),c.pay_amount+c.balance_payment+c.credits_expense/100,0)) AS `order_amount`,
        count(distinct if(c.order_state in (4, 5, 96), a.order_no, null)) as 'cs_order_cnt',
        COUNT(a.id) AS `reward_cnt`,
        SUM(IF((`a`.`status` <> 2),`a`.`reward`,0)) AS `total_reward`,
        SUM(IF((`a`.`status` = 0),`a`.`reward`,0)) AS `not_settled_reward`,
        SUM(IF((`a`.`status` = 1),`a`.`achieved`,0)) AS `settled_reward`,
        SUM(IF((`a`.`status` = 2),`a`.`reward`,0)) AS `revoked_reward`,
        `a`.`referrer_id` AS `uid`, `b`.`mobile` AS `mobile`
        FROM `promote_rewardrecord` `a`
        JOIN `profile_enduser` `b` ON((`a`.`referrer_id` = `b`.`uid`))
        join basedata_order as c on a.order_no = c.order_no
        where 1=1 %(reward_con)s
        GROUP BY `a`.`referrer_id`
        """
    cursor = connection.cursor()
    conditions = {'order_con': '', 'reward_con': ''}
    params = {}
    conditions['order_con'] += ' and bo.ship_type = "local"'
    if filter.get('from'):
        conditions['order_con'] += ' and bo.pay_date >= %(from_date)s'
        conditions['reward_con'] += ' and a.create_time >= %(from_date)s'
        params['from_date'] = filter.get('from')
    if filter.get('to'):
        conditions['order_con'] += ' and bo.pay_date < %(to_date)s'
        conditions['reward_con'] += ' and a.create_time < %(to_date)s'
        params['to_date'] = filter.get('to')

    header = (u'姓名', u'昵称', '直接促成订单数（不含维权）', '直接促成订单总额（不含维权）',
              '直接促成订单数（仅维权）', '直接促成订单总额（仅维权）',
              u'收益订单成交数', u'收益订单成交总额（￥）', u'维权单数', u'收益笔数', u'总收益（￥）',
              u'未结算收益（￥）', u'已结算收益（￥）', u'已撤销收益（￥）', u'用户UID', u'手机号')
    data = []
    order_by = int(filter.get('orderBy', 8))
    order_by = order_by if 0 < order_by <= len(header) else 8
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql = sql % conditions
    # if len(params) > 0:
    logger.debug(sql)
    cursor.execute(sql, params)
    # else:
    #     cursor.execute(sql)
    for row in cursor.fetchall():
        row = list(row)
        if row[3]:
            row[3] = row[3].quantize(Decimal('1.00'))
        if row[5]:
            row[5] = row[5].quantize(Decimal('1.00'))
        if row[7]:
            row[7] = row[7].quantize(Decimal('1.00'))
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


user_reward_report_local.name = '用户收益统计（本地配送）'
user_reward_report_local.permission = 'report.view_user_reward_summary_local'


def user_reward_report_express(user=None, filter=None, supplier=None):
    """
    用户收益统计(非本地配送)
    :param request:
    :return:
    """
    # 由于python字符串格式化的问题，sql中'%Y-%m-%d'要写为'%%%%Y-%%%%m-%%%%d'
    sql = """
        SELECT `b`.`real_name` AS `real_name`,
        if(b.nick_name is null, if(b.ex_nick_name is null, '', b.ex_nick_name), b.nick_name) as nick_name,
        (select count(order_no) from basedata_order as bo
          where bo.referrer_id = a.referrer_id
          and bo.order_state not in (0, 4, 5, 96, 98, 999) %(order_con)s) as direct_order_cnt,
        (select sum(pay_amount+balance_payment+credits_expense/100) from basedata_order as bo
          where bo.referrer_id = a.referrer_id
          and bo.order_state not in (0, 4, 5, 96, 98, 999) %(order_con)s) as direct_order_amount,
        (select count(order_no) from basedata_order as bo
          where bo.referrer_id = a.referrer_id
          and bo.order_state in (4, 5, 96) %(order_con)s) as cs_direct_order_cnt,
        (select sum(pay_amount+balance_payment+credits_expense/100) from basedata_order as bo
          where bo.referrer_id = a.referrer_id
          and bo.order_state in (4, 5, 96) %(order_con)s) as cs_direct_order_amount,
        count(distinct c.order_no) as order_cnt,
        SUM(IF((`a`.`status` <> 2),c.pay_amount+c.balance_payment+c.credits_expense/100,0)) AS `order_amount`,
        count(distinct if(c.order_state in (4, 5, 96), a.order_no, null)) as 'cs_order_cnt',
        COUNT(a.id) AS `reward_cnt`,
        SUM(IF((`a`.`status` <> 2),`a`.`reward`,0)) AS `total_reward`,
        SUM(IF((`a`.`status` = 0),`a`.`reward`,0)) AS `not_settled_reward`,
        SUM(IF((`a`.`status` = 1),`a`.`achieved`,0)) AS `settled_reward`,
        SUM(IF((`a`.`status` = 2),`a`.`reward`,0)) AS `revoked_reward`,
        `a`.`referrer_id` AS `uid`, `b`.`mobile` AS `mobile`
        FROM `promote_rewardrecord` `a`
        JOIN `profile_enduser` `b` ON((`a`.`referrer_id` = `b`.`uid`))
        join basedata_order as c on a.order_no = c.order_no
        where 1=1 %(reward_con)s
        GROUP BY `a`.`referrer_id`
        """
    cursor = connection.cursor()
    conditions = {'order_con': '', 'reward_con': ''}
    params = {}
    conditions['order_con'] += ' and bo.ship_type <> "local"'
    if filter.get('from'):
        conditions['order_con'] += ' and bo.pay_date >= %(from_date)s'
        conditions['reward_con'] += ' and a.create_time >= %(from_date)s'
        params['from_date'] = filter.get('from')
    if filter.get('to'):
        conditions['order_con'] += ' and bo.pay_date < %(to_date)s'
        conditions['reward_con'] += ' and a.create_time < %(to_date)s'
        params['to_date'] = filter.get('to')

    header = (u'姓名', u'昵称', '直接促成订单数（不含维权）', '直接促成订单总额（不含维权）',
              '直接促成订单数（仅维权）', '直接促成订单总额（仅维权）',
              u'收益订单成交数', u'收益订单成交总额（￥）', u'维权单数', u'收益笔数', u'总收益（￥）',
              u'未结算收益（￥）', u'已结算收益（￥）', u'已撤销收益（￥）', u'用户UID', u'手机号')
    data = []
    order_by = int(filter.get('orderBy', 8))
    order_by = order_by if 0 < order_by <= len(header) else 8
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql = sql % conditions
    # if len(params) > 0:
    logger.debug(sql)
    cursor.execute(sql, params)
    # else:
    #     cursor.execute(sql)
    for row in cursor.fetchall():
        row = list(row)
        if row[3]:
            row[3] = row[3].quantize(Decimal('1.00'))
        if row[5]:
            row[5] = row[5].quantize(Decimal('1.00'))
        if row[7]:
            row[7] = row[7].quantize(Decimal('1.00'))
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


user_reward_report_express.name = '用户收益统计（非本地配送）'
user_reward_report_express.permission = 'report.view_user_reward_summary_express'


def user_cumulated_referrer_summary(user=None, filter=None, supplier=None):
    """
    用户累计推广统计
    :param request:
    :return:
    """
    # 由于python字符串格式化的问题，sql中'%Y-%m-%d'要写为'%%%%Y-%%%%m-%%%%d'
    sql = """
        select concat(if(b.nick_name is null, if(b.ex_nick_name is null, '', b.ex_nick_name), b.nick_name), '/', if(b.real_name is null, '', b.real_name)) as name,
        a.user_cnt, a.order_cnt, a.order_amount,
        d.user_cnt as referree_user_cnt, d.referree_cnt, d.referree_amount,
        b.mobile, b.uid
        from profile_enduser as b
        left join (select a.referrer_id, count(DISTINCT a.buyer_id) as user_cnt, count(a.order_no) as order_cnt,
                sum(a.pay_amount+a.balance_payment+a.credits_expense/100) as order_amount
            from  basedata_order as a group by a.referrer_id) as a on a.referrer_id = b.uid
        join (select b.uid, count(distinct e.uid) as user_cnt, count(a.order_no) as referree_cnt,
            sum(a.pay_amount+a.balance_payment+a.credits_expense/100) as referree_amount
            from profile_enduser as b
            join profile_enduser as e on b.uid = e.referrer
            left join basedata_order as a on a.referrer_id = e.uid
            group by b.uid) as d on b.uid = d.uid
        where exists (select c.uid from profile_enduser as c where c.referrer = b.uid)
        """
    cursor = connection.cursor()
    conditions = []
    params = []
    # if filter.get('from'):
    #     conditions.append(' and b.register_time >= %s')
    #     params.append(filter.get('from'))
    # if filter.get('to'):
    #     conditions.append(' and b.register_time < %s')
    #     params.append(filter.get('to'))

    header = (u'昵称/姓名', '促成买家数', u'推广人促成用户订单成交数', '推广人促成用户订单成交额（￥)',
              '推广导游数', u'被推导游促成用户订单成交数', u'被推导游促成用户订单成交总额（￥）',
              u'推广人手机号', u'推广人UID')
    data = []
    order_by = int(filter.get('orderBy', 4))
    order_by = order_by if 0 < order_by <= len(header) else 4
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    # sql = sql % ''.join(conditions)
    # if len(params) > 0:
    logger.debug(sql)
    cursor.execute(sql, params)
    # else:
    #     cursor.execute(sql)
    for row in cursor.fetchall():
        row = list(row)
        if row[3]:
            row[3] = row[3].quantize(Decimal('1.00'))
        if row[6]:
            row[6] = row[6].quantize(Decimal('1.00'))
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


user_cumulated_referrer_summary.name = '用户累计推广统计'
user_cumulated_referrer_summary.permission = 'report.view_user_cumulated_referrer_summary'


def user_referrer_summary(user=None, filter=None, supplier=None):
    """
    用户推广统计
    :param request:
    :return:
    """
    # 由于python字符串格式化的问题，sql中'%Y-%m-%d'要写为'%%%%Y-%%%%m-%%%%d'
    sql = """
        select concat(if(b.nick_name is null, if(b.ex_nick_name is null, '', b.ex_nick_name), b.nick_name), '/', if(b.real_name is null, '', b.real_name)) as name,
            count(a.uid) as referree_cnt,
            b.mobile, b.uid
        from profile_enduser as b
        join profile_enduser as a on b.uid = a.referrer
        where TRUE %s
        group by b.uid
        having referree_cnt > 0
        """
    cursor = connection.cursor()
    conditions = []
    params = []
    if filter.get('from'):
        conditions.append(' and a.register_time >= %s')
        params.append(filter.get('from'))
    if filter.get('to'):
        conditions.append(' and a.register_time < %s')
        params.append(filter.get('to'))

    header = (u'昵称/姓名', '推广导游数', u'推广人手机号', u'推广人UID')
    data = []
    order_by = int(filter.get('orderBy', 2))
    order_by = order_by if 0 < order_by <= len(header) else 2
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql = sql % ''.join(conditions)
    # if len(params) > 0:
    logger.debug(sql)
    cursor.execute(sql, params)
    # else:
    #     cursor.execute(sql)
    for row in cursor.fetchall():
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


user_referrer_summary.name = '用户推广统计'
user_referrer_summary.permission = 'report.view_user_referrer_summary'


def user_cascade_reward(user=None, filter=None, supplier=None):
    """
    伙伴推广收益统计
    :param request:
    :return:
    """
    # 由于python字符串格式化的问题，sql中'%Y-%m-%d'要写为'%%%%Y-%%%%m-%%%%d'
    sql = """
        select c.real_name, if(c.nick_name is null, if(c.ex_nick_name is null, '', c.ex_nick_name), c.nick_name) as nick_name,
        sum(if(a.status=1, a.achieved, 0)) as achieved_reward_amount,
        sum(if(a.status=1, 0, a.reward)) as unachieved_reward_amount,
        (select count(*)
            from basedata_order where referrer_id=c.uid
            and order_state not in (0, 4, 5, 96, 98, 999) %s
            ) as order_cnt,
        count(if(b.order_state=3, b.order_no, null)) as signoff_cnt,
        sum(if(b.order_state=3, b.pay_amount+b.balance_payment+b.credits_expense/100, 0)) as signoff_order_amount,
        count(if(b.order_state=3, null, b.order_no)) as unsignoff_cnt,
        sum(if(b.order_state=3, 0, b.pay_amount+b.balance_payment+b.credits_expense/100)) as unsignoff_order_amount,
        c.mobile, c.uid
        from promote_rewardrecord as a
        join basedata_order as b on a.order_no = b.order_no
        join profile_enduser as c on a.referrer_id = c.uid
        where reward_type=1 %s
        group by c.uid
        """
    cursor = connection.cursor()
    conditions1 = []
    conditions = []
    params1 = []
    params = []
    if filter.get('from'):
        conditions1.append(' and pay_date >= %s')
        conditions.append(' and b.signoff_date >= %s')
        params1.append(filter.get('from'))
        params.append(filter.get('from'))
    if filter.get('to'):
        conditions1.append(' and pay_date < %s')
        conditions.append(' and b.signoff_date < %s')
        params1.append(filter.get('to'))
        params.append(filter.get('to'))

    header = (u'姓名', u'昵称', u'已结算奖励总额（￥）', u'未结算奖励总额（￥）', u'个人推广订单成交数',
              u'已签收订单成交数', u'已签收成交总额（￥）', u'未签收订单成交数', u'未签收成交总额（￥）',
              u'手机号', u'UID', )
    data = []
    order_by = int(filter.get('orderBy', 3))
    order_by = order_by if 0 < order_by <= len(header) else 3
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql = sql % (''.join(conditions1), ''.join(conditions))
    # if len(params) > 0:
    logger.debug(sql)
    params1.extend(params)
    cursor.execute(sql, params1)

    # else:
    #     cursor.execute(sql)
    for row in cursor.fetchall():
        row = list(row)
        row[6] = row[6].quantize(Decimal('1.00'))
        row[8] = row[8].quantize(Decimal('1.00'))
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


user_cascade_reward.name = '伙伴推广收益统计'
user_cascade_reward.permission = 'report.view_user_cascade_reward'


def operational_report(user=None, filter=None, supplier=None):
    sql = ''


def finance_margin_detail(user=None, filter=None, supplier=None):
    """
    销售利润表
    :param request:
    :return:
    """
    # 由于python字符串格式化的问题，sql中'%Y-%m-%d'要写为'%%%%Y-%%%%m-%%%%d'
    sql = """
        select a.pay_date, a.order_no, a.order_state, b.name, a.buyer,
            (select name from vendor_salesagent where id=a.agent_id) as n,
            (select group_concat(concat('[', x.product_id, ']', y.name, '(￥', x.deal_price ,')', '*', x.pcs) separator ';<br>')
                from basedata_orderitem as x
                join basedata_product as y
                on x.product_id = y.code
                where x.order_id=a.order_no) as brief,
            a.pay_amount, a.balance_payment, a.credits_expense/100,
            (select sum(oi.cost*oi.pcs) from basedata_orderitem as oi
                where oi.order_id=a.order_no) as cost,
            (a.ship_fee - a.ship_fee_off) as ship_fee, 0 as commission,
            if(a.shop_amount_off > 0, a.shop_amount_off, '') as other,
            # 0 as gross_profit, (a.pay_amount - cost - ship_fee - other - reward)
            (select sum(reward) from promote_rewardrecord as pr where pr.order_no=a.order_no and pr.status<>2) as reward,
            if(a.refunded_fee, concat("退款: ", a.refunded_fee), '') as memo
        from basedata_order as a
         left join vendor_supplier as b on a.supplier_id = b.id
        where a.order_state not in (0, 98, 999)
        AND (a.agent_id <>7 or a.agent_id is NULL)
        %s
        """
    # if (a.shop_amount_off > 0, concat("优惠：", a.shop_amount_off), '') as other,

    cursor = connection.cursor()
    conditions = []
    params = []
    if filter.get('from'):
        conditions.append(' and pay_date >= %s')
        params.append(filter.get('from'))
    if filter.get('to'):
        conditions.append(' and pay_date < %s')
        params.append(filter.get('to'))

    header = ('日期(支付时间)', '订单号', '订单状态', '供应商', '客户名称', '销售渠道', '商品名称', '销售金额（￥，含税）',
              '余额支付', '积分扣抵',
              '供货价（￥，含税）', '运费/快递费（￥）', '手续费（￥）', '其他优惠（￥）', '导游提成（￥）', '备注',)
    data = []  # '毛利率',
    order_by = int(filter.get('orderBy', 1))
    order_by = order_by if 0 < order_by <= len(header) else 1
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql = sql % ''.join(conditions)
    logger.debug(sql)
    cursor.execute(sql, params)
    state_dict = dict(Order.ORDER_STATES)
    for row in cursor.fetchall():
        row = list(row)
        if not row[5]:
            row[5] = u'布丁'
        row[9] = row[9].quantize(Decimal('1.00'))
        row[2] = state_dict.get(row[2], u'未知')
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


finance_margin_detail.name = '销售利润表'
finance_margin_detail.permission = 'report.view_finance_margin_detail'


def finance_sale_report(user=None, filter=None, supplier=None):
    """
    订单销售报表（按日期统计成交金额，单量等）
    :param request:
    :return:
    """
    # 由于python字符串格式化的问题，sql中'%Y-%m-%d'要写为'%%%%Y-%%%%m-%%%%d'
    sql = """
        select a.pay_date, a.order_no, a.order_state, a.buyer,
            (select group_concat(concat('[', x.product_id, ']', y.name, '(￥', x.deal_price ,')', '*', x.pcs) separator ';<br>')
                from basedata_orderitem as x
                join basedata_product as y
                on x.product_id = y.code
                where x.order_id=a.order_no) as brief,
            a.pay_amount,
            (a.ship_fee - a.ship_fee_off) as ship_fee,
            if(a.shop_amount_off > 0, concat("优惠：", a.shop_amount_off), '') as other,
            if(a.refunded_fee > 0, concat("退款: ", a.refunded_fee), '') as memo
        from basedata_order as a
        where a.order_state not in (0, 98, 999)
        AND (a.agent_id <>7 or a.agent_id is NULL)
        %s
        """

    cursor = connection.cursor()
    conditions = []
    params = []
    if filter.get('from'):
        conditions.append(' and pay_date >= %s')
        params.append(filter.get('from'))
    if filter.get('to'):
        conditions.append(' and pay_date < %s')
        params.append(filter.get('to'))

    header = ('日期(支付时间)', '订单号', '订单状态', '客户名称', '商品名称', '销售金额（￥，含税）',  '运费/快递费（￥）',
             '其他费用（￥）', '备注',)
    data = []
    order_by = int(filter.get('orderBy', 1))
    order_by = order_by if 0 < order_by <= len(header) else 1
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql = sql % ''.join(conditions)
    logger.debug(sql)
    cursor.execute(sql, params)
    state_dict = dict(Order.ORDER_STATES)
    for row in cursor.fetchall():
        row = list(row)
        row[2] = state_dict.get(row[2], u'未知')
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


finance_sale_report.name = '订单销售报表'
finance_sale_report.permission = 'report.view_finance_sale_report'


def finance_purchase_report(user=None, filter=None, supplier=None):
    return [('暂无采购记录',)]


finance_purchase_report.name = '采购报表'
finance_purchase_report.permission = 'report.view_finance_purchase_report'


def finance_supplier_detail(user=None, filter=None, supplier=None):
    sql = """
        select a.code, a.name, c.ca_type, c.ca_name, c.ca_no,
            concat(c.bank_name, c.open_bank) as open_bank, b.name,
            if(b.mobile, b.mobile, b.phone) as phone, a.address
        from vendor_supplier as a
        left join vendor_contact as b on a.primary_contact_id = b.id
        left join profile_usercapitalaccount as c on c.id = concat("SUP-", lpad(a.id, 12, 0))
        """
    cursor = connection.cursor()
    header = ('编码', '名称', '账户类别', '开户名', '账号', '开户行', '联系人', '联系电话', '联系地址',)
    data = []
    order_by = int(filter.get('orderBy', 2))
    order_by = order_by if 0 < order_by <= len(header) else 2
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    logger.debug(sql)
    cursor.execute(sql)
    from profile.models import UserCapitalAccount
    type_dict = dict(UserCapitalAccount.CAPITAL_ACCOUNT_TYPES)
    for row in cursor.fetchall():
        row = list(row)
        row[2] = type_dict.get(row[2], u'未知')
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


finance_supplier_detail.name = '供应商信息表'
finance_supplier_detail.permission = 'report.view_finance_supplier_detail'


def user_credits_report(user=None, filter=None, supplier=None):
    sql = """
        select concat(if(b.nick_name is null, if(b.ex_nick_name is null, '', b.ex_nick_name), b.nick_name), '/', if(b.real_name is null, '', b.real_name)) as name,
            sum(if(a.is_income, a.figure, -a.figure)) as total,
            sum(if(a.is_income, a.figure, 0)) as income,
            sum(if(a.is_income, 1, 0)) as income_cnt,
            sum(if(a.is_income, 0, a.figure)) as expense,
            sum(if(a.is_income, 0, 1)) as expense_cnt,
            a.uid
        from credit_creditbook as a
        join profile_enduser as b on a.uid = b.uid
        where TRUE %s
        group by a.uid
        """
    conditions = []
    params = {}
    if filter.get('from'):
        conditions.append(' and a.create_time >= %(from_date)s')
        params['from_date'] = filter.get('from')
    if filter.get('to'):
        conditions.append(' and a.create_time < %(to_date)s')
        params['to_date'] = filter.get('to')

    cursor = connection.cursor()
    header = ('昵称/姓名', '积分余额', '积分收入总额', '收入笔数', '积分消费总额', '消费笔数', '用户UID',)
    order_by = int(filter.get('orderBy', 3))
    order_by = order_by if 0 < order_by <= len(header) else 3
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql += " limit 100"
    sql %= "".join(conditions)
    logger.debug(sql)
    cursor.execute(sql, params)
    data = cursor.fetchall()

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


user_credits_report.name = '用户积分排行榜（指定时段）'
user_credits_report.permission = 'report.view_user_credits_report'


def credits_distribution(user=None, filter=None, supplier=None):
    sql = """
        select DATE_FORMAT(a.create_time, '%%%%Y-%%%%m-%%%%d') as order_pay_date,
            count(distinct a.uid) as user_cnt,
            sum(if(a.is_income, a.figure, 0))/count(distinct a.uid) as user_avg,
            sum(if(a.is_income, a.figure, 0)) as income,
            sum(if(a.is_income, 1, 0)) as income_cnt,
            sum(if(a.is_income, 0, a.figure)) as expense,
            sum(if(a.is_income, 0, 1)) as expense_cnt
        from credit_creditbook as a
        where TRUE %s
        group by 1
        """
    conditions = []
    params = {}
    if filter.get('from'):
        conditions.append(' and a.create_time >= %(from_date)s')
        params['from_date'] = filter.get('from')
    if filter.get('to'):
        conditions.append(' and a.create_time < %(to_date)s')
        params['to_date'] = filter.get('to')

    cursor = connection.cursor()
    header = ('日期', '发放用户数', '人均发放数', '积分发放总额', '发放笔数', '积分消费总额', '消费笔数', )
    order_by = int(filter.get('orderBy', 1))
    order_by = order_by if 0 < order_by <= len(header) else 1
    sql += " order by %s" % order_by
    is_asc = 'isAsc' in filter
    sql += " asc" if is_asc else " desc"
    sql += " limit 100"
    sql %= "".join(conditions)
    logger.debug(sql)
    cursor.execute(sql, params)
    data = []
    for row in cursor.fetchall():
        row = list(row)
        row[2] = '%.2f' % row[2]
        data.append(row)

    return {"data": data,
            "header": header,
            "summary": [],
            "orderBy": order_by,
            "isAsc": is_asc}


credits_distribution.name = '积分发放统计（按天）'
credits_distribution.permission = 'report.view_credits_distribution'

