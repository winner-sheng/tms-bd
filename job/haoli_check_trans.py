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

print "Source: basedata_order, Dest: transport_logs"

# SQL 查询语句
sql = "SELECT order_no, order_date, receiver, receiver_mobile FROM basedata_order where agent_id=10 order by order_date"
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
             select order_no from transport_logs WHERE order_no = "%s"
             ''' % (o_no)

        cursor.execute(sql)
        res = [row[0] for row in cursor.fetchall()]
        if len(res) > 0:
            continue
        else:
            # continue
            print "No.[%d] order_no: [%s] order_date: [%s] mobile: [%s] ===> is NONE!" % (i, o_no, o_date, o_rm)
            i += 1
except:
    print "Error: unable to fecth data"

# 关闭数据库连接
db.close()

# AND (referrer IS NULL or referrer = '')
