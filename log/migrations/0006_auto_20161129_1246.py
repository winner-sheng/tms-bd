# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0005_auto_20160805_1615'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersmslog',
            name='allow_retries',
            field=models.PositiveSmallIntegerField(default=1, help_text='\u5f53\u5141\u8bb8\u91cd\u8bd5\u6b21\u6570\u51cf\u4e3a0\u540e\u4e0d\u518d\u53d1\u9001\u8be5\u77ed\u4fe1', verbose_name='\u5141\u8bb8\u91cd\u8bd5\u6b21\u6570'),
        ),
        migrations.AddField(
            model_name='usersmslog',
            name='status',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='\u72b6\u6001', choices=[(0, '\u5f85\u53d1\u9001'), (3, '\u53d1\u9001\u4e2d'), (1, '\u53d1\u9001\u6210\u529f'), (2, '\u53d1\u9001\u5931\u8d25')]),
        ),
        migrations.AlterField(
            model_name='userpaylog',
            name='pay_type',
            field=models.IntegerField(default=0, verbose_name='\u652f\u4ed8\u65b9\u5f0f', choices=[(0, '\u672a\u77e5'), (1, '\u7ebf\u4e0b\u652f\u4ed8'), (2, '\u5fae\u4fe1'), (3, '\u652f\u4ed8\u5b9d'), (4, '\u94f6\u8054'), (998, '\u65e0\u9700\u4ed8\u6b3e'), (999, '\u6df7\u5408\u652f\u4ed8'), (1000, '\u672a\u77e5\u652f\u4ed8\u65b9\u5f0f')]),
        ),
    ]
