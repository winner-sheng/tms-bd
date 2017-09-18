# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0016_auto_20160831_1523'),
    ]

    operations = [
        migrations.AddField(
            model_name='enduserenterprise',
            name='created_by',
            field=models.CharField(max_length=32, null=True, verbose_name='\u7533\u8bf7\u4ebaUID', blank=True),
        ),
    ]
