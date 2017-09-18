# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filemgmt', '0002_auto_20160817_1013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseimage',
            name='origin',
            field=models.ImageField(help_text='\u5e94\u5c3d\u91cf\u907f\u514d\u4f7f\u7528\u975e\u82f1\u6587\u5b57\u7b26\u547d\u540d\u7684\u56fe\u7247\u6587\u4ef6', upload_to='%Y/%m/%d', verbose_name='\u539f\u59cb\u56fe\u7247'),
        ),
    ]
