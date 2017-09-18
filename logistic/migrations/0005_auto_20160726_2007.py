# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logistic', '0004_auto_20160505_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipreport',
            name='report',
            field=models.CharField(max_length=4000, null=True, verbose_name='\u7269\u6d41\u72b6\u6001\u62a5\u544a', blank=True),
        ),
    ]
