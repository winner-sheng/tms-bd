# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0004_auto_20160722_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermaillog',
            name='mail_from',
            field=models.CharField(default=b'TMS <oms@sh-anze.com>', max_length=60, null=True, verbose_name='\u53d1\u4ef6\u5730\u5740', blank=True),
        ),
    ]
