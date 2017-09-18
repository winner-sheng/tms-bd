# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0012_enduser_update_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccountbook',
            name='effective_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='\u751f\u6548\u65f6\u95f4', null=True),
        ),
        migrations.AlterField(
            model_name='useraccountbook',
            name='type',
            field=models.CharField(default='other', max_length=10, verbose_name='\u8d26\u76ee\u7c7b\u522b', choices=[('allowance', '\u8865\u8d34'), ('bonus', '\u5956\u52b1'), ('charge', '\u5145\u503c'), ('expense', '\u6d88\u8d39\u652f\u51fa'), ('sales', '\u9500\u552e\u6536\u5165'), ('penalty', '\u7f5a\u6b3e'), ('reward', '\u56de\u4f63'), ('roll-in', '\u8f6c\u5165'), ('roll-out', '\u8f6c\u51fa'), ('withdraw', '\u63d0\u73b0'), ('deduct', '\u6263\u9664'), ('return', '\u8fd4\u8fd8'), ('other', '\u5176\u5b83')]),
        ),
        migrations.AlterField(
            model_name='useraccountbook',
            name='uid',
            field=models.CharField(help_text='\u5bf9\u4e8e\u666e\u901a\u7528\u6237\u662f\u7528\u6237\u7684UID\uff0c\u5bf9\u4e8e\u4f9b\u5e94\u5546\uff0c\u5219\u662f"SUP-"\u524d\u7f00 + \u4f9b\u5e94\u5546\u7f16\u7801\uff0c\u5982"SUP-TWOHOU"', max_length=32, verbose_name='\u7528\u6237UID', db_index=True),
        ),
    ]
