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
from tms import settings
from basedata.models import Order
from log.models import TaskLog, UserMailLog
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist
from util.renderutil import now
from config.models import AppSetting
from vendor.models import Supplier, Contact

timeout = AppSetting.get('app.order_to_ship_timeout', 3)  # hours
TASK_NAME = u'10. 待发货订单检查任务'
start_time = now()
print TASK_NAME, start_time
rows = None
# 获取所有待发货的订单
is_ok = True
try:
    # 获取超时未处理订单
    orders = Order.objects.filter(order_state=Order.STATE_TO_SHIP,
                                  is_closed=False,
                                  is_deleted=False,
                                  pay_date__lt=now(settings.USE_TZ)-datetime.timedelta(hours=timeout))
    rows = orders.count()
    if rows > 0:
        mail_msg = [u'以下是最近10条订单列表：']
        receivers = AppSetting.get('app.order_recipients', 'winsom.huang@sh-anze.com')
        for order in orders[:10]:
            mail_msg.append(order.order_brief)

        mail_msg.append(u'\n请登录 http://tms.twohou.com:8001/tms/ 查看')
        supplier_cnt = orders.values('supplier').distinct().order_by('supplier')\
            .aggregate(cnt=Count('supplier')).get('cnt')
        msg = subject = u'【TMS】：合计【%s】家供应商【%s】条订单超过%s小时未处理！' % (supplier_cnt, rows, timeout)
        if receivers:
            receivers = receivers[:-1] if receivers[-1] == ';' else receivers
            print receivers
            # send_mail(subject, "\n".join(mail_msg), settings.DEFAULT_FROM_EMAIL, receivers.split(';'))
            UserMailLog.put_in_queue(mail_to=receivers.split(';'), subject=subject, body="\n".join(mail_msg))

        else:
            msg = u"缺少管理员email地址"
    else:
        msg = u"还木有订单呢!"
except Exception, e:
    is_ok = False
    msg = "Check order FAILED! %s" % (e.message or e.args[1])

print msg

end_time = datetime.datetime.now()
try:
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

# prepare mails to each supplier
TASK_NAME = u'11. 待发货订单检查任务(供应商)'
start_time = datetime.datetime.now()
print TASK_NAME, start_time
rows = None
# 获取所有待发货的订单
is_ok = True
try:
    qs = Order.objects.filter(order_state=Order.STATE_TO_SHIP,
                              is_closed=False,
                              is_deleted=False,
                              pay_date__lt=now(settings.USE_TZ)-datetime.timedelta(hours=timeout))
    counters = qs.values('supplier').order_by('supplier').annotate(order_cnt=Count('*'))
    msgs = [u"共有%s家供应商有超时未处理订单" % counters.count()]

    for c in counters:
        if c['supplier']:
            sup = Supplier.objects.get(id=c['supplier'])
            contact = Contact.objects.get(id=sup.primary_contact_id)
            if sup.backup_contact_id:
                contact_backup = Contact.objects.get(id=sup.backup_contact_id)
            orders = qs.filter(supplier_id=c['supplier'])
            mail_msg = [u'以下是订单列表（最多显示10条）：']
            for order in orders[:10]:
                mail_msg.append(order.order_brief)

            mail_msg.append(u'\n请登录 http://tms.twohou.com:8001/stms/ 查看')
            subject = u'【TMS】：您【%s】有【%s】条订单超过%s小时未发货，请尽快处理！' % (sup.name, orders.count(), timeout)

            emails = []
            try:
                if order.supplier:
                    emails = order.supplier.get_email_to()
                    # if order.supplier.primary_contact and order.supplier.primary_contact.email:
                    #     emails.append(order.supplier.primary_contact.email)
                    # if order.supplier.backup_contact and order.supplier.backup_contact.email:
                    #     emails.append(order.supplier.backup_contact.email)
                    # managers = order.supplier.suppliermanager_set.all()
                    # for mgr in managers:
                    #     if mgr.user and mgr.user.email:
                    #         emails.append(mgr.user.email)
            except ObjectDoesNotExist:
                pass

            if len(emails) > 0:
                emails = set(emails)
                print 'Sending mails to : ',  ';'.join(emails)
                # send_mail(subject, "\n".join(mail_msg), settings.DEFAULT_FROM_EMAIL, emails)
                UserMailLog.put_in_queue(mail_to=emails, subject=subject, body="\n".join(mail_msg))

            else:
                msgs.append(u'供应商[%s]缺少email地址' % order.supplier.name)
        else:
            orders = qs.filter(supplier_id=c['supplier']).values('order_no')
            order_nos = [order['order_no'] for order in orders]
            msgs.append(u'订单[%s]缺少供应商信息！' % ",".join(order_nos))
    msg = "\n".join(msgs) if len(msgs) > 0 else ''
except Exception, e:
    is_ok = False
    msg = "Check order FAILED! %s" % (e.message or e.args[1])

print msg

end_time = datetime.datetime.now()
try:
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
