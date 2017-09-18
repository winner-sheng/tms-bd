# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rewardsummary',
            name='total_cnt',
            field=models.PositiveIntegerField(default=0, help_text=b'\xe5\x8c\x85\xe5\x90\xab\xe6\x89\x80\xe6\x9c\x89\xe6\x9c\xaa\xe7\xbb\x93\xe7\xae\x97\xe3\x80\x81\xe5\xb7\xb2\xe7\xbb\x93\xe7\xae\x97\xe5\x92\x8c\xe8\xa2\xab\xe6\x92\xa4\xe9\x94\x80\xe7\x9a\x84\xe6\x94\xb6\xe7\x9b\x8a\xe8\xae\xb0\xe5\xbd\x95', null=True, verbose_name=b'\xe6\x94\xb6\xe7\x9b\x8a\xe6\x80\xbb\xe7\xac\x94\xe6\x95\xb0', blank=True),
        ),
    ]
