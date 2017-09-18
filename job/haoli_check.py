# -*- coding: utf-8 -*-
# 用于检查王涛给的sellers表伙伴推荐对应关系和uid_referrer里差别用户

#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb
import datetime

# 打开数据库连接
db = MySQLdb.connect("127.0.0.1", "tms", "tms@twohou.com", "twohou_tms")

# 使用cursor()方法获取操作游标
cursor = db.cursor()

# SQL 查询语句
sql = "SELECT order_no, order_date, receiver, receiver_mobile FROM basedata_order where agent_id=10 and order_state=2 order by order_date"
try:
    # 执行SQL语句
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    i = 1
    k = 1
    for row in results:
        o_no = row[0]
        o_date = row[1]
        o_receiver = row[2]
        o_rm = row[3]
        # print "[%s] [%s] [%s] [%s]" % (o_no, o_date, row[3], o_receiver)
        sql = '''
             select order_no, order_date, receiver, receiver_mobile, shop_amount from basedata_order WHERE order_date = "%s" AND receiver_mobile = "%s";
             ''' % (o_date, o_rm)

        cursor.execute(sql)
        res = [row[0] for row in cursor.fetchall()]
        if len(res) > 1:
             print "No.[%d] order_no: [%s] order_date: [%s] receiver: [%s] receiver_mobile: [%s] shop_amount: [%d]" % (i, row[0], row[1], row[2], row[3], row[4])
             i += 1
             # if row[1] == referrer:
             #     # print "uid: [%s] [%s] [%s] is OK!" % (row[0], row[2], referrer)
             #     continue
             # else:
             #     print "[%d] uid: [%s] [%s] referrer is: [%s] has changed to [%s]" % (k, row[0], row[2], referrer, row[1])
             #     k += 1
             #     # sql = '''
             #     #     update profile_enduser set referrer = "%s" WHERE uid = "%s";
             #     # ''' % (referrer, row[0])
             #     # cursor.execute(sql)
             #     # db.commit()
        else:
             continue
             # print "No.[%d] uid: [%s] referrer: [%s] No this uid!" % (i, uid, referrer)
             # i += 1
except:
    print "Error: unable to fecth data"

# 关闭数据库连接
db.close()

# AND (referrer IS NULL or referrer = '')
