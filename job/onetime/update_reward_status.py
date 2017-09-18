# -*- coding: utf-8 -*-
import os
PROJECT_PATH = os.path.abspath('%s/../..' % __file__)
DJANGO_SETTINGS = "tms.settings"

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

from basedata.models import Product
from util.qiniu_util import convert_intro2qiniu

products = Product.objects.all()
total_prd = 0
total_img = 0
for prd in products:
    print "check [%s]..." % prd.name
    prd.intro, cnt = convert_intro2qiniu(prd.intro)
    if cnt > 0:
        total_img += cnt
        total_prd += 1
        prd.save()

print "Total %s products updated, %s images uploaded to Qiniu" % (total_prd, total_img)