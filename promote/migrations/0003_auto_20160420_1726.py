# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0002_auto_20160419_2252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rewardrecord',
            name='account_no',
            field=models.CharField(help_text=b'\xe5\xb7\xb2\xe7\xbb\x93\xe7\xae\x97\xe6\x94\xb6\xe7\x9b\x8a\xe5\xbf\x85\xe9\xa1\xbb\xe6\x9c\x89\xe6\xb5\x81\xe6\xb0\xb4\xe5\x8f\xb7\xe5\x90\x8e\xef\xbc\x8c\xe6\x89\x8d\xe6\x84\x8f\xe5\x91\xb3\xe7\x9d\x80\xe8\xaf\xa5\xe6\x94\xb6\xe7\x9b\x8a\xe5\x88\xb0\xe8\xb4\xa6', max_length=32, null=True, verbose_name=b'\xe6\xb5\x81\xe6\xb0\xb4\xe5\x8f\xb7', blank=True),
        ),
    ]
