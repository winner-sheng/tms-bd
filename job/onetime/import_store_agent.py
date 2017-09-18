# -*- coding: utf-8 -*-
import os
PROJECT_PATH = os.path.abspath('%s/../..' % __file__)
DJANGO_SETTINGS = "tms.settings"
DAYS_TO_CLOSE_ORDER = 15  # days

import sys
print('Python %s on %s' % (sys.version, sys.platform))
import django
print('Django %s' % django.get_version())
sys.path.extend([PROJECT_PATH])
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS)
print sys.path
if 'setup' in dir(django):
    django.setup()

from django.utils import timezone
from log.models import TaskLog
from util import jsonall
start_time = timezone.now()
from filemgmt.views import load_agent
if len(sys.argv) < 2:
    print "Pls specify the excel file to load."
    sys.exit(1)

result = load_agent(sys.argv[1])
exec_result = jsonall.json_encode(result)
try:
    TaskLog.objects.create(
        name='导入门店及前台账号',
        start_time=start_time,
        end_time=timezone.now(),
        exec_result=exec_result,
        is_ok=not result.get("error"),
        result_file=sys.argv[1]
    )

except Exception, e:
    print 'Save task log error: %s' % (e.message or e.args[1])

print "Totally created %s user accounts, %s stores, %s contacts." % \
      (result.get('counter').get('user'),
       result.get('counter').get('store'),
       result.get('counter').get('contact'))
if result.get('error'):
    print "ERROR:"
    print "\n".join(result.get('error'))
if result.get('warning'):
    print "WARNING:"
    print "\n".join(result.get('warning'))
print "Import completed!"