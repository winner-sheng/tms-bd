# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0016_auto_20161129_1246'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotel',
            name='settlement',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='\u7ed3\u7b97\u65b9\u5f0f', choices=[(0, '\u7ebf\u4e0a\u7ed3\u7b97'), (1, '\u7ebf\u4e0b\u7ed3\u7b97'), (2, '\u5176\u4ed6')]),
        ),
        migrations.AddField(
            model_name='logisticsvendor',
            name='settlement',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='\u7ed3\u7b97\u65b9\u5f0f', choices=[(0, '\u7ebf\u4e0a\u7ed3\u7b97'), (1, '\u7ebf\u4e0b\u7ed3\u7b97'), (2, '\u5176\u4ed6')]),
        ),
        migrations.AddField(
            model_name='manufacturer',
            name='settlement',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='\u7ed3\u7b97\u65b9\u5f0f', choices=[(0, '\u7ebf\u4e0a\u7ed3\u7b97'), (1, '\u7ebf\u4e0b\u7ed3\u7b97'), (2, '\u5176\u4ed6')]),
        ),
        migrations.AddField(
            model_name='salesagent',
            name='settlement',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='\u7ed3\u7b97\u65b9\u5f0f', choices=[(0, '\u7ebf\u4e0a\u7ed3\u7b97'), (1, '\u7ebf\u4e0b\u7ed3\u7b97'), (2, '\u5176\u4ed6')]),
        ),
        migrations.AddField(
            model_name='store',
            name='settlement',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='\u7ed3\u7b97\u65b9\u5f0f', choices=[(0, '\u7ebf\u4e0a\u7ed3\u7b97'), (1, '\u7ebf\u4e0b\u7ed3\u7b97'), (2, '\u5176\u4ed6')]),
        ),
        migrations.AddField(
            model_name='supplier',
            name='settlement',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='\u7ed3\u7b97\u65b9\u5f0f', choices=[(0, '\u7ebf\u4e0a\u7ed3\u7b97'), (1, '\u7ebf\u4e0b\u7ed3\u7b97'), (2, '\u5176\u4ed6')]),
        ),
    ]
