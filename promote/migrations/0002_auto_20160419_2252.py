# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rewardrecord',
            name='achieved_time',
            field=models.DateTimeField(null=True, verbose_name=b'\xe7\xbb\x93\xe7\xae\x97\xe6\x97\xb6\xe9\x97\xb4', blank=True),
        ),
    ]
