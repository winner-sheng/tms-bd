# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0012_auto_20160706_1546'),
    ]

    operations = [
        migrations.AddField(
            model_name='rewardrecord',
            name='source_uid',
            field=models.CharField(max_length=32, blank=True, help_text='\u5982\u679c\u662f\u9500\u552e\u56de\u4f63\uff0c\u5219\u4e3a\u4e70\u5bb6uid\uff0c\u5982\u679c\u662f\u4f19\u4f34\u9500\u552e\u5956\u52b1\uff0c\u5219\u4e3a\u4f19\u4f34uid\uff0c\u5982\u679c\u662f\u4f01\u4e1a\u7ba1\u7406\u8d39\u7528\uff0c\u5219\u4e3a\u4e0b\u5c5e\u4f01\u4e1auid', null=True, verbose_name='\u6536\u76ca\u6765\u6e90\u7528\u6237UID', db_index=True),
        ),
        migrations.AlterField(
            model_name='rewardrecord',
            name='reward_type',
            field=models.PositiveSmallIntegerField(default=0, null=True, verbose_name='\u6536\u76ca\u7c7b\u578b', blank=True, choices=[(0, '\u9500\u552e\u56de\u4f63'), (1, '\u4f19\u4f34\u9500\u552e\u5956\u52b1'), (2, '\u4f01\u4e1a\u7ba1\u7406\u8d39\u7528')]),
        ),
    ]
