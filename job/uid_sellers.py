# -*- coding: utf-8 -*-
# 用于检查王涛给的sellers表伙伴推荐对应关系和uid_referrer里差别用户

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
    k = 1
    for row in results:
        uid = row[0]
        referrer = row[1]
        sql = '''
             select uid, referrer, nick_name from profile_enduser WHERE uid = "%s";
             ''' % (uid)

        cursor.execute(sql)
        res = [row[0] for row in cursor.fetchall()]
        if len(res) > 0:
             if row[1] == referrer:
                 # print "uid: [%s] [%s] [%s] is OK!" % (row[0], row[2], referrer)
                 continue
             else:
                 print "[%d] uid: [%s] [%s] referrer is: [%s] has changed to [%s]" % (k, row[0], row[2], referrer, row[1])
                 k += 1
                 # sql = '''
                 #     update profile_enduser set referrer = "%s" WHERE uid = "%s";
                 # ''' % (referrer, row[0])
                 # cursor.execute(sql)
                 # db.commit()
        else:
             print "No.[%d] uid: [%s] referrer: [%s] No this uid!" % (i, uid, referrer)
             i += 1
        cursor.close()
except:
    print "Error: unable to fecth data"

# 关闭数据库连接
db.close()

# AND (referrer IS NULL or referrer = '')
