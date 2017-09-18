# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0007_auto_20161122_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appsetting',
            name='usage',
            field=models.CharField(max_length=255, null=True, verbose_name='\u914d\u7f6e\u9879\u7528\u9014', blank=True),
        ),
    ]
