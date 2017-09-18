# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
PROJECT_PATH = os.path.abspath('%s/../../..' % __file__)
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
from log.models import TaskLog
from basedata.fileimport import sync_twohou_product
from util.renderutil import logger, random_code
from util.jsonall import json_encode

now = timezone.now() if settings.USE_TZ else datetime.datetime.now()
start_time = datetime.datetime.now()
print start_time
is_ok = True

sync_result = sync_twohou_product()
end_time = datetime.datetime.now()
is_ok = len(sync_result.get('error')) > 0
exec_result = []
if not is_ok:
    exec_result = sync_result['error']

exec_result.extend([
    '新增商品记录%s条' % sync_result['product_add'],
    '新增品牌记录%s条' % sync_result['brand_add'],
    '新增生产商记录%s条' % sync_result['manufacturer_add'],
    '新增供应商记录%s条' % sync_result['supplier_add'],
    '新增图片%s张' % sync_result['image_add'],
    '共计%s条警告' % len(sync_result['warnings']),
    '共计%s条消息' % len(sync_result['messages']),
])
exec_result.extend(sync_result['warnings'])
exec_result.extend(sync_result['messages'])
result = ";\n".join(exec_result)
print result
log_path = settings.LOG_ROOT+datetime.datetime.now().strftime('%Y%m/')
os.path.exists(log_path) or os.makedirs(log_path, mode=0744)
log_file = log_path+datetime.datetime.now().strftime('sync%d-%H%M%S-')+random_code(4)

try:
    writer = open(log_file, 'wb+')
    writer.write(result)
    TaskLog.objects.create(
        name='同步OMS商品信息',
        start_time=start_time,
        end_time=end_time,
        exec_result=result,
        is_ok=is_ok,
        result_file=''
    )
except Exception, e:
    logger.exception(e)
    print 'Save task log error: %s' % (e.message or e.args[1])
