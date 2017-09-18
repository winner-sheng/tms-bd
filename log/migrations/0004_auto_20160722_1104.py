# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0003_auto_20160428_2259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wechatmsglog',
            name='open_id',
            field=models.CharField(db_index=True, max_length=32, null=True, verbose_name='\u5fae\u4fe1OpenID', blank=True),
        ),
    ]
