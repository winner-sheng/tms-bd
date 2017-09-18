# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0022_auto_20170505_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='withdrawrequest',
            name='status',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='\u63d0\u73b0\u7ed3\u679c', choices=[(0, '\u5904\u7406\u4e2d'), (1, '\u5b8c\u6210'), (2, '\u63d0\u73b0\u5931\u8d25'), (3, '\u5f85\u5ba1\u6838'), (4, '\u5f85\u786e\u8ba4'), (5, '\u5df2\u786e\u8ba4')]),
        ),
    ]
