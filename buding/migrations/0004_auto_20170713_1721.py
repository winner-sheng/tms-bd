# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buding', '0003_shopkeeperinfo_update_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='saleshop',
            name='update_time',
            field=models.DateTimeField(null=True, verbose_name='\u66f4\u65b0\u65f6\u95f4', blank=True),
        ),
        migrations.AddField(
            model_name='saleshopproduct',
            name='update_time',
            field=models.DateTimeField(null=True, verbose_name='\u66f4\u65b0\u65f6\u95f4', blank=True),
        ),
        migrations.AddField(
            model_name='shopmanagerinfo',
            name='update_time',
            field=models.DateTimeField(null=True, verbose_name='\u66f4\u65b0\u65f6\u95f4', blank=True),
        ),
    ]
