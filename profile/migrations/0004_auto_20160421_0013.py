# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0003_auto_20160420_2322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccountbook',
            name='type',
            field=models.CharField(default=b'other', max_length=10, verbose_name=b'\xe8\xb4\xa6\xe7\x9b\xae\xe7\xb1\xbb\xe5\x88\xab', choices=[(b'bonus', '\u5956\u52b1'), (b'charge', '\u5145\u503c'), (b'expense', '\u6d88\u8d39\u652f\u51fa'), (b'penalty', '\u7f5a\u6b3e'), (b'reward', '\u56de\u4f63'), (b'roll-in', '\u8f6c\u5165'), (b'roll-out', '\u8f6c\u51fa'), (b'withdraw', '\u63d0\u73b0'), (b'deduct', '\u6263\u9664'), (b'other', '\u5176\u5b83')]),
        ),
    ]
