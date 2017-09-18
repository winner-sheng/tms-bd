# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buding', '0006_saleshopproduct_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopmanagerinfo',
            name='reward_percent',
            field=models.PositiveSmallIntegerField(default=75, help_text='\u5206\u4f63\u767e\u5206\u6bd4\uff0c75\u8868\u793a\u4e2a\u4eba\u5f9775%\uff0c25%\u7ed9\u5e97\u957f', verbose_name='\u5206\u4f63\u767e\u5206\u6bd4'),
        ),
        migrations.AlterField(
            model_name='shopmanagerinfo',
            name='role',
            field=models.PositiveSmallIntegerField(default=0, help_text='\u804c\u4f4d', db_index=True, verbose_name='\u804c\u4f4d', choices=[(0, '\u5458\u5de5'), (1, '\u7ecf\u7406'), (2, '\u5e97\u4e3b')]),
        ),
    ]
