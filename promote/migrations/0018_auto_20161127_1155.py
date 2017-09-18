# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0017_auto_20161124_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='couponticket',
            name='get_time',
            field=models.DateTimeField(db_index=True, null=True, verbose_name='\u9886\u53d6\u65f6\u95f4', blank=True),
        ),
    ]
