# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filemgmt', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseimage',
            name='usage',
            field=models.SmallIntegerField(default=0, verbose_name=b'\xe7\x94\xa8\xe9\x80\x94(\xe5\xbc\x80\xe5\x8f\x91\xe4\xbd\xbf\xe7\x94\xa8)', choices=[(0, b'\xe9\x80\x9a\xe7\x94\xa8'), (1, b'Logo'), (2, b'\xe5\xa4\xb4\xe5\x83\x8f'), (3, b'\xe6\xa8\xaa\xe5\xb9\x85Banner'), (4, b'\xe5\x9b\xbe\xe6\xa0\x87'), (11, b'\xe5\xbf\xab\xe9\x80\x92\xe5\x8d\x95\xe6\xa8\xa1\xe6\x9d\xbf')]),
        ),
    ]
