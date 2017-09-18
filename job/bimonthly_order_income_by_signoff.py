# -*- coding: utf-8 -*-
from __future__ import unicode_literals
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
from django.utils import timezone
from tms import settings
from basedata.models import Order
from report.models import TmsReport
from log.models import TaskLog
from util.renderutil import logger
from vendor.models import Supplier, SupplierManager
from util.jsonall import json_encode
from django.db import connection


def order_income_by_signoff(supplier_id=None, from_date=None, to_date=None):
    """
    订单收入/退款统计（列表，按签收时间统计供应商账单，需扣除当前周期之前签收但在当前周期退款的订单）

    :param supplier_id:  为None或者"[TMS]"表示创建总账
    :param from_date:
    :param to_date:
    :return:
    """
    sql_per_signoff = """
        select a.order_no, a.order_state, a.buyer, a.receiver, a.receiver_mobile,
        (select group_concat(concat('[', x.product_id, ']', y.name, '(￥', x.deal_price ,')', '*', x.pcs) separator ';<br>')
            from basedata_orderitem as x
            join basedata_product as y
            on x.product_id = y.code
            where x.order_id=a.order_no) as brief,
        a.pay_date, a.signoff_date, a.pay_amount,
        a.shop_amount,
        a.shop_amount_off, a.ship_fee, a.ship_fee_off, a.pcs_amount, a.package_pcs,
        b.name, c.cost,
        a.refunded_fee,
        if(a.refunded_fee > 0,
            if(a.refunded_fee < c.cost + a.ship_fee - a.ship_fee_off,
                a.refunded_fee,
                c.cost + a.ship_fee - a.ship_fee_off), 0) as deduct,
        a.refund_date
        from basedata_order as a
         left join vendor_supplier as b on a.supplier_id = b.id
         inner join (select x.order_id, sum(if(x.cost, x.cost * x.pcs, y.cost * x.pcs)) as cost
            from basedata_orderitem as x
            join basedata_product as y
            on x.product_id = y.code
            group by x.order_id) as c on a.order_no = c.order_id
         where signoff_date >= %(from_date)s and signoff_date < %(to_date)s
            and a.split_required = 0 and a.agent_id is NULL
        """
    sql_per_refund = """
        select a.order_no, a.order_state, a.buyer, a.receiver, a.receiver_mobile,
        (select group_concat(concat('[', x.product_id, ']', y.name, '(￥', x.deal_price ,')', '*', x.pcs) separator ';<br>')
            from basedata_orderitem as x
            join basedata_product as y
            on x.product_id = y.code
            where x.order_id=a.order_no) as brief,
        a.pay_date, a.signoff_date, '-' as pay_amount,
        '-' as shop_amount,
        '-' as shop_amount_off, '-' as ship_fee, '-' as ship_fee_off, a.pcs_amount, a.package_pcs,
        b.name, c.cost,
        a.refunded_fee,
        if(a.refunded_fee > 0,
            if(a.refunded_fee < c.cost + a.ship_fee - a.ship_fee_off,
                a.refunded_fee,
                c.cost + a.ship_fee - a.ship_fee_off), 0) as deduct,
        a.refund_date
        from basedata_order as a
         left join vendor_supplier as b on a.supplier_id = b.id
         inner join (select x.order_id, sum(if(x.cost, x.cost * x.pcs, y.cost * x.pcs)) as cost
            from basedata_orderitem as x
            join basedata_product as y
            on x.product_id = y.code
            group by x.order_id) as c on a.order_no = c.order_id
         where signoff_date < %(from_date)s and refund_date >= %(from_date)s and refund_date < %(to_date)s
            and a.split_required = 0 and a.agent_id is NULL
        """
    cursor = connection.cursor()
    params = {'from_date': from_date,
              'to_date': to_date}
    if supplier_id and supplier_id != '[TMS]':
        sql_per_signoff += ' and a.supplier_id = %(supplier_id)s'
        sql_per_refund += ' and a.supplier_id = %(supplier_id)s'
        params['supplier_id'] = supplier_id

    sql_per_signoff += ' order by signoff_date asc'
    sql_per_refund += ' order by refund_date asc'

    header = (u'订单号', u'订单状态', u'购买人', u'收件人', u'联系电话', u'订单简介', u'付款时间', u'签收时间', u'支付金额', u'商品总额', u'商品优惠',
              u'邮费', u'邮费优惠', u'商品总数', u'包裹总数', u'供应商', u'供货价', u'订单退款', u'账单扣除', u'退款时间',)
    data = []
    # 获取签收时间在指定报告日期的订单明细
    logger.debug(sql_per_signoff)
    cursor.execute(sql_per_signoff, params)
    state_dict = dict(Order.ORDER_STATES)
    for row in cursor.fetchall():
        row = list(row)
        row[1] = state_dict.get(row[1], u'未知')
        data.append(row)

    # 获取退款时间在指定报告日期的订单明细，签收日期在指定报告日期之前的
    logger.debug(sql_per_refund)
    refund_data = []
    cursor.execute(sql_per_refund, params)
    for row in cursor.fetchall():
        row = list(row)
        row[1] = '已退款（非本期签收订单）'
        refund_data.append(row)

    condition = 'signoff_date >= %(from_date)s and signoff_date < %(to_date)s'
    if supplier_id and supplier_id != '[TMS]':
        condition += ' and a.supplier_id=%(supplier_id)s'
    summary_header = [u'用户支付总额', u'订单退款总额', u'销售商品总额', u'商品优惠总额', u'邮费总额', u'邮费优惠总额',
                      u'货款总额', u'账单扣除总额', u'销售商品总数', u'发送包裹总数', '成交订单数(含退款)', '退款订单数', ]
    summary_sql = """
        select sum(a.pay_amount), sum(a.refunded_fee), sum(a.shop_amount),
        sum(a.shop_amount_off), sum(a.ship_fee), sum(a.ship_fee_off), sum(c.cost),
        sum(if(a.refunded_fee > 0,
                if(a.refunded_fee < c.cost + a.ship_fee - a.ship_fee_off,
                a.refunded_fee,
                c.cost + a.ship_fee - a.ship_fee_off), 0)) as deduct,
        sum(a.pcs_amount), sum(a.package_pcs),
        count(a.order_no) as order_cnt,
        sum(if(a.refunded_fee > 0, 1, 0)) as refund_cnt
        from basedata_order as a
         inner join (select x.order_id, sum(if(x.cost, x.cost * x.pcs, y.cost * x.pcs)) as cost
            from basedata_orderitem as x
            join basedata_product as y
            on x.product_id = y.code
            group by x.order_id) as c on a.order_no = c.order_id
         where a.agent_id is NULL and %(condition)s
        """

    summary_sql = summary_sql % {"condition": condition}
    cursor.execute(summary_sql, params)
    summary_row = list(cursor.fetchone())
    if len(refund_data) > 0:
        # 添加退款记录，并把账单周期之前签收但本周期内退款的订单，退款金额累加
        data.extend(refund_data)
        summary_row[7] = summary_row[7] or 0
        for r in refund_data:
            summary_row[7] += r[15]
            summary_row[11] += 1

    summary = zip(summary_header, summary_row)
    # 账单总额插到第一列
    summary[:0] = [['账单总额', (summary_row[6] or 0) + (summary_row[4] or 0) - (summary_row[5] or 0) - (summary_row[7] or 0)]]
    title_sum = 0
    title_sum = (summary_row[6] or 0) + (summary_row[4] or 0) - (summary_row[5] or 0) - (summary_row[7] or 0)
    cursor.close()
    return {"data": data,
            "header": header,
            "summary": summary,
            "orderBy": 5,
            "isAsc": True,
            "title_sum": title_sum}


