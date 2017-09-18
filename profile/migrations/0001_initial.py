# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

import profile.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EndUser',
            fields=[
                ('uid', models.CharField(default=profile.models._uuid, max_length=32, serialize=False, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7ID', primary_key=True)),
                ('mobile', models.CharField(max_length=15, null=True, verbose_name=b'\xe6\x89\x8b\xe6\x9c\xba', blank=True)),
                ('nick_name', models.CharField(help_text=b'\xe7\x94\xa8\xe6\x88\xb7\xe8\x87\xaa\xe5\xae\x9a\xe4\xb9\x89\xe6\x98\xb5\xe7\xa7\xb0\xef\xbc\x8c\xe4\xbc\x98\xe5\x85\x88\xe4\xba\x8e\xe7\xac\xac\xe4\xb8\x89\xe6\x96\xb9\xe6\x98\xb5\xe7\xa7\xb0\xe8\xae\xbe\xe7\xbd\xae', max_length=30, null=True, verbose_name=b'\xe6\x98\xb5\xe7\xa7\xb0', blank=True)),
                ('avatar', models.URLField(help_text=b'\xe7\x94\xa8\xe6\x88\xb7\xe8\x87\xaa\xe5\xae\x9a\xe4\xb9\x89\xe5\xa4\xb4\xe5\x83\x8f\xef\xbc\x8c\xe4\xbc\x98\xe5\x85\x88\xe4\xba\x8e\xe7\xac\xac\xe4\xb8\x89\xe6\x96\xb9\xe5\xa4\xb4\xe5\x83\x8f\xe8\xae\xbe\xe7\xbd\xae', null=True, verbose_name=b'\xe5\xa4\xb4\xe5\x83\x8f', blank=True)),
                ('ex_nick_name', models.CharField(max_length=30, null=True, verbose_name=b'\xe6\x98\xb5\xe7\xa7\xb0\xef\xbc\x88\xe7\xac\xac\xe4\xb8\x89\xe6\x96\xb9\xef\xbc\x89', blank=True)),
                ('ex_avatar', models.URLField(help_text=b'\xe7\xac\xac\xe4\xb8\x89\xe6\x96\xb9\xe8\xb4\xa6\xe5\x8f\xb7\xe7\x9a\x84\xe5\xa4\xb4\xe5\x83\x8f\xef\xbc\x8c\xe9\x9a\x8f\xe6\x97\xb6\xe6\xa0\xb9\xe6\x8d\xae\xe7\x94\xa8\xe6\x88\xb7\xe7\x99\xbb\xe5\xbd\x95\xe6\x97\xb6\xe7\x9a\x84\xe4\xbf\xa1\xe6\x81\xaf\xe6\x9b\xb4\xe6\x96\xb0', null=True, verbose_name=b'\xe5\xa4\xb4\xe5\x83\x8f\xef\xbc\x88\xe7\xac\xac\xe4\xb8\x89\xe6\x96\xb9\xef\xbc\x89', blank=True)),
                ('password', models.CharField(verbose_name=b'\xe5\xaf\x86\xe7\xa0\x81', max_length=128, null=True, editable=False, blank=True)),
                ('real_name', models.CharField(help_text=b'\xe5\xa4\x87\xe7\x94\xa8\xef\xbc\x8c\xe7\xbd\x91\xe5\xae\x89\xe5\xae\x9e\xe5\x90\x8d\xe5\x88\xb6\xe8\xa6\x81\xe6\xb1\x82', max_length=30, null=True, verbose_name=b'\xe5\xa7\x93\xe5\x90\x8d', blank=True)),
                ('id_card', models.CharField(help_text=b'\xe5\xa4\x87\xe7\x94\xa8\xef\xbc\x8c\xe7\xbd\x91\xe5\xae\x89\xe5\xae\x9e\xe5\x90\x8d\xe5\x88\xb6\xe8\xa6\x81\xe6\xb1\x82', max_length=18, null=True, verbose_name=b'\xe8\xba\xab\xe4\xbb\xbd\xe8\xaf\x81\xe5\x8f\xb7', blank=True)),
                ('gender', models.CharField(default=b'X', max_length=1, verbose_name=b'\xe6\x80\xa7\xe5\x88\xab', choices=[(b'M', b'\xe7\x94\xb7'), (b'F', b'\xe5\xa5\xb3'), (b'X', b'\xe4\xb8\x8d\xe5\x91\x8a\xe8\xaf\x89\xe4\xbd\xa0')])),
                ('status', models.SmallIntegerField(default=0, null=True, verbose_name=b'\xe7\x8a\xb6\xe6\x80\x81', blank=True, choices=[(0, b'\xe6\x9c\x89\xe6\x95\x88'), (1, b'\xe6\x97\xa0\xe6\x95\x88'), (99, b'\xe9\xbb\x91\xe5\x90\x8d\xe5\x8d\x95')])),
                ('register_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe6\xb3\xa8\xe5\x86\x8c\xe6\x97\xb6\xe9\x97\xb4')),
                ('register_ip', models.GenericIPAddressField(verbose_name=b'\xe6\xb3\xa8\xe5\x86\x8c\xe6\x97\xb6IP', null=True, editable=False, blank=True)),
                ('last_login', models.DateTimeField(null=True, verbose_name=b'\xe4\xb8\x8a\xe6\xac\xa1\xe7\x99\xbb\xe5\xbd\x95\xe6\x97\xb6\xe9\x97\xb4', blank=True)),
                ('referrer', models.CharField(max_length=36, null=True, verbose_name=b'\xe6\x8e\xa8\xe8\x8d\x90\xe4\xba\xba', blank=True)),
            ],
            options={
                'verbose_name': '\u7ec8\u7aef\u7528\u6237',
                'verbose_name_plural': '\u7ec8\u7aef\u7528\u6237',
            },
        ),
        migrations.CreateModel(
            name='EndUserExt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(max_length=32, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7UID', db_index=True)),
                ('ex_id_type', models.PositiveSmallIntegerField(default=0, verbose_name=b'\xe7\xac\xac\xe4\xb8\x89\xe6\x96\xb9\xe8\xb4\xa6\xe5\x8f\xb7\xe7\xb1\xbb\xe5\x9e\x8b', choices=[(0, b'\xe5\xbe\xae\xe4\xbf\xa1openID'), (1, b'\xe5\xbe\xae\xe4\xbf\xa1unionID'), (2, b'QQ\xe5\xbc\x80\xe6\x94\xbe\xe8\xb4\xa6\xe5\x8f\xb7ID'), (3, b'\xe6\x94\xaf\xe4\xbb\x98\xe5\xae\x9d\xe5\xbc\x80\xe6\x94\xbe\xe8\xb4\xa6\xe5\x8f\xb7ID'), (4, b'\xe5\xbe\xae\xe5\x8d\x9a\xe5\xbc\x80\xe6\x94\xbe\xe8\xb4\xa6\xe5\x8f\xb7ID'), (99, b'\xe4\xba\xa4\xe6\x98\x93\xe5\xb9\xb3\xe5\x8f\xb0\xe7\xae\xa1\xe7\x90\x86\xe8\xb4\xa6\xe5\x8f\xb7')])),
                ('ex_id', models.CharField(null=True, max_length=32, blank=True, unique=True, verbose_name=b'\xe7\xac\xac\xe4\xb8\x89\xe6\x96\xb9\xe8\xb4\xa6\xe5\x8f\xb7', db_index=True)),
                ('reg_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe6\xb3\xa8\xe5\x86\x8c\xe6\x97\xb6\xe9\x97\xb4')),
            ],
            options={
                'verbose_name': '\u7b2c\u4e09\u65b9\u8d26\u53f7',
                'verbose_name_plural': '\u7b2c\u4e09\u65b9\u8d26\u53f7',
            },
        ),
        migrations.CreateModel(
            name='ShipAddress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(max_length=32, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7UID', db_index=True)),
                ('receiver', models.CharField(max_length=30, null=True, verbose_name=b'\xe6\x94\xb6\xe4\xbb\xb6\xe4\xba\xba', blank=True)),
                ('receiver_mobile', models.CharField(max_length=20, null=True, verbose_name=b'\xe6\x94\xb6\xe4\xbb\xb6\xe4\xba\xba\xe7\x94\xb5\xe8\xaf\x9d', blank=True)),
                ('ship_province', models.CharField(max_length=3, verbose_name=b'\xe6\x94\xb6\xe4\xbb\xb6\xe7\x9c\x81\xe4\xbb\xbd', choices=[('\u5b89\u5fbd', '\u5b89\u5fbd'), ('\u6fb3\u95e8', '\u6fb3\u95e8'), ('\u5317\u4eac', '\u5317\u4eac'), ('\u91cd\u5e86', '\u91cd\u5e86'), ('\u798f\u5efa', '\u798f\u5efa'), ('\u7518\u8083', '\u7518\u8083'), ('\u5e7f\u4e1c', '\u5e7f\u4e1c'), ('\u5e7f\u897f', '\u5e7f\u897f'), ('\u8d35\u5dde', '\u8d35\u5dde'), ('\u6d77\u5357', '\u6d77\u5357'), ('\u6cb3\u5317', '\u6cb3\u5317'), ('\u6cb3\u5357', '\u6cb3\u5357'), ('\u9ed1\u9f99\u6c5f', '\u9ed1\u9f99\u6c5f'), ('\u6e56\u5317', '\u6e56\u5317'), ('\u6e56\u5357', '\u6e56\u5357'), ('\u5409\u6797', '\u5409\u6797'), ('\u6c5f\u82cf', '\u6c5f\u82cf'), ('\u6c5f\u897f', '\u6c5f\u897f'), ('\u8fbd\u5b81', '\u8fbd\u5b81'), ('\u5185\u8499\u53e4', '\u5185\u8499\u53e4'), ('\u5b81\u590f', '\u5b81\u590f'), ('\u9752\u6d77', '\u9752\u6d77'), ('\u5c71\u4e1c', '\u5c71\u4e1c'), ('\u5c71\u897f', '\u5c71\u897f'), ('\u9655\u897f', '\u9655\u897f'), ('\u4e0a\u6d77', '\u4e0a\u6d77'), ('\u56db\u5ddd', '\u56db\u5ddd'), ('\u53f0\u6e7e', '\u53f0\u6e7e'), ('\u5929\u6d25', '\u5929\u6d25'), ('\u897f\u85cf', '\u897f\u85cf'), ('\u9999\u6e2f', '\u9999\u6e2f'), ('\u65b0\u7586', '\u65b0\u7586'), ('\u4e91\u5357', '\u4e91\u5357'), ('\u6d59\u6c5f', '\u6d59\u6c5f')])),
                ('ship_city', models.CharField(max_length=10, null=True, verbose_name=b'\xe6\x94\xb6\xe4\xbb\xb6\xe5\xb8\x82', blank=True)),
                ('ship_district', models.CharField(max_length=10, null=True, verbose_name=b'\xe6\x94\xb6\xe4\xbb\xb6\xe5\x8c\xba/\xe5\x8e\xbf', blank=True)),
                ('ship_address', models.CharField(max_length=50, verbose_name=b'\xe8\xaf\xa6\xe7\xbb\x86\xe6\x94\xb6\xe4\xbb\xb6\xe5\x9c\xb0\xe5\x9d\x80')),
                ('zip_code', models.CharField(max_length=6, null=True, verbose_name=b'\xe9\x82\xae\xe7\xbc\x96', blank=True)),
                ('is_default', models.BooleanField(default=False, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe9\xbb\x98\xe8\xae\xa4\xe5\x9c\xb0\xe5\x9d\x80')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4')),
            ],
            options={
                'ordering': ['uid'],
                'verbose_name': '\u7528\u6237\u6536\u4ef6\u5730\u5740',
                'verbose_name_plural': '\u7528\u6237\u6536\u4ef6\u5730\u5740',
            },
        ),
        migrations.CreateModel(
            name='TmsUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(help_text=b'\xe8\xaf\xa5\xe5\xb1\x9e\xe6\x80\xa7\xe7\x94\xa8\xe4\xba\x8e\xe4\xb8\x8e\xe7\xbb\x88\xe7\xab\xaf\xe7\x94\xa8\xe6\x88\xb7\xe7\xbb\x91\xe5\xae\x9a\xef\xbc\x8c\xe4\xbd\xbf\xe5\xbe\x97\xe7\xbb\x88\xe7\xab\xaf\xe7\x94\xa8\xe6\x88\xb7\xe4\xb9\x9f\xe5\x8f\xaf\xe7\x99\xbb\xe5\xbd\x95', max_length=32, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7UID', db_index=True)),
                ('mobile', models.CharField(help_text=b'\xe7\xae\xa1\xe7\x90\x86\xe7\x94\xa8\xe6\x88\xb7\xe7\xbb\x91\xe5\xae\x9a\xe6\x89\x8b\xe6\x9c\xba\xe5\x8f\xb7', max_length=15, null=True, verbose_name=b'\xe6\x89\x8b\xe6\x9c\xba', blank=True)),
                ('user', models.OneToOneField(verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7', to=settings.AUTH_USER_MODEL, help_text=b'\xe5\x90\x8e\xe5\x8f\xb0\xe7\xae\xa1\xe7\x90\x86\xe7\x94\xa8\xe6\x88\xb7')),
            ],
        ),
        migrations.CreateModel(
            name='UserAccountBook',
            fields=[
                ('account_no', models.CharField(default=profile.models._get_account_no, max_length=32, serialize=False, verbose_name=b'\xe6\xb5\x81\xe6\xb0\xb4\xe5\x8f\xb7', primary_key=True)),
                ('uid', models.CharField(max_length=32, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7UID', db_index=True)),
                ('figure', models.DecimalField(default=0, help_text=b'\xe5\x87\xba/\xe5\x85\xa5\xe8\xb4\xa6\xe5\x9d\x87\xe8\xae\xa1\xe5\x85\xa5\xe6\xad\xa4\xe6\xa0\x8f\xef\xbc\x8c\xe6\xad\xa3\xe5\x80\xbc\xe8\xa1\xa8\xe7\xa4\xba\xe6\x94\xb6\xe5\x85\xa5\xef\xbc\x8c\xe8\xb4\x9f\xe5\x80\xbc\xe8\xa1\xa8\xe7\xa4\xba\xe6\x94\xaf\xe5\x87\xba', verbose_name=b'\xe5\x85\xa5\xe8\xb4\xa6\xe9\x87\x91\xe9\xa2\x9d', max_digits=10, decimal_places=2)),
                ('is_income', models.BooleanField(default=True, help_text=b'\xe5\xa6\x82\xe6\x9e\x9c\xe6\x98\xaf\xe6\x94\xaf\xe5\x87\xba\xef\xbc\x8c\xe5\xba\x94\xe8\xae\xbe\xe4\xb8\xbaFalse', verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe6\x94\xb6\xe5\x85\xa5')),
                ('type', models.CharField(default=b'other', max_length=10, verbose_name=b'\xe8\xb4\xa6\xe7\x9b\xae\xe7\xb1\xbb\xe5\x88\xab', choices=[(b'bonus', b'\xe5\xa5\x96\xe5\x8a\xb1'), (b'charge', b'\xe5\x85\x85\xe5\x80\xbc'), (b'expense', b'\xe6\xb6\x88\xe8\xb4\xb9\xe6\x94\xaf\xe5\x87\xba'), (b'penalty', b'\xe7\xbd\x9a\xe6\xac\xbe'), (b'reward', b'\xe5\x9b\x9e\xe4\xbd\xa3'), (b'roll-in', b'\xe8\xbd\xac\xe5\x85\xa5'), (b'roll-out', b'\xe8\xbd\xac\xe5\x87\xba'), (b'withdraw', b'\xe6\x8f\x90\xe7\x8e\xb0'), (b'other', b'\xe5\x85\xb6\xe5\xae\x83')])),
                ('account_desc', models.CharField(max_length=200, null=True, verbose_name=b'\xe8\xb4\xa6\xe7\x9b\xae\xe8\xaf\xb4\xe6\x98\x8e', blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True)),
            ],
            options={
                'verbose_name': '\u7528\u6237\u51fa\u5165\u8d26\u8bb0\u5f55',
                'verbose_name_plural': '\u7528\u6237\u51fa\u5165\u8d26\u8bb0\u5f55',
            },
        ),
        migrations.CreateModel(
            name='UserFavorite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(max_length=32, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7UID', db_index=True)),
                ('favor_type', models.PositiveIntegerField(default=0, verbose_name=b'\xe5\x85\xb3\xe6\xb3\xa8\xe7\xb1\xbb\xe5\x9e\x8b', choices=[(0, b'\xe6\x94\xb6\xe8\x97\x8f')])),
                ('entity_type', models.CharField(max_length=2, verbose_name=b'\xe5\x85\xb3\xe6\xb3\xa8\xe5\xaf\xb9\xe8\xb1\xa1\xe7\xb1\xbb\xe5\x9e\x8b', choices=[(b'P', b'\xe5\x95\x86\xe5\x93\x81')])),
                ('entity_id', models.IntegerField(verbose_name=b'\xe5\x85\xb3\xe6\xb3\xa8\xe5\xaf\xb9\xe8\xb1\xa1ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x85\xb3\xe6\xb3\xa8\xe6\x97\xb6\xe9\x97\xb4')),
            ],
            options={
                'ordering': ('-create_time',),
                'verbose_name': '\u7528\u6237\u5173\u6ce8\u5217\u8868',
                'verbose_name_plural': '\u7528\u6237\u5173\u6ce8\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='UserHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(max_length=32, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7UID', db_index=True)),
                ('entity_type', models.CharField(max_length=2, verbose_name=b'\xe8\xae\xbf\xe9\x97\xae\xe5\xaf\xb9\xe8\xb1\xa1\xe7\xb1\xbb\xe5\x9e\x8b', choices=[(b'P', b'\xe5\x95\x86\xe5\x93\x81'), (b'KW', b'\xe6\x90\x9c\xe7\xb4\xa2')])),
                ('entity_id', models.IntegerField(default=0, null=True, verbose_name=b'\xe8\xae\xbf\xe9\x97\xae\xe5\xaf\xb9\xe8\xb1\xa1ID', blank=True)),
                ('entity_value', models.CharField(help_text=b'\xe4\xb8\xbb\xe8\xa6\x81\xe7\x94\xa8\xe4\xba\x8e\xe4\xbf\x9d\xe5\xad\x98\xe7\x94\xa8\xe6\x88\xb7\xe6\x90\x9c\xe7\xb4\xa2\xe7\x9a\x84\xe5\x85\xb3\xe9\x94\xae\xe8\xaf\x8d\xe5\x8e\x86\xe5\x8f\xb2', max_length=20, null=True, verbose_name=b'\xe8\xae\xbf\xe9\x97\xae\xe5\xaf\xb9\xe8\xb1\xa1\xe5\x80\xbc', blank=True)),
                ('update_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe8\xae\xbf\xe9\x97\xae\xe6\x97\xb6\xe9\x97\xb4')),
            ],
            options={
                'ordering': ('-update_time',),
                'verbose_name': '\u7528\u6237\u8bbf\u95ee\u5386\u53f2',
                'verbose_name_plural': '\u7528\u6237\u8bbf\u95ee\u5386\u53f2',
            },
        ),
    ]
