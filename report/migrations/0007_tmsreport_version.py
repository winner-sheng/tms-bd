# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0006_auto_20160922_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='tmsreport',
            name='version',
            field=models.PositiveSmallIntegerField(default=1, help_text='\u8003\u8651\u5230\u7531\u4e8e\u9700\u6c42\u7684\u53d8\u5316\uff0c\u62a5\u8868\u6570\u636e\u683c\u5f0f\u53ef\u80fd\u4f1a\u6709\u6240\u8c03\u6574\uff0c\u7528\u4e8e\u8bf4\u660e\u6570\u636e\u7684\u7248\u672c', verbose_name='\u7248\u672c'),
        ),
    ]
