# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('credit', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditbook',
            name='create_by',
            field=models.CharField(help_text='\u5bf9\u4e8e\u901a\u8fc7\u540e\u53f0\u7ba1\u7406\u5165\u53e3\u6dfb\u52a0\u8005\uff0c\u8bb0\u5f55\u7528\u6237\u4fe1\u606f"', max_length=32, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True),
        ),
    ]
