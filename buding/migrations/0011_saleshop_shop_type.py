# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buding', '0010_auto_20170821_1017'),
    ]

    operations = [
        migrations.AddField(
            model_name='saleshop',
            name='shop_type',
            field=models.PositiveSmallIntegerField(default=0, help_text='\u5e97\u94fa\u7c7b\u578b', db_index=True, verbose_name='\u5e97\u94fa\u7c7b\u578b', choices=[(0, '\u76f4\u8425\u5e97'), (1, '\u52a0\u76df\u5e97')]),
        ),
    ]
