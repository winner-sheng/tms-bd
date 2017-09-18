# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0017_enduserenterprise_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='userorgsnapshot',
            name='overhead_rate',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='\u62bd\u6210\u6bd4\u4f8b(0-100)', validators=[django.core.validators.MaxValueValidator(80), django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='enduserenterprise',
            name='overhead_rate',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='\u62bd\u6210\u6bd4\u4f8b(0-100)', validators=[django.core.validators.MaxValueValidator(80), django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='userorgsnapshot',
            name='org_uid',
            field=models.CharField(db_index=True, max_length=32, verbose_name='\u6240\u5c5e\u7ec4\u7ec7\u7528\u6237UID', blank=True),
        ),
    ]
