# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0005_auto_20160426_1201'),
    ]

    operations = [
        migrations.AddField(
            model_name='couponticket',
            name='is_expired',
            field=models.BooleanField(default=False, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe8\xbf\x87\xe6\x9c\x9f'),
        ),
        migrations.AlterField(
            model_name='couponticket',
            name='status',
            field=models.PositiveIntegerField(default=0, verbose_name=b'\xe7\x8a\xb6\xe6\x80\x81', choices=[(0, b'\xe6\x9c\xaa\xe9\xa2\x86\xe5\x8f\x96'), (1, b'\xe5\xb7\xb2\xe9\xa2\x86\xe5\x8f\x96'), (2, b'\xe5\xb7\xb2\xe6\xb6\x88\xe8\xb4\xb9')]),
        ),
        migrations.AlterField(
            model_name='couponrule',
            name='threshold',
            field=models.PositiveIntegerField(default=0, help_text=b'\xe8\xae\xa2\xe5\x8d\x95\xe6\x9c\x80\xe5\xb0\x8f\xe8\xb4\xad\xe7\x89\xa9\xe9\x87\x91\xe9\xa2\x9d\xe9\x99\x90\xe5\x88\xb6(\xe5\x85\x83)', null=True, verbose_name=b'\xe8\xb4\xad\xe7\x89\xa9\xe9\x87\x91\xe9\xa2\x9d\xe9\x99\x90\xe5\x88\xb6(\xe5\x85\x83)', blank=True),
        ),
        migrations.AlterField(
            model_name='rewardrecord',
            name='achieved',
            field=models.DecimalField(default=0, help_text=b'\xe4\xb8\xba\xe8\xae\xa2\xe5\x8d\x95\xe7\xbb\x93\xe7\xae\x97\xe5\xae\x8c\xe6\x88\x90\xe5\x90\x8e\xe5\xae\x9e\xe9\x99\x85\xe5\x88\xb0\xe8\xb4\xa6\xe9\x87\x91\xe9\xa2\x9d', verbose_name=b'\xe5\xb7\xb2\xe7\xbb\x93\xe7\xae\x97\xe6\x94\xb6\xe7\x9b\x8a', max_digits=10, decimal_places=2),
        ),
    ]
