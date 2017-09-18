# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0006_auto_20160426_1248'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='couponticket',
            name='status',
        ),
        migrations.AlterField(
            model_name='couponrule',
            name='threshold',
            field=models.PositiveIntegerField(default=0, help_text=b'\xe8\xae\xa2\xe5\x8d\x95\xe6\x9c\x80\xe5\xb0\x8f\xe8\xb4\xad\xe7\x89\xa9\xe9\x87\x91\xe9\xa2\x9d\xe9\x99\x90\xe5\x88\xb6(\xe5\x85\x83)\xef\xbc\x8c0\xe8\xa1\xa8\xe7\xa4\xba\xe4\xb8\x8d\xe9\x99\x90', null=True, verbose_name=b'\xe8\xb4\xad\xe7\x89\xa9\xe9\x87\x91\xe9\xa2\x9d\xe9\x99\x90\xe5\x88\xb6(\xe5\x85\x83)', blank=True),
        ),
        migrations.AlterField(
            model_name='couponticket',
            name='consume_time',
            field=models.DateTimeField(null=True, verbose_name=b'\xe6\xb6\x88\xe8\xb4\xb9\xe6\x97\xb6\xe9\x97\xb4', blank=True),
        ),
        migrations.AlterField(
            model_name='couponticket',
            name='consumer',
            field=models.CharField(help_text=b'\xe5\x8d\xb3\xe6\x9c\x80\xe7\xbb\x88\xe8\xaf\xa5\xe4\xbc\x98\xe6\x83\xa0\xe5\x88\xb8\xe7\x9a\x84\xe4\xbd\xbf\xe7\x94\xa8\xe4\xba\xba', max_length=32, null=True, verbose_name=b'\xe9\xa2\x86\xe7\x94\xa8\xe4\xba\xbaUID', blank=True),
        ),
        migrations.AlterField(
            model_name='couponticket',
            name='dispatcher',
            field=models.CharField(help_text=b'\xe5\xa4\x87\xe7\x94\xa8\xef\xbc\x8c\xe7\x94\xa8\xe4\xba\x8e\xe7\x89\xb9\xe6\xae\x8a\xe8\xa7\x92\xe8\x89\xb2\xef\xbc\x8c\xe5\x8d\xb3\xe8\x8e\xb7\xe5\x8f\x96\xe4\xbc\x98\xe6\x83\xa0\xe5\x88\xb8\xef\xbc\x8c\xe6\x8f\x90\xe4\xbe\x9b\xe7\xbb\x99\xe4\xbb\x96\xe4\xba\xba\xe4\xbd\xbf\xe7\x94\xa8\xe7\x9a\x84\xe7\x94\xa8\xe6\x88\xb7', max_length=32, null=True, verbose_name=b'\xe5\x88\x86\xe5\x8f\x91\xe4\xba\xbaUID', blank=True),
        ),
        migrations.AlterField(
            model_name='couponticket',
            name='get_time',
            field=models.DateTimeField(null=True, verbose_name=b'\xe9\xa2\x86\xe5\x8f\x96\xe6\x97\xb6\xe9\x97\xb4', blank=True),
        ),
        migrations.AlterField(
            model_name='couponticket',
            name='order_no',
            field=models.CharField(max_length=20, null=True, verbose_name=b'\xe6\xb6\x88\xe8\xb4\xb9\xe8\xae\xa2\xe5\x8d\x95\xe5\x8f\xb7', blank=True),
        ),
    ]
