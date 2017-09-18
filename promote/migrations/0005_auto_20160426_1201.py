# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import promote.models


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0004_auto_20160425_2337'),
    ]

    operations = [
        migrations.AddField(
            model_name='couponrule',
            name='update_by',
            field=models.CharField(verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe4\xba\xba', max_length=32, null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='couponrule',
            name='update_time',
            field=models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4', null=True),
        ),
        migrations.AlterField(
            model_name='couponrule',
            name='code',
            field=models.CharField(primary_key=True, default=promote.models._activity_code, serialize=False, max_length=12, help_text=b'\xe7\x94\xa8\xe4\xba\x8e\xe5\xbc\x95\xe7\x94\xa8', verbose_name=b'\xe6\xb4\xbb\xe5\x8a\xa8\xe7\xbc\x96\xe7\xa0\x81'),
        ),
        migrations.AlterField(
            model_name='couponrule',
            name='create_by',
            field=models.CharField(verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe4\xba\xba', max_length=32, null=True, editable=False, blank=True),
        ),
    ]
