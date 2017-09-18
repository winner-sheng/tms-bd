# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0021_auto_20161017_2152'),
    ]

    operations = [
        migrations.AddField(
            model_name='withdrawrequest',
            name='real_uid',
            field=models.CharField(help_text='\u5bf9\u4e8e\u975e\u4e2a\u4eba\u63d0\u73b0\u7533\u8bf7\uff0c\u8fd9\u91cc\u5c06\u4fdd\u5b58\u53d1\u8d77\u63d0\u73b0\u7533\u8bf7\u7684\u7528\u6237UID', max_length=32, null=True, verbose_name='\u63d0\u73b0\u7528\u6237UID', blank=True),
        ),
        migrations.AddField(
            model_name='withdrawrequest',
            name='uid_type',
            field=models.PositiveSmallIntegerField(default=2, verbose_name='\u7528\u6237\u7c7b\u578b', choices=[(0, '\u4e2a\u4eba'), (1, '\u4f9b\u5e94\u5546'), (2, '\u5176\u4ed6')]),
        ),
    ]
