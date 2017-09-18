# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='logisticsvendor',
            name='create_by',
            field=models.IntegerField(verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe4\xba\xba', null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='logisticsvendor',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True),
        ),
        migrations.AddField(
            model_name='logisticsvendor',
            name='update_by',
            field=models.IntegerField(verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe4\xba\xba', null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='logisticsvendor',
            name='update_time',
            field=models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4', null=True),
        ),
        migrations.AddField(
            model_name='manufacturer',
            name='create_by',
            field=models.IntegerField(verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe4\xba\xba', null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='manufacturer',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True),
        ),
        migrations.AddField(
            model_name='manufacturer',
            name='update_by',
            field=models.IntegerField(verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe4\xba\xba', null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='manufacturer',
            name='update_time',
            field=models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4', null=True),
        ),
        migrations.AddField(
            model_name='store',
            name='create_by',
            field=models.IntegerField(verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe4\xba\xba', null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='store',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True),
        ),
        migrations.AddField(
            model_name='store',
            name='update_by',
            field=models.IntegerField(verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe4\xba\xba', null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='store',
            name='update_time',
            field=models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4', null=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='create_by',
            field=models.IntegerField(verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe4\xba\xba', null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='update_by',
            field=models.IntegerField(verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe4\xba\xba', null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='update_time',
            field=models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4', null=True),
        ),
    ]
