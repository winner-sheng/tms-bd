# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0009_auto_20160505_1205'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='useraccountbook',
            options={'ordering': ['-pk'], 'verbose_name': '\u7528\u6237\u8d44\u91d1\u6d41\u6c34', 'verbose_name_plural': '\u7528\u6237\u8d44\u91d1\u6d41\u6c34'},
        ),
        migrations.AddField(
            model_name='withdrawrequest',
            name='process_time',
            field=models.DateTimeField(null=True, verbose_name='\u5b8c\u6210\u65f6\u95f4', blank=True),
        ),
        migrations.AlterField(
            model_name='useraccountbook',
            name='type',
            field=models.CharField(default=b'other', max_length=10, verbose_name='\u8d26\u76ee\u7c7b\u522b', choices=[(b'allowance', '\u8865\u8d34'), (b'bonus', '\u5956\u52b1'), (b'charge', '\u5145\u503c'), (b'expense', '\u6d88\u8d39\u652f\u51fa'), (b'penalty', '\u7f5a\u6b3e'), (b'reward', '\u56de\u4f63'), (b'roll-in', '\u8f6c\u5165'), (b'roll-out', '\u8f6c\u51fa'), (b'withdraw', '\u63d0\u73b0'), (b'deduct', '\u6263\u9664'), (b'return', '\u8fd4\u8fd8'), (b'other', '\u5176\u5b83')]),
        ),
        migrations.AlterField(
            model_name='userhistory',
            name='entity_type',
            field=models.CharField(max_length=2, verbose_name='\u8bbf\u95ee\u5bf9\u8c61\u7c7b\u578b', choices=[(b'P', '\u5546\u54c1'), (b'KW', '\u641c\u7d22'), (b'A', '\u6587\u7ae0')]),
        ),
    ]
