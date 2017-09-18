# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filemgmt', '0002_auto_20160817_1013'),
        ('credit', '0003_auto_20161108_1950'),
    ]

    operations = [
        migrations.AddField(
            model_name='medalcatalog',
            name='image2',
            field=models.ForeignKey(related_name='+', blank=True, to='filemgmt.BaseImage', help_text='\u52cb\u7ae0\u672a\u6fc0\u6d3b\u65f6\u5bf9\u5e94\u7684\u56fe\u7247', null=True, verbose_name='\u672a\u6fc0\u6d3b\u52cb\u7ae0\u56fe\u7247'),
        ),
        migrations.AlterField(
            model_name='medalcatalog',
            name='code',
            field=models.CharField(help_text='\u52cb\u7ae0\u7f16\u7801\uff0c\u7528\u4e8e\u524d\u7aef\u5f15\u7528\uff0c\u9700\u8981\u4fdd\u6301\u552f\u4e00\uff0c\u6bd4\u5982\u7528\u540d\u79f0\u62fc\u97f3\u9996\u5b57\u6bcd', unique=True, max_length=20, verbose_name='\u7f16\u7801'),
        ),
        migrations.AlterField(
            model_name='medalcatalog',
            name='create_by',
            field=models.CharField(help_text='\u5bf9\u4e8e\u901a\u8fc7\u540e\u53f0\u7ba1\u7406\u5165\u53e3\u6dfb\u52a0\u8005\uff0c\u8bb0\u5f55\u7528\u6237\u4fe1\u606f', max_length=32, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True),
        ),
        migrations.AlterField(
            model_name='medalcatalog',
            name='update_by',
            field=models.CharField(help_text='\u5bf9\u4e8e\u901a\u8fc7\u540e\u53f0\u7ba1\u7406\u5165\u53e3\u6dfb\u52a0\u8005\uff0c\u8bb0\u5f55\u7528\u6237\u4fe1\u606f', max_length=32, null=True, verbose_name='\u66f4\u65b0\u4eba', blank=True),
        ),
    ]
