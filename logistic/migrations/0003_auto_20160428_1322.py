# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logistic', '0002_auto_20160419_2245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipreport',
            name='ship_code',
            field=models.CharField(db_index=True, max_length=20, null=True, verbose_name=b'\xe7\x89\xa9\xe6\xb5\x81\xe5\x8d\x95\xe5\x8f\xb7', blank=True),
        ),
        migrations.AlterField(
            model_name='shipreport',
            name='vendor_code',
            field=models.CharField(max_length=16, verbose_name=b'\xe7\x89\xa9\xe6\xb5\x81\xe5\x85\xac\xe5\x8f\xb8\xe7\xbc\x96\xe7\xa0\x81', db_index=True),
        ),
        migrations.AlterUniqueTogether(
            name='shipreport',
            unique_together=set([]),
        ),
    ]
