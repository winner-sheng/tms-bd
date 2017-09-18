# -*- coding: utf-8 -*-
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
from log.models import TaskLog, WechatMsgLog
TASK_NAME = u'15. 微信消息处理任务'
NO_WECHAT = u"没有待处理微信消息"
start_time = datetime.datetime.now()
print TASK_NAME, start_time
rows = None
# 获取所有待发邮件
is_ok = True
try:
    msgs = WechatMsgLog.objects.filter(is_sent=False, retries__lt=5, subject__contains="积分变动提醒")
    rows = msgs.count()
    if rows > 0:
        failed_cnt = 0
        for msg in msgs:
            try:
                msg.send_message()
            except Exception, e:
                failed_cnt += 1
                print 'failed to send Wechat message to： ', msg.uid
                print 'message subject: ', msg.subject
                print e.message
        msg = u'共发送%s条微信消息（失败%s）' % (rows, failed_cnt)
    else:
        msg = NO_WECHAT
except Exception, e:
    is_ok = False
    msg = "Check WechatMsgLog FAILED! %s" % (e.message or e.args[1])

print msg

end_time = datetime.datetime.now()
try:
    # latest = TaskLog.objects.filter(name=TASK_NAME).last()
    # if latest and latest.start_time > (datetime.datetime.now() - datetime.timedelta(hours=1)) \
    #         and latest.exec_result == NO_WECHAT:
    #     pass  # do not log task status one more time in an hour, if no emails
    # else:
    TaskLog.objects.create(
        name=TASK_NAME,
        start_time=start_time,
        end_time=end_time,
        exec_result=msg,
        is_ok=is_ok,
        result_file=''
    )
except Exception, e:
    print 'Save task log error: %s' % (e.message or e.args[1])
