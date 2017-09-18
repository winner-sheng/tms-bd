# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0010_auto_20160516_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='rewardrecord',
            name='memo',
            field=models.CharField(help_text='\u7528\u4e8e\u7b80\u5355\u8bf4\u660e\u6536\u76ca\u64a4\u9500\u539f\u56e0', max_length=32, null=True, verbose_name='\u5907\u6ce8', blank=True),
        ),
        migrations.AlterField(
            model_name='rewardrecord',
            name='create_time',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='\u521b\u5efa\u65f6\u95f4', blank=True),
        ),
        migrations.AlterField(
            model_name='rewardrecord',
            name='reward_type',
            field=models.PositiveSmallIntegerField(default=0, null=True, verbose_name='\u6536\u76ca\u7c7b\u578b', blank=True, choices=[(0, '\u9500\u552e\u56de\u4f63'), (1, '\u4f19\u4f34\u9500\u552e\u5956\u52b1')]),
        ),
    ]
