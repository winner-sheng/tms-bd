# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0005_auto_20160824_1948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='effective_date',
            field=models.DateTimeField(default=datetime.datetime.now, help_text='\u53ea\u6709\u751f\u6548\u65f6\u95f4\u540e\u7684\u56fe\u7247\u624d\u4f1a\u5c55\u793a', null=True, verbose_name='\u751f\u6548\u65f6\u95f4', blank=True),
        ),
    ]
