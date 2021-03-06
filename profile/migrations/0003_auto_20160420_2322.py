# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0002_useraccountbook_extra_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccountbook',
            name='extra_type',
            field=models.CharField(max_length=30, null=True, verbose_name=b'\xe5\x85\xb3\xe8\x81\x94\xe5\xaf\xb9\xe8\xb1\xa1\xe7\xb1\xbb\xe5\x9e\x8b', blank=True),
        ),
        migrations.AlterField(
            model_name='useraccountbook',
            name='extra_data',
            field=models.CharField(help_text=b'\xe7\x94\xa8\xe4\xba\x8e\xe4\xbf\x9d\xe5\xad\x98\xe9\xa2\x9d\xe5\xa4\x96\xe7\x9a\x84\xe5\x85\xb3\xe8\x81\x94\xe6\x95\xb0\xe6\x8d\xae\xef\xbc\x8c\xe6\xaf\x94\xe5\xa6\x82\xe8\xae\xa2\xe5\x8d\x95\xe5\x8f\xb7\xef\xbc\x8c\xe8\xbd\xac\xe5\x87\xba\xe8\xb4\xa6\xe5\x8f\xb7\xe7\xad\x89', max_length=500, null=True, verbose_name=b'\xe8\xa1\xa5\xe5\x85\x85\xe4\xbf\xa1\xe6\x81\xaf', blank=True),
        ),
    ]
