# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0004_auto_20160421_0013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enduser',
            name='avatar',
            field=models.URLField(help_text=b'\xe7\x94\xa8\xe6\x88\xb7\xe8\x87\xaa\xe5\xae\x9a\xe4\xb9\x89\xe5\xa4\xb4\xe5\x83\x8f\xef\xbc\x8c\xe4\xbc\x98\xe5\x85\x88\xe4\xba\x8e\xe7\xac\xac\xe4\xb8\x89\xe6\x96\xb9\xe5\xa4\xb4\xe5\x83\x8f\xe8\xae\xbe\xe7\xbd\xae', max_length=255, null=True, verbose_name=b'\xe5\xa4\xb4\xe5\x83\x8f', blank=True),
        ),
        migrations.AlterField(
            model_name='enduser',
            name='ex_avatar',
            field=models.URLField(help_text=b'\xe7\xac\xac\xe4\xb8\x89\xe6\x96\xb9\xe8\xb4\xa6\xe5\x8f\xb7\xe7\x9a\x84\xe5\xa4\xb4\xe5\x83\x8f\xef\xbc\x8c\xe9\x9a\x8f\xe6\x97\xb6\xe6\xa0\xb9\xe6\x8d\xae\xe7\x94\xa8\xe6\x88\xb7\xe7\x99\xbb\xe5\xbd\x95\xe6\x97\xb6\xe7\x9a\x84\xe4\xbf\xa1\xe6\x81\xaf\xe6\x9b\xb4\xe6\x96\xb0', max_length=255, null=True, verbose_name=b'\xe5\xa4\xb4\xe5\x83\x8f\xef\xbc\x88\xe7\xac\xac\xe4\xb8\x89\xe6\x96\xb9\xef\xbc\x89', blank=True),
        ),
    ]