TASK_NAME = u'4. 为每个供应商创建账单'
# 2016-10-11之前为版本1
# 2016-10-11更新为版本2，修正退款订单计算错误的问题（误将订单金额作为供货商结算退款金额）
REPORT_VERSION = 2
start_time = datetime.datetime.now()  # if len(sys.argv) == 1 else datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d')
print TASK_NAME, '@', start_time
# if start_time < datetime.datetime(start_time.year, start_time.month, 16, 0, 0, 0):
#     # 为上个月的后半个月创建报表
#     # 跨年日期处理 winner
#     if start_time.month == 1:
#         from_date = datetime.datetime(start_time.year-1, 12, 16, 0, 0, 0)
#         to_date = datetime.datetime(start_time.year, start_time.month, 1, 0, 0, 0)
#     else:
#         from_date = datetime.datetime(start_time.year, start_time.month-1, 16, 0, 0, 0)
#         to_date = datetime.datetime(start_time.year, start_time.month, 1, 0, 0, 0)
# else:
#     # 为本月的上半个月创建报表
#     from_date = datetime.datetime(start_time.year, start_time.month, 1, 0, 0, 0)
#     to_date = datetime.datetime(start_time.year, start_time.month, 16, 0, 0, 0)

if start_time.month == 1:
    from_date = datetime.datetime(start_time.year-1, 12, 1, 0, 0, 0)
    to_date = datetime.datetime(start_time.year, 1, 1, 0, 0, 0)
else:
    from_date = datetime.datetime(start_time.year, start_time.month-1, 1, 0, 0, 0)
    to_date = datetime.datetime(start_time.year, start_time.month, 1, 0, 0, 0)

from_date_str = from_date.strftime('%Y%m%d')
to_date_str = to_date.strftime('%Y%m%d')
suppliers = Supplier.objects.filter(is_active=True, create_time__lt=to_date).values_list('id', 'name')
msg = []
err = []
cnt = 0
suppliers = list(suppliers)
suppliers.append((None, '布丁总账'))
for supplier_id, supplier_name in suppliers:
    supplier_id = supplier_id or '[TMS]'
    if TmsReport.objects.filter(
            report_type='order_income_by_signoff',
            start_time=from_date,
            end_time=to_date,
            owner="SUP-%s" % supplier_id).exists():
        msg.append('%s的报表已创建，忽略' % supplier_name)
        continue
    try:
        print "正在统计供应商%s的报表..." % supplier_name
        report = order_income_by_signoff(supplier_id=supplier_id, from_date=from_date, to_date=to_date)
        if report and 'data' in report:
            cnt += 1
            rp = TmsReport.objects.create(
                report_type='order_income_by_signoff',
                version=REPORT_VERSION,
                title="[%s]销售账单: %s 元" % (supplier_name, report.get('title_sum')),
                start_time=from_date,
                end_time=to_date,
                header=json_encode(report.get('header')),
                data=json_encode(report.get('data')),
                summary=json_encode(report.get('summary')),
                owner="SUP-%s" % supplier_id,
            )
        else:
            err.append('未获得供应商[%s]的统计数据' % supplier_name)
        print "完成"
    except Exception, e:
        print "失败！"
        logger.exception(e)
        err.append('未获得供应商[%s]的统计数据' % supplier_name)

res = '已为%s家供货商成功创建报表' % cnt
print res
end_time = datetime.datetime.now()
try:
    msg.insert(0, res)
    TaskLog.objects.create(
        name=TASK_NAME,
        start_time=start_time,
        end_time=end_time,
        exec_result=";".join(err + msg) or "成功",
        is_ok=len(err) == 0,
        result_file=''
    )
except Exception, e:
    logger.exception(e)
    logger.error('Save task log error: %s' % (e.message or e.args[1]))


