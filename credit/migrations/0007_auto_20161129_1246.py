# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('credit', '0006_auto_20161123_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertitle',
            name='uid',
            field=models.CharField(help_text='\u5bf9\u4e8e\u666e\u901a\u7528\u6237\u662f\u7528\u6237\u7684UID\uff0c\u5bf9\u4e8e\u4f9b\u5e94\u5546\uff0c\u5219\u662f"SUP-"\u524d\u7f00 + \u4f9b\u5e94\u5546\u7f16\u7801\uff0c\u5982"SUP-TWOHOU"', unique=True, max_length=32, verbose_name='\u7528\u6237UID'),
        ),
    ]
