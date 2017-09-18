# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0020_auto_20170428_1841'),
    ]

    operations = [
        migrations.AddField(
            model_name='rewardrecord',
            name='store_code',
            field=models.CharField(max_length=32, blank=True, help_text='\u5e97\u94fa\u7f16\u7801', null=True, verbose_name='\u5e97\u94fa\u4ee3\u7801', db_index=True),
        ),
    ]
