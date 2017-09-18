# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import util.renderutil


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0008_auto_20160803_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logisticsvendor',
            name='code',
            field=models.CharField(default=util.renderutil.random_code, help_text='\u53ef\u81ea\u52a8\u751f\u6210\uff0c\u5efa\u8bae\u7edf\u4e00\u4f7f\u7528\u7528\u62fc\u97f3\u9996\u5b57\u6bcd\u4f5c\u4e3a\u7f16\u7801(\u6ce8\uff1a"TWOHOU-"\u524d\u7f00\u4e3a\u571f\u7334\u4e13\u7528)', unique=True, max_length=32, verbose_name='\u7f16\u7801'),
        ),
        migrations.AlterField(
            model_name='manufacturer',
            name='code',
            field=models.CharField(default=util.renderutil.random_code, help_text='\u53ef\u81ea\u52a8\u751f\u6210\uff0c\u5efa\u8bae\u7edf\u4e00\u4f7f\u7528\u7528\u62fc\u97f3\u9996\u5b57\u6bcd\u4f5c\u4e3a\u7f16\u7801(\u6ce8\uff1a"TWOHOU-"\u524d\u7f00\u4e3a\u571f\u7334\u4e13\u7528)', unique=True, max_length=32, verbose_name='\u7f16\u7801'),
        ),
        migrations.AlterField(
            model_name='store',
            name='code',
            field=models.CharField(default=util.renderutil.random_code, help_text='\u53ef\u81ea\u52a8\u751f\u6210\uff0c\u5efa\u8bae\u7edf\u4e00\u4f7f\u7528\u7528\u62fc\u97f3\u9996\u5b57\u6bcd\u4f5c\u4e3a\u7f16\u7801(\u6ce8\uff1a"TWOHOU-"\u524d\u7f00\u4e3a\u571f\u7334\u4e13\u7528)', unique=True, max_length=32, verbose_name='\u7f16\u7801'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='code',
            field=models.CharField(default=util.renderutil.random_code, help_text='\u53ef\u81ea\u52a8\u751f\u6210\uff0c\u5efa\u8bae\u7edf\u4e00\u4f7f\u7528\u7528\u62fc\u97f3\u9996\u5b57\u6bcd\u4f5c\u4e3a\u7f16\u7801(\u6ce8\uff1a"TWOHOU-"\u524d\u7f00\u4e3a\u571f\u7334\u4e13\u7528)', unique=True, max_length=32, verbose_name='\u7f16\u7801'),
        ),
    ]
