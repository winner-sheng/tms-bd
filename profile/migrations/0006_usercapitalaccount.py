# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0005_auto_20160423_2044'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCapitalAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(max_length=32, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7UID', db_index=True)),
                ('ca_no', models.CharField(unique=True, max_length=32, verbose_name=b'\xe8\xb5\x84\xe9\x87\x91\xe5\xb8\x90\xe5\x8f\xb7')),
                ('ca_type', models.CharField(default=b'bank', max_length=10, verbose_name=b'\xe8\xb4\xa6\xe5\x8f\xb7\xe7\xb1\xbb\xe5\x88\xab', choices=[(b'alipay', '\u652f\u4ed8\u5b9d'), (b'bank', '\u50a8\u84c4\u5361'), (b'credit', '\u4fe1\u7528\u5361'), (b'other', '\u5176\u5b83')])),
                ('ca_desc', models.CharField(max_length=200, null=True, verbose_name=b'\xe8\xb4\xa6\xe5\x8f\xb7\xe8\xaf\xb4\xe6\x98\x8e', blank=True)),
                ('bank_name', models.CharField(max_length=30, null=True, verbose_name=b'\xe9\x93\xb6\xe8\xa1\x8c\xe5\x90\x8d\xe7\xa7\xb0', blank=True)),
                ('bank_code', models.CharField(max_length=20, null=True, verbose_name=b'\xe9\x93\xb6\xe8\xa1\x8c\xe7\xbc\x96\xe7\xa0\x81', blank=True)),
                ('open_bank', models.CharField(max_length=50, null=True, verbose_name=b'\xe5\xbc\x80\xe6\x88\xb7\xe8\xa1\x8c\xe5\x90\x8d\xe7\xa7\xb0', blank=True)),
                ('is_valid', models.BooleanField(default=False, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe9\xaa\x8c\xe8\xaf\x81\xe6\x9c\x89\xe6\x95\x88')),
                ('is_default', models.BooleanField(default=False, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe9\xbb\x98\xe8\xae\xa4\xe8\xb4\xa6\xe5\x8f\xb7')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True)),
            ],
            options={
                'verbose_name': '\u7528\u6237\u8d44\u91d1\u8d26\u53f7',
                'verbose_name_plural': '\u7528\u6237\u8d44\u91d1\u8d26\u53f7',
            },
        ),
    ]
