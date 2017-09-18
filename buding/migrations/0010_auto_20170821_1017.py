# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buding', '0009_auto_20170727_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='saleshopproduct',
            name='list_order',
            field=models.PositiveIntegerField(default=0, help_text='\u6570\u503c\u8d8a\u5927\uff0c\u6392\u5e8f\u8d8a\u9760\u524d', verbose_name='\u6392\u5e8f\u6807\u8bb0'),
        ),
        migrations.AddField(
            model_name='saleshopproduct',
            name='tags',
            field=models.CharField(max_length=128, blank=True, help_text='\u7528\u4e8e\u5546\u54c1\u641c\u7d22\uff0c\u6bcf\u4e2a\u6807\u7b7e\u4e4b\u95f4\u5e94\u4f7f\u7528\u82f1\u6587\u9017\u53f7","\u5206\u9694\uff0c\u6807\u7b7e\u4e3a\u7cbe\u786e\u5339\u914d', null=True, verbose_name='\u5546\u54c1\u6807\u7b7e', db_index=True),
        ),
        migrations.AlterField(
            model_name='saleshopproduct',
            name='productid',
            field=models.CharField(help_text='\u5546\u54c1\u4ee3\u7801', max_length=32, verbose_name='\u5546\u54c1\u4ee3\u7801', db_index=True),
        ),
    ]
