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
from basedata.models import Product
from log.models import TaskLog
from django.db.models import F
from log.models import UserMailLog
from util.renderutil import logger


TASK_NAME = u'8. 商品库存检查任务'
start_time = datetime.datetime.now()
print TASK_NAME, start_time
rows = None
# 获取所有待发货的订单
is_ok = True
try:
    products = Product.objects.filter(status=Product.STATUS_ONSHELF,
                                      stock_volume__lte=F('stock_volume_threshold'))\
        .order_by('supplier')
    rows = products.count()
    if rows > 0:
        supplier_products_dict = {}
        supplier_mails_dict = {}
        supplier_dict = {}
        msgs = []
        for p in products:
            if p.supplier_id not in supplier_mails_dict:
                supplier_dict[p.supplier_id] = p.supplier
                emails = p.supplier.get_email_to()
                managers = p.supplier.suppliermanager_set.all()
                for mgr in managers:
                    if mgr.user and mgr.user.email:
                        emails.append(mgr.user.email)

                supplier_mails_dict[p.supplier_id] = emails
                supplier_products_dict[p.supplier_id] = set([p])
            else:
                # if len(supplier_mails_dict[p.supplier_id]) == 0:  # ignore as the supplier has no email
                supplier_products_dict[p.supplier_id].add(p)

        s_count = p_count = m_ok = m_failed = 0
        for s_id, mails in supplier_mails_dict.items():
            s_products = supplier_products_dict[s_id]
            s_count += 1
            p_count += len(s_products)
            if len(mails) == 0:
                msgs.append(u'供应商[%s]缺少email地址' % supplier_dict[s_id].name)
                # m_failed += 1
                continue

            mails = list(set(mails))
            print "sending mails to : ", mails
            subject = u'【TMS】：您有%s种商品库存达到预警条件，请及时补货！' % len(s_products)
            mail_msg = [u'以下商品库存达到预警条件，请及时补货：']
            for s_p in s_products:
                mail_msg.append(u"【%s】 - 库存 %s (预警阈值: %s)" % (s_p.name, s_p.stock_volume, s_p.stock_volume_threshold))
            mail_msg.append(u"\n请注意，您可以采取以下措施来阻止后续预警消息通知：\n")
            mail_msg.append(u"1. 立即补货，并在平台更新库存数量\n")
            mail_msg.append(u"2. 无法补货修改库存数量，则在平台调低预警阈值，如果设为0则不再报警\n")
            mail_msg.append(u"3. 如果已经0库存，可将商品下架，即设置商品状态为“下架”\n")
            mail_msg.append(u"\n请登录TMS系统进行处理，网址：http://tms.twohou.com:8001/stms/")
            try:
                UserMailLog.put_in_queue(mail_to=mails, subject=subject, body="\n".join(mail_msg))
                m_ok += 1
            except Exception, e:
                logger.exception(e)
                m_failed += 1
                is_ok = False  # job flag
                msgs.append(u'给供应商【%s】发送通知失败: %s' % (s_products[0].supplier.name, e.message))

        msgs.append(u'发现%s家供应商%s种商品库存符合预警条件，已发送%s条通知（失败%s条）'
                    % (s_count, p_count, m_ok, m_failed))
        msg = "\n".join(msgs)
    else:
        msg = u"未发现需库存预警商品!"
except Exception, e:
    logger.exception(e)
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
