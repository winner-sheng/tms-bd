# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0002_auto_20160419_2333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasklog',
            name='exec_result',
            field=models.CharField(max_length=255, null=True, verbose_name=b'\xe6\x89\xa7\xe8\xa1\x8c\xe7\xbb\x93\xe6\x9e\x9c', blank=True),
        ),
    ]
