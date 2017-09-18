# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BaseImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('origin', models.ImageField(upload_to=b'%Y/%m/%d', verbose_name=b'\xe5\x8e\x9f\xe5\xa7\x8b\xe5\x9b\xbe\xe7\x89\x87')),
                ('image_desc', models.CharField(max_length=50, null=True, verbose_name=b'\xe5\x9b\xbe\xe7\x89\x87\xe6\x8f\x8f\xe8\xbf\xb0', blank=True)),
                ('width', models.PositiveIntegerField(verbose_name=b'\xe5\x9b\xbe\xe7\x89\x87\xe5\xae\xbd\xe5\xba\xa6', null=True, editable=False, blank=True)),
                ('height', models.PositiveIntegerField(verbose_name=b'\xe5\x9b\xbe\xe7\x89\x87\xe9\xab\x98\xe5\xba\xa6', null=True, editable=False, blank=True)),
                ('size', models.PositiveIntegerField(verbose_name=b'\xe6\x96\x87\xe4\xbb\xb6\xe5\xa4\xa7\xe5\xb0\x8f', null=True, editable=False, blank=True)),
                ('usage', models.SmallIntegerField(default=0, verbose_name=b'\xe7\x94\xa8\xe9\x80\x94(\xe5\xbc\x80\xe5\x8f\x91\xe4\xbd\xbf\xe7\x94\xa8)', choices=[(0, b'\xe9\x80\x9a\xe7\x94\xa8'), (1, b'Logo'), (2, b'\xe5\xa4\xb4\xe5\x83\x8f'), (3, b'\xe6\xa8\xaa\xe5\xb9\x85Banner'), (11, b'\xe5\xbf\xab\xe9\x80\x92\xe5\x8d\x95\xe6\xa8\xa1\xe6\x9d\xbf')])),
                ('upload_time', models.DateTimeField(auto_now_add=True, null=True, verbose_name=b'\xe4\xb8\x8a\xe4\xbc\xa0\xe6\x97\xb6\xe9\x97\xb4', db_index=True)),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': '\u56fe\u7247',
                'verbose_name_plural': '\u56fe\u7247',
            },
        ),
    ]
