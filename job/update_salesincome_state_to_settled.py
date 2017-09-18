# -*- coding: utf-8 -*-
# 用于生成销售商报告

#!/usr/bin/python

import MySQLdb


# 打开数据库连接
db = MySQLdb.connect("127.0.0.1", "tms", "tms@twohou.com", "twohou_tms")

# 使用cursor()方法获取操作游标
cursor = db.cursor()
print "No*id*order_no*status"

# SQL 查询语句
sql = '''
    select id, order_no, status from vendor_suppliersalesincome
    where account_no is not NULL
    and `status`=1
    and revoked_time is NULL
    and settled_time is not NULL
'''
# print sql
try:
    # 执行SQL语句
    cursor.execute(sql)
    # 获取所有记录列表
except:
    print "Error: unable to fecth data"
results = cursor.fetchall()
i = 1
k = 1
for row in results:
    print "%d*%d*%s*%d" % (i, row[0], row[1], row[2])
    i += 1

sql = '''
          update vendor_suppliersalesincome set `status`=2
          where account_no is not NULL
          and `status`=1
          and revoked_time is NULL
          and settled_time is not NULL
          '''

# print sql

try:
    cursor.execute(sql)
    db.commit()
    print 'ok'
except:
    print "Error: unable to fecth data"

# 关闭数据库连接
cursor.close()
db.close()

