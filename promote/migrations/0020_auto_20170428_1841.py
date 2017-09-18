# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0019_auto_20161129_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rewardrecord',
            name='reward_type',
            field=models.PositiveSmallIntegerField(default=0, null=True, verbose_name='\u6536\u76ca\u7c7b\u578b', blank=True, choices=[(0, '\u9500\u552e\u56de\u4f63'), (1, '\u4f19\u4f34\u9500\u552e\u5956\u52b1'), (2, '\u4f01\u4e1a\u7ba1\u7406\u8d39\u7528'), (3, '\u8f6c\u53d1\u63a8\u5e7f\u56de\u4f63')]),
        ),
    ]
