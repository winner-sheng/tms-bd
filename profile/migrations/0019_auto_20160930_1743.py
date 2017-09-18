# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0018_auto_20160908_1101'),
    ]

    operations = [
        migrations.AddField(
            model_name='enduserenterprise',
            name='ent_type',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='\u4f01\u4e1a\u7c7b\u578b'),
        ),
        migrations.AlterField(
            model_name='enduserenterprise',
            name='overhead_rate',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='\u62bd\u6210\u6bd4\u4f8b(0-80%)', validators=[django.core.validators.MaxValueValidator(80), django.core.validators.MinValueValidator(0)]),
        ),
    ]
