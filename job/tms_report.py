# -*- coding: utf-8 -*-
# 用于生成销售商报告

#!/usr/bin/python

import MySQLdb
import datetime

s_date = "2017-06-01 00:00:00"
e_date = "2017-07-01 00:00:00"


# 打开数据库连接
db = MySQLdb.connect("127.0.0.1", "tms", "tms@twohou.com", "twohou_tms")

# 使用cursor()方法获取操作游标
cursor = db.cursor()

f = open("tms_report.txt", 'w')

print >> f, "结算周期：%s  <-->  %s"  % (s_date, e_date)
print >> f, "序号,供应商名称,供应商ID,账单总额,积分支付,订单退款总额,销售商品总额,商品优惠总额,邮费总额,邮费优惠总额,货款总额,账单扣除总额,销售商品总数,发送包裹总数,成交订单数(含退款),退款订单数"

# SQL 查询语句
sql = '''
    select id, name, code from vendor_supplier
'''
try:
    # 执行SQL语句
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    i = 1
    k = 1
    for row in results:
        v_id = row[0]
        v_name = row[1]
        v_code = row[2]
        # o_rm = row[3]
        # print "[%s] [%s] [%s] [%s]" % (o_no, o_date, row[3], o_receiver)
        # +a.balance_payment + a.credits_expense / 100
        sql = '''
                select
                sum(a.pay_amount), sum(a.refunded_fee), sum(a.shop_amount),
                sum(a.shop_amount_off), sum(a.ship_fee), sum(a.ship_fee_off), sum(c.cost),
                sum( if (a.refunded_fee > 0,
                if (a.refunded_fee < c.cost + a.ship_fee - a.ship_fee_off, a.refunded_fee,
                    c.cost + a.ship_fee - a.ship_fee_off), 0)) as deduct,
                sum(a.pcs_amount), sum(a.package_pcs),
                count(a.order_no) as order_cnt,
                sum( if (a.refunded_fee > 0, 1, 0)) as refund_cnt
                from basedata_order as a

                inner join(select x.order_id, sum( if (x.cost, x.cost * x.pcs, y.cost * x.pcs)) as cost
                from basedata_orderitem as x

                join basedata_product as y
                on x.product_id = y.code
                group by x.order_id) as c
                on a.order_no = c.order_id
                where signoff_date >= "%s" and signoff_date < "%s"
                and a.supplier_id = %d
             ''' % (s_date, e_date, v_id)
        # conditions = []
        # params = {}
        # if filter.get('from'):
        #     conditions.append(' and a.create_time >= %(from_date)s')
        #     params['from_date'] = filter.get('from')
        # if filter.get('to'):
        #     conditions.append(' and a.create_time < %(to_date)s')
        #     params['to_date'] = filter.get('to')

        cursor.execute(sql)
        # nos = [row[0] for row in cursor.fetchall()]
        summ_row = list(cursor.fetchone())
        if summ_row[0]:
            print >> f, "%d,%s,%d,%.2f," \
                        "%.2f," \
                        "%.2f,%.2f,%.2f," \
                        "%.2f,%.2f,%.2f," \
                        "%d,%d,%d,%d" % (i, v_name, v_id, summ_row[0],
                                         summ_row[1], summ_row[2], summ_row[3],
                                         summ_row[4], summ_row[5], summ_row[6],
                                         summ_row[7], summ_row[8], summ_row[9],
                                         summ_row[10], summ_row[11])
        else:
            print >> f, "%d,%s,%d," % (i, v_name, v_id)
        i += 1
except:
    print "Error: unable to fecth data"

f.flush()
f.close()
# 关闭数据库连接
cursor.close()
db.close()

# AND (referrer IS NULL or referrer = '')
