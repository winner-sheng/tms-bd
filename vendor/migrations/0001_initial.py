# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import util.renderutil
import django.db.models.deletion
from django.conf import settings
import ueditor.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('filemgmt', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, unique=True, null=True, verbose_name=b'\xe8\x81\x94\xe7\xb3\xbb\xe4\xba\xba', blank=True)),
                ('mobile', models.CharField(max_length=13, null=True, verbose_name=b'\xe6\x89\x8b\xe6\x9c\xba', blank=True)),
                ('phone', models.CharField(max_length=15, null=True, verbose_name=b'\xe5\x9b\xba\xe5\xae\x9a\xe7\x94\xb5\xe8\xaf\x9d', blank=True)),
                ('qq', models.CharField(max_length=15, null=True, verbose_name=b'QQ', blank=True)),
                ('wechat', models.CharField(max_length=30, null=True, verbose_name=b'\xe5\xbe\xae\xe4\xbf\xa1', blank=True)),
                ('email', models.EmailField(max_length=60, null=True, verbose_name=b'Email', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': '\u5546\u5bb6-\u8054\u7cfb\u4eba',
                'verbose_name_plural': '\u5546\u5bb6-\u8054\u7cfb\u4eba',
            },
        ),
        migrations.CreateModel(
            name='LogisticsVendor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(default=util.renderutil.random_code, help_text=b'\xe5\x8f\xaf\xe8\x87\xaa\xe5\x8a\xa8\xe7\x94\x9f\xe6\x88\x90\xef\xbc\x8c\xe5\xbb\xba\xe8\xae\xae\xe7\xbb\x9f\xe4\xb8\x80\xe4\xbd\xbf\xe7\x94\xa8\xe7\x94\xa8\xe6\x8b\xbc\xe9\x9f\xb3\xe9\xa6\x96\xe5\xad\x97\xe6\xaf\x8d\xe4\xbd\x9c\xe4\xb8\xba\xe7\xbc\x96\xe7\xa0\x81', unique=True, max_length=32, verbose_name=b'\xe7\xbc\x96\xe7\xa0\x81')),
                ('name', models.CharField(unique=True, max_length=50, verbose_name=b'\xe5\x90\x8d\xe7\xa7\xb0')),
                ('intro', ueditor.models.UEditorField(max_length=10000, null=True, verbose_name=b'\xe7\xae\x80\xe4\xbb\x8b', blank=True)),
                ('homepage', models.URLField(null=True, verbose_name=b'\xe7\xbd\x91\xe5\x9d\x80(http://)', blank=True)),
                ('province', models.CharField(max_length=10, null=True, verbose_name=b'\xe6\x89\x80\xe5\x9c\xa8\xe7\x9c\x81/\xe7\x9b\xb4\xe8\xbe\x96\xe5\xb8\x82/\xe8\x87\xaa\xe6\xb2\xbb\xe5\x8c\xba', blank=True)),
                ('city', models.CharField(max_length=10, null=True, verbose_name=b'\xe6\x89\x80\xe5\x9c\xa8\xe5\x9f\x8e\xe5\xb8\x82', blank=True)),
                ('address', models.CharField(max_length=100, null=True, verbose_name=b'\xe5\x9c\xb0\xe5\x9d\x80', blank=True)),
                ('post_code', models.CharField(max_length=8, null=True, verbose_name=b'\xe9\x82\xae\xe7\xbc\x96', blank=True)),
                ('longitude', models.FloatField(default=0, null=True, verbose_name=b'\xe7\xbb\x8f\xe5\xba\xa6', blank=True)),
                ('latitude', models.FloatField(default=0, null=True, verbose_name=b'\xe7\xba\xac\xe5\xba\xa6', blank=True)),
                ('geo_hash', models.CharField(db_index=True, max_length=16, null=True, editable=False, blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe6\x9c\x89\xe6\x95\x88')),
                ('is_verified', models.BooleanField(default=True, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe5\xb7\xb2\xe8\xae\xa4\xe8\xaf\x81')),
                ('backup_contact', models.ForeignKey(related_name='backup_contact+', verbose_name=b'\xe5\xa4\x87\xe8\x81\x94\xe7\xb3\xbb\xe4\xba\xba', blank=True, to='vendor.Contact', null=True)),
                ('logo', models.ForeignKey(related_name='company_logo+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='filemgmt.BaseImage', null=True)),
                ('primary_contact', models.ForeignKey(related_name='primary_contact+', verbose_name=b'\xe4\xb8\xbb\xe8\x81\x94\xe7\xb3\xbb\xe4\xba\xba', blank=True, to='vendor.Contact', null=True)),
            ],
            options={
                'ordering': ['-is_active', 'code'],
                'verbose_name': '\u5546\u5bb6-\u7269\u6d41\u670d\u52a1\u5546',
                'verbose_name_plural': '\u5546\u5bb6-\u7269\u6d41\u670d\u52a1\u5546',
            },
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(default=util.renderutil.random_code, help_text=b'\xe5\x8f\xaf\xe8\x87\xaa\xe5\x8a\xa8\xe7\x94\x9f\xe6\x88\x90\xef\xbc\x8c\xe5\xbb\xba\xe8\xae\xae\xe7\xbb\x9f\xe4\xb8\x80\xe4\xbd\xbf\xe7\x94\xa8\xe7\x94\xa8\xe6\x8b\xbc\xe9\x9f\xb3\xe9\xa6\x96\xe5\xad\x97\xe6\xaf\x8d\xe4\xbd\x9c\xe4\xb8\xba\xe7\xbc\x96\xe7\xa0\x81', unique=True, max_length=32, verbose_name=b'\xe7\xbc\x96\xe7\xa0\x81')),
                ('name', models.CharField(unique=True, max_length=50, verbose_name=b'\xe5\x90\x8d\xe7\xa7\xb0')),
                ('intro', ueditor.models.UEditorField(max_length=10000, null=True, verbose_name=b'\xe7\xae\x80\xe4\xbb\x8b', blank=True)),
                ('homepage', models.URLField(null=True, verbose_name=b'\xe7\xbd\x91\xe5\x9d\x80(http://)', blank=True)),
                ('province', models.CharField(max_length=10, null=True, verbose_name=b'\xe6\x89\x80\xe5\x9c\xa8\xe7\x9c\x81/\xe7\x9b\xb4\xe8\xbe\x96\xe5\xb8\x82/\xe8\x87\xaa\xe6\xb2\xbb\xe5\x8c\xba', blank=True)),
                ('city', models.CharField(max_length=10, null=True, verbose_name=b'\xe6\x89\x80\xe5\x9c\xa8\xe5\x9f\x8e\xe5\xb8\x82', blank=True)),
                ('address', models.CharField(max_length=100, null=True, verbose_name=b'\xe5\x9c\xb0\xe5\x9d\x80', blank=True)),
                ('post_code', models.CharField(max_length=8, null=True, verbose_name=b'\xe9\x82\xae\xe7\xbc\x96', blank=True)),
                ('longitude', models.FloatField(default=0, null=True, verbose_name=b'\xe7\xbb\x8f\xe5\xba\xa6', blank=True)),
                ('latitude', models.FloatField(default=0, null=True, verbose_name=b'\xe7\xba\xac\xe5\xba\xa6', blank=True)),
                ('geo_hash', models.CharField(db_index=True, max_length=16, null=True, editable=False, blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe6\x9c\x89\xe6\x95\x88')),
                ('is_verified', models.BooleanField(default=True, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe5\xb7\xb2\xe8\xae\xa4\xe8\xaf\x81')),
                ('backup_contact', models.ForeignKey(related_name='backup_contact+', verbose_name=b'\xe5\xa4\x87\xe8\x81\x94\xe7\xb3\xbb\xe4\xba\xba', blank=True, to='vendor.Contact', null=True)),
                ('logo', models.ForeignKey(related_name='company_logo+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='filemgmt.BaseImage', null=True)),
                ('primary_contact', models.ForeignKey(related_name='primary_contact+', verbose_name=b'\xe4\xb8\xbb\xe8\x81\x94\xe7\xb3\xbb\xe4\xba\xba', blank=True, to='vendor.Contact', null=True)),
            ],
            options={
                'ordering': ['code'],
                'verbose_name': '\u5546\u5bb6-\u751f\u4ea7\u5382\u5bb6',
                'verbose_name_plural': '\u5546\u5bb6-\u751f\u4ea7\u5382\u5bb6',
            },
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(default=util.renderutil.random_code, help_text=b'\xe5\x8f\xaf\xe8\x87\xaa\xe5\x8a\xa8\xe7\x94\x9f\xe6\x88\x90\xef\xbc\x8c\xe5\xbb\xba\xe8\xae\xae\xe7\xbb\x9f\xe4\xb8\x80\xe4\xbd\xbf\xe7\x94\xa8\xe7\x94\xa8\xe6\x8b\xbc\xe9\x9f\xb3\xe9\xa6\x96\xe5\xad\x97\xe6\xaf\x8d\xe4\xbd\x9c\xe4\xb8\xba\xe7\xbc\x96\xe7\xa0\x81', unique=True, max_length=32, verbose_name=b'\xe7\xbc\x96\xe7\xa0\x81')),
                ('name', models.CharField(unique=True, max_length=50, verbose_name=b'\xe5\x90\x8d\xe7\xa7\xb0')),
                ('intro', ueditor.models.UEditorField(max_length=10000, null=True, verbose_name=b'\xe7\xae\x80\xe4\xbb\x8b', blank=True)),
                ('homepage', models.URLField(null=True, verbose_name=b'\xe7\xbd\x91\xe5\x9d\x80(http://)', blank=True)),
                ('province', models.CharField(max_length=10, null=True, verbose_name=b'\xe6\x89\x80\xe5\x9c\xa8\xe7\x9c\x81/\xe7\x9b\xb4\xe8\xbe\x96\xe5\xb8\x82/\xe8\x87\xaa\xe6\xb2\xbb\xe5\x8c\xba', blank=True)),
                ('city', models.CharField(max_length=10, null=True, verbose_name=b'\xe6\x89\x80\xe5\x9c\xa8\xe5\x9f\x8e\xe5\xb8\x82', blank=True)),
                ('address', models.CharField(max_length=100, null=True, verbose_name=b'\xe5\x9c\xb0\xe5\x9d\x80', blank=True)),
                ('post_code', models.CharField(max_length=8, null=True, verbose_name=b'\xe9\x82\xae\xe7\xbc\x96', blank=True)),
                ('longitude', models.FloatField(default=0, null=True, verbose_name=b'\xe7\xbb\x8f\xe5\xba\xa6', blank=True)),
                ('latitude', models.FloatField(default=0, null=True, verbose_name=b'\xe7\xba\xac\xe5\xba\xa6', blank=True)),
                ('geo_hash', models.CharField(db_index=True, max_length=16, null=True, editable=False, blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe6\x9c\x89\xe6\x95\x88')),
                ('is_verified', models.BooleanField(default=True, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe5\xb7\xb2\xe8\xae\xa4\xe8\xaf\x81')),
                ('backup_contact', models.ForeignKey(related_name='backup_contact+', verbose_name=b'\xe5\xa4\x87\xe8\x81\x94\xe7\xb3\xbb\xe4\xba\xba', blank=True, to='vendor.Contact', null=True)),
                ('logo', models.ForeignKey(related_name='company_logo+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='filemgmt.BaseImage', null=True)),
                ('primary_contact', models.ForeignKey(related_name='primary_contact+', verbose_name=b'\xe4\xb8\xbb\xe8\x81\x94\xe7\xb3\xbb\xe4\xba\xba', blank=True, to='vendor.Contact', null=True)),
            ],
            options={
                'ordering': ['code'],
                'verbose_name': '\u95e8\u5e97',
                'verbose_name_plural': '\u95e8\u5e97',
            },
        ),
        migrations.CreateModel(
            name='StoreAgent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('store', models.ForeignKey(verbose_name=b'\xe9\x97\xa8\xe5\xba\x97', to='vendor.Store')),
                ('user', models.OneToOneField(verbose_name=b'\xe5\x89\x8d\xe5\x8f\xb0\xe7\x94\xa8\xe6\x88\xb7', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u95e8\u5e97-\u524d\u53f0\u7528\u6237',
                'verbose_name_plural': '\u95e8\u5e97-\u524d\u53f0\u7528\u6237',
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(default=util.renderutil.random_code, help_text=b'\xe5\x8f\xaf\xe8\x87\xaa\xe5\x8a\xa8\xe7\x94\x9f\xe6\x88\x90\xef\xbc\x8c\xe5\xbb\xba\xe8\xae\xae\xe7\xbb\x9f\xe4\xb8\x80\xe4\xbd\xbf\xe7\x94\xa8\xe7\x94\xa8\xe6\x8b\xbc\xe9\x9f\xb3\xe9\xa6\x96\xe5\xad\x97\xe6\xaf\x8d\xe4\xbd\x9c\xe4\xb8\xba\xe7\xbc\x96\xe7\xa0\x81', unique=True, max_length=32, verbose_name=b'\xe7\xbc\x96\xe7\xa0\x81')),
                ('name', models.CharField(unique=True, max_length=50, verbose_name=b'\xe5\x90\x8d\xe7\xa7\xb0')),
                ('intro', ueditor.models.UEditorField(max_length=10000, null=True, verbose_name=b'\xe7\xae\x80\xe4\xbb\x8b', blank=True)),
                ('homepage', models.URLField(null=True, verbose_name=b'\xe7\xbd\x91\xe5\x9d\x80(http://)', blank=True)),
                ('province', models.CharField(max_length=10, null=True, verbose_name=b'\xe6\x89\x80\xe5\x9c\xa8\xe7\x9c\x81/\xe7\x9b\xb4\xe8\xbe\x96\xe5\xb8\x82/\xe8\x87\xaa\xe6\xb2\xbb\xe5\x8c\xba', blank=True)),
                ('city', models.CharField(max_length=10, null=True, verbose_name=b'\xe6\x89\x80\xe5\x9c\xa8\xe5\x9f\x8e\xe5\xb8\x82', blank=True)),
                ('address', models.CharField(max_length=100, null=True, verbose_name=b'\xe5\x9c\xb0\xe5\x9d\x80', blank=True)),
                ('post_code', models.CharField(max_length=8, null=True, verbose_name=b'\xe9\x82\xae\xe7\xbc\x96', blank=True)),
                ('longitude', models.FloatField(default=0, null=True, verbose_name=b'\xe7\xbb\x8f\xe5\xba\xa6', blank=True)),
                ('latitude', models.FloatField(default=0, null=True, verbose_name=b'\xe7\xba\xac\xe5\xba\xa6', blank=True)),
                ('geo_hash', models.CharField(db_index=True, max_length=16, null=True, editable=False, blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe6\x9c\x89\xe6\x95\x88')),
                ('is_verified', models.BooleanField(default=True, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe5\xb7\xb2\xe8\xae\xa4\xe8\xaf\x81')),
                ('backup_contact', models.ForeignKey(related_name='backup_contact+', verbose_name=b'\xe5\xa4\x87\xe8\x81\x94\xe7\xb3\xbb\xe4\xba\xba', blank=True, to='vendor.Contact', null=True)),
                ('logo', models.ForeignKey(related_name='company_logo+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='filemgmt.BaseImage', null=True)),
                ('primary_contact', models.ForeignKey(related_name='primary_contact+', verbose_name=b'\xe4\xb8\xbb\xe8\x81\x94\xe7\xb3\xbb\xe4\xba\xba', blank=True, to='vendor.Contact', null=True)),
            ],
            options={
                'ordering': ['code'],
                'verbose_name': '\u5546\u5bb6-\u4ea7\u54c1\u4f9b\u5e94\u5546',
                'verbose_name_plural': '\u5546\u5bb6-\u4ea7\u54c1\u4f9b\u5e94\u5546',
            },
        ),
        migrations.CreateModel(
            name='SupplierManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('supplier', models.ForeignKey(verbose_name=b'\xe4\xbe\x9b\xe5\xba\x94\xe5\x95\x86', to='vendor.Supplier')),
                ('user', models.ForeignKey(verbose_name=b'\xe4\xbe\x9b\xe5\xba\x94\xe5\x95\x86\xe7\xae\xa1\xe7\x90\x86\xe5\x91\x98\xe8\xb4\xa6\xe5\x8f\xb7', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u4f9b\u5e94\u5546\u8d26\u53f7\u7ba1\u7406',
                'verbose_name_plural': '\u4f9b\u5e94\u5546\u8d26\u53f7\u7ba1\u7406',
            },
        ),
    ]
