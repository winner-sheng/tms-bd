# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('credit', '0004_auto_20161117_1741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditbook',
            name='create_by',
            field=models.CharField(help_text='\u5bf9\u4e8e\u901a\u8fc7\u540e\u53f0\u7ba1\u7406\u5165\u53e3\u6dfb\u52a0\u8005\uff0c\u8bb0\u5f55\u7528\u6237\u4fe1\u606f', max_length=32, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True),
        ),
        migrations.AlterField(
            model_name='rankseries',
            name='create_by',
            field=models.CharField(help_text='\u5bf9\u4e8e\u901a\u8fc7\u540e\u53f0\u7ba1\u7406\u5165\u53e3\u6dfb\u52a0\u8005\uff0c\u8bb0\u5f55\u7528\u6237\u4fe1\u606f', max_length=32, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True),
        ),
        migrations.AlterField(
            model_name='rankseries',
            name='update_by',
            field=models.CharField(help_text='\u5bf9\u4e8e\u901a\u8fc7\u540e\u53f0\u7ba1\u7406\u5165\u53e3\u6dfb\u52a0\u8005\uff0c\u8bb0\u5f55\u7528\u6237\u4fe1\u606f', max_length=32, null=True, verbose_name='\u66f4\u65b0\u4eba', blank=True),
        ),
        migrations.AlterField(
            model_name='ranktitle',
            name='right_value',
            field=models.PositiveIntegerField(default=0, help_text='\u5373\u8be5\u7b49\u7ea7\u5bf9\u5e94\u7684\u6307\u6807\u4e0a\u9650\uff0c\u5927\u4e8e\u8be5\u6307\u6807\u5219\u4e3a\u4e0a\u4e00\u7ea7\u6307\u5b9a\u79f0\u53f7', verbose_name='\u6307\u6807\u4e0a\u9650\uff08\u5305\u542b\uff09'),
        ),
        migrations.AlterUniqueTogether(
            name='usermedal',
            unique_together=set([('uid', 'medal')]),
        ),
    ]
