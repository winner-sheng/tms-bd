# -*- coding: utf-8 -*-
# 用于重建伙伴推荐对应关系

#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb

# 打开数据库连接
db = MySQLdb.connect("127.0.0.1", "tms", "tms@twohou.com", "twohou_tms")

# 使用cursor()方法获取操作游标
cursor = db.cursor()

# SQL 查询语句
sql = "SELECT * FROM sellers"
try:
   # 执行SQL语句
   cursor.execute(sql)
   # 获取所有记录列表
   results = cursor.fetchall()
   i = 1
   for row in results:
       # uid = row[0]
       # referrer = row[1]
       sql = '''
           update profile_enduser set referrer = "%s" WHERE uid = "%s";
       ''' % (row[1], row[0])
       cursor.execute(sql)
       db.commit()
       print "No.[%d] uid: [%s] <-->  referrer: [%s] SQL: %s" % \
            (i, row[0], row[1], sql)
       i=i+1
       cursor.close()
except:
   print "Error: unable to fecth data"

# 关闭数据库连接
db.close()

# AND (referrer IS NULL or referrer = '')
