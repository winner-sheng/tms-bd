# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import config.models
import datetime
import django.db.models.deletion
from django.conf import settings
import ueditor.models


class Migration(migrations.Migration):

    dependencies = [
        # ('basedata', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('filemgmt', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiAuth',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('grant_to', models.CharField(help_text=b'\xe6\x8f\x8f\xe8\xbf\xb0\xe6\x8e\xa5\xe5\x8f\xa3\xe8\xae\xb8\xe5\x8f\xaf\xe5\xaf\xb9\xe8\xb1\xa1\xe6\x98\xaf\xe8\xb0\x81', max_length=30, verbose_name=b'\xe6\x8e\x88\xe6\x9d\x83\xe5\xaf\xb9\xe8\xb1\xa1')),
                ('visitor_code', models.CharField(help_text=b'\xe4\xbb\xa4\xe7\x89\x8c\xe9\xaa\x8c\xe8\xaf\x81\xe9\x80\x9a\xe8\xbf\x87\xe5\x90\x8e\xef\xbc\x8c\xe8\x87\xaa\xe5\x8a\xa8\xe8\xbf\x94\xe5\x9b\x9e\xe6\x8e\x88\xe6\x9d\x83\xe5\xaf\xb9\xe8\xb1\xa1\xe7\x9a\x84\xe8\xba\xab\xe4\xbb\xbd\xe7\xbc\x96\xe7\xa0\x81\xef\xbc\x8c\xe6\x9f\x90\xe4\xba\x9b\xe6\x83\x85\xe5\x86\xb5\xe4\xb8\x8b\xe7\x9b\xb8\xe5\x85\xb3\xe6\x8e\xa5\xe5\x8f\xa3\xe8\xbf\x94\xe5\x9b\x9e\xe6\x95\xb0\xe6\x8d\xae\xe5\x86\x85\xe5\xae\xb9\xe9\x9c\x80\xe6\xa0\xb9\xe6\x8d\xae\xe6\xad\xa4\xe8\xaf\x86\xe5\x88\xab\xe7\xa0\x81\xe8\xbf\x9b\xe8\xa1\x8c\xe5\x8c\xba\xe5\x88\x86', max_length=30, null=True, verbose_name=b'\xe6\x8e\x88\xe6\x9d\x83\xe5\xaf\xb9\xe8\xb1\xa1\xe8\xaf\x86\xe5\x88\xab\xe7\xa0\x81', blank=True)),
                ('token', models.CharField(default=config.models.create_token, help_text=b'32\xe4\xbd\x8d\xe4\xbb\xa4\xe7\x89\x8c\xef\xbc\x8c\xe5\x8f\xaf\xe8\x87\xaa\xe5\x8a\xa8\xe7\x94\x9f\xe6\x88\x90\xe3\x80\x82\xe5\xa4\x96\xe9\x83\xa8\xe8\xae\xbf\xe9\x97\xae\xe6\x8e\x88\xe6\x9d\x83\xe6\x8e\xa5\xe5\x8f\xa3\xe6\x97\xb6\xef\xbc\x8c\xe5\xbf\x85\xe9\xa1\xbb\xe5\xb8\xa6\xe6\xad\xa4token\xef\xbc\x8c\xe5\x90\xa6\xe5\x88\x99\xe6\x8b\x92\xe7\xbb\x9d\xe8\xae\xbf\xe9\x97\xae', unique=True, max_length=32, verbose_name=b'\xe6\x8e\x88\xe6\x9d\x83\xe4\xbb\xa4\xe7\x89\x8c(\xe5\x8f\xaf\xe8\x87\xaa\xe5\x8a\xa8\xe7\x94\x9f\xe6\x88\x90)')),
                ('api_list', models.CharField(help_text=b'\xe5\xa6\x82\xe6\x9e\x9c\xe8\xae\xbe\xe5\xae\x9a\xe6\xad\xa4\xe9\xa1\xb9\xef\xbc\x8c\xe5\x88\x99\xe5\x8f\xaa\xe5\x85\x81\xe8\xae\xb8\xe5\xa4\x96\xe9\x83\xa8\xe7\x94\xa8\xe6\x88\xb7\xe4\xbd\xbf\xe7\x94\xa8token\xe8\xae\xbf\xe9\x97\xae\xe7\x9a\x84\xe6\x8e\xa5\xe5\x8f\xa3\xe5\x88\x97\xe8\xa1\xa8\xef\xbc\x8c\xe5\xa4\x9a\xe4\xb8\xaa\xe6\x8e\xa5\xe5\x8f\xa3\xe7\x94\xa8","\xe5\x88\x86\xe9\x9a\x94\xef\xbc\x8c\xe9\xbb\x98\xe8\xae\xa4\xe4\xb8\x8d\xe5\x81\x9a\xe9\x99\x90\xe5\x88\xb6', max_length=1024, null=True, verbose_name=b'\xe8\xae\xb8\xe5\x8f\xaf\xe6\x8e\xa5\xe5\x8f\xa3\xe5\x88\x97\xe8\xa1\xa8', blank=True)),
                ('ip_list', models.CharField(help_text=b'\xe5\xa6\x82\xe6\x9e\x9c\xe8\xae\xbe\xe5\xae\x9a\xe6\xad\xa4\xe9\xa1\xb9\xef\xbc\x8c\xe5\x88\x99\xe5\x8f\xaa\xe5\x85\x81\xe8\xae\xb8\xe5\x88\x97\xe8\xa1\xa8\xe4\xb8\xad\xe7\x9a\x84\xe6\x9d\xa5\xe6\xba\x90IP\xe8\xae\xbf\xe9\x97\xae\xe7\x9b\xb8\xe5\x85\xb3\xe6\x8e\xa5\xe5\x8f\xa3\xef\xbc\x8c\xe5\xa4\x9a\xe4\xb8\xaaIP\xe7\x94\xa8","\xe5\x88\x86\xe9\x9a\x94\xef\xbc\x8c\xe9\xbb\x98\xe8\xae\xa4\xe4\xb8\x8d\xe5\x81\x9a\xe9\x99\x90\xe5\x88\xb6', max_length=1024, null=True, verbose_name=b'\xe8\xae\xb8\xe5\x8f\xaf\xe6\x9d\xa5\xe6\xba\x90IP\xe5\x88\x97\xe8\xa1\xa8', blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('grant_by', models.ForeignKey(verbose_name=b'\xe6\x8e\x88\xe6\x9d\x83\xe4\xba\xba', blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'API\u63a5\u53e3\u6388\u6743',
                'verbose_name_plural': 'API\u63a5\u53e3\u6388\u6743',
            },
        ),
        migrations.CreateModel(
            name='AppSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.CharField(default=b'app', max_length=30, verbose_name=b'\xe7\xb1\xbb\xe5\x88\xab', choices=[(b'app', b'\xe5\x85\xa8\xe5\xb1\x80'), (b'activity', b'\xe6\xb4\xbb\xe5\x8a\xa8\xe7\x9b\xb8\xe5\x85\xb3'), (b'callback', b'\xe5\x9b\x9e\xe8\xb0\x83URL'), (b'payment', b'\xe6\x94\xaf\xe4\xbb\x98\xe5\x8f\x82\xe6\x95\xb0')])),
                ('name', models.CharField(help_text=b'\xe5\xbb\xba\xe8\xae\xae\xe4\xbd\xbf\xe7\x94\xa8\xe8\x8b\xb1\xe6\x96\x87\xe5\xad\x97\xe7\xac\xa6\xe8\xa1\xa8\xe7\xa4\xba', max_length=30, verbose_name=b'\xe9\x85\x8d\xe7\xbd\xae\xe9\xa1\xb9\xe9\x94\xae\xe5\x80\xbc')),
                ('usage', models.CharField(max_length=30, null=True, verbose_name=b'\xe9\x85\x8d\xe7\xbd\xae\xe9\xa1\xb9\xe7\x94\xa8\xe9\x80\x94', blank=True)),
                ('value_type', models.PositiveSmallIntegerField(default=0, verbose_name=b'\xe6\x95\xb0\xe6\x8d\xae\xe6\xa0\xbc\xe5\xbc\x8f', choices=[(0, b'\xe5\xad\x97\xe7\xac\xa6\xe5\x9e\x8b'), (1, b'\xe6\x95\xb4\xe5\xbd\xa2\xe6\x95\xb0\xe5\x80\xbc'), (2, b'\xe6\xb5\xae\xe7\x82\xb9\xe6\x95\xb0\xe5\x80\xbc'), (8, b'HTML\xe6\xa0\xbc\xe5\xbc\x8f'), (9, b'JSON\xe6\xa0\xbc\xe5\xbc\x8f')])),
                ('value', models.CharField(max_length=1024, null=True, verbose_name=b'\xe9\x85\x8d\xe7\xbd\xae\xe9\xa1\xb9\xe5\x80\xbc', blank=True)),
            ],
            options={
                'verbose_name': '\u7cfb\u7edf\u8bbe\u7f6e',
                'verbose_name_plural': '\u7cfb\u7edf\u8bbe\u7f6e',
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=20, null=True, verbose_name=b'\xe6\x96\x87\xe7\xab\xa0\xe4\xb8\xbb\xe9\xa2\x98', blank=True)),
                ('tags', models.CharField(max_length=256, blank=True, help_text=b'\xe7\x94\xa8\xe4\xba\x8e\xe6\x96\x87\xe7\xab\xa0\xe6\x90\x9c\xe7\xb4\xa2\xef\xbc\x8c\xe6\xaf\x8f\xe4\xb8\xaa\xe6\xa0\x87\xe7\xad\xbe\xe4\xb9\x8b\xe9\x97\xb4\xe5\xba\x94\xe4\xbd\xbf\xe7\x94\xa8\xe8\x8b\xb1\xe6\x96\x87\xe9\x80\x97\xe5\x8f\xb7","\xe5\x88\x86\xe9\x9a\x94\xef\xbc\x8c\xe6\xa0\x87\xe7\xad\xbe\xe4\xb8\xba\xe7\xb2\xbe\xe7\xa1\xae\xe5\x8c\xb9\xe9\x85\x8d', null=True, verbose_name=b'\xe6\x96\x87\xe7\xab\xa0Tag', db_index=True)),
                ('content', ueditor.models.UEditorField(help_text=b'\xe6\xb3\xa8\xe6\x84\x8f\xef\xbc\x9a\xe5\xbb\xba\xe8\xae\xae\xe4\xbd\xbf\xe7\x94\xa8\xe4\xb8\x8d\xe8\xb6\x85\xe8\xbf\x87600\xe5\x83\x8f\xe7\xb4\xa0\xe5\xae\xbd\xe5\xba\xa6\xe7\x9a\x84\xe5\x9b\xbe\xe7\x89\x87\xe3\x80\x82\xe9\x99\xa4\xe9\x9d\x9e\xe6\x98\x8e\xe7\xa1\xae\xe7\x9f\xa5\xe9\x81\x93\xe8\xae\xbe\xe7\xbd\xae\xe5\x9b\xbe\xe7\x89\x87\xe5\xa4\xa7\xe5\xb0\x8f\xe7\x9a\x84\xe7\x9b\xae\xe7\x9a\x84\xef\xbc\x8c\xe5\x90\xa6\xe5\x88\x99\xe8\xaf\xb7\xe4\xb8\x8d\xe8\xa6\x81\xe6\x8c\x87\xe5\xae\x9a\xe5\x9b\xbe\xe7\x89\x87\xe5\xa4\xa7\xe5\xb0\x8f\xef\xbc\x8c\xe7\x94\xb1\xe9\xa1\xb5\xe9\x9d\xa2\xe8\x87\xaa\xe5\x8a\xa8\xe7\xbc\xa9\xe6\x94\xbe', max_length=20000, null=True, verbose_name=b'\xe5\x86\x85\xe5\xae\xb9\xe6\x8f\x8f\xe8\xbf\xb0', blank=True)),
                ('link_to', models.CharField(help_text=b'\xe5\x8d\xb3\xe7\x94\xa8\xe6\x88\xb7\xe7\x82\xb9\xe5\x87\xbb\xe8\xaf\xa5\xe4\xb8\xbb\xe9\xa2\x98\xe5\x9b\xbe\xe7\x89\x87\xe5\x90\x8e\xef\xbc\x8c\xe6\x89\x93\xe5\xbc\x80\xe7\x9a\x84\xe5\xa4\x96\xe9\x93\xbe\xe5\x9c\xb0\xe5\x9d\x80\xef\xbc\x88\xe9\xbb\x98\xe8\xae\xa4\xe5\x9c\xa8\xe5\x95\x86\xe5\x9f\x8e\xe4\xb8\xad\xe6\x89\x93\xe5\xbc\x80\xef\xbc\x8c\xe6\x97\xa0\xe9\x9c\x80\xe9\x85\x8d\xe7\xbd\xae\xef\xbc\x89', max_length=100, null=True, verbose_name=b'\xe7\x9b\xae\xe6\xa0\x87\xe5\x9c\xb0\xe5\x9d\x80', blank=True)),
                ('list_order', models.PositiveIntegerField(default=0, null=True, verbose_name=b'\xe6\x98\xbe\xe7\xa4\xba\xe9\xa1\xba\xe5\xba\x8f(\xe5\xa4\xa7\xe7\x9a\x84\xe5\x9c\xa8\xe5\x89\x8d)', db_index=True, blank=True)),
                ('effective_date', models.DateTimeField(default=datetime.datetime.now, help_text=b'\xe5\x8f\xaa\xe6\x9c\x89\xe7\x94\x9f\xe6\x95\x88\xe6\x97\xb6\xe9\x97\xb4\xe5\x90\x8e\xe7\x9a\x84\xe6\x96\x87\xe7\xab\xa0\xe6\x89\x8d\xe4\xbc\x9a\xe5\xb1\x95\xe7\xa4\xba', null=True, verbose_name=b'\xe7\x94\x9f\xe6\x95\x88\xe6\x97\xb6\xe9\x97\xb4', blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe6\x9c\x89\xe6\x95\x88')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('create_by', models.IntegerField(verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe4\xba\xba', null=True, editable=False, blank=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('update_by', models.IntegerField(verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe4\xba\xba', null=True, editable=False, blank=True)),
                ('content_image', models.ForeignKey(related_name='discovery_content_image+', blank=True, to='filemgmt.BaseImage', help_text=b'\xe6\x9f\xa5\xe7\x9c\x8b\xe6\x96\x87\xe7\xab\xa0\xe7\x9a\x84\xe8\xaf\xa6\xe6\x83\x85\xe6\x97\xb6\xe6\x98\xbe\xe7\xa4\xba\xef\xbc\x8c\xe9\xbb\x98\xe8\xae\xa4\xe4\xb8\x8e\xe4\xb8\xbb\xe9\xa2\x98\xe5\x9b\xbe\xe7\x89\x87\xe7\x9b\xb8\xe5\x90\x8c', null=True, verbose_name=b'\xe5\x86\x85\xe5\xae\xb9\xe5\x9b\xbe\xe7\x89\x87')),
                ('subject_image', models.ForeignKey(related_name='discovery_subject_image+', verbose_name=b'\xe4\xb8\xbb\xe9\xa2\x98\xe5\x9b\xbe\xe7\x89\x87', to='filemgmt.BaseImage', help_text=b'\xe5\xbb\xba\xe8\xae\xae\xe4\xbd\xbf\xe7\x94\xa8\xe5\xae\xbd\xe5\xba\xa6\xe4\xb8\xba\xe4\xb8\x8d\xe8\xb6\x85\xe8\xbf\x87600\xe5\x83\x8f\xe7\xb4\xa0\xe7\x9a\x84\xe5\x9b\xbe\xe7\x89\x87\xef\xbc\x8c\xe9\xab\x98\xe5\xba\xa6\xe6\xa0\xb9\xe6\x8d\xae\xe9\x9c\x80\xe8\xa6\x81\xe9\x85\x8c\xe6\x83\x85\xe8\xae\xbe\xe8\xae\xa1')),
            ],
            options={
                'ordering': ('-list_order', '-update_time'),
                'verbose_name': '\u6587\u7ae0',
                'verbose_name_plural': '\u6587\u7ae0',
            },
        ),
        migrations.CreateModel(
            name='ArticleProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('list_order', models.PositiveIntegerField(default=0, null=True, verbose_name=b'\xe6\x98\xbe\xe7\xa4\xba\xe9\xa1\xba\xe5\xba\x8f(\xe5\xa4\xa7\xe7\x9a\x84\xe5\x9c\xa8\xe5\x89\x8d)', blank=True)),
                ('article', models.ForeignKey(verbose_name=b'\xe6\x96\x87\xe7\xab\xa0', to='config.Article')),
                ('product', models.ForeignKey(verbose_name=b'\xe5\x95\x86\xe5\x93\x81', to='basedata.Product')),
            ],
            options={
                'ordering': ('-list_order', 'id'),
                'verbose_name': '\u6587\u7ae0\u5546\u54c1\u6620\u5c04\u8868',
                'verbose_name_plural': '\u6587\u7ae0\u5546\u54c1\u6620\u5c04\u8868',
            },
        ),
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=20, null=True, verbose_name=b'\xe4\xb8\xbb\xe9\xa2\x98', blank=True)),
                ('link_to', models.CharField(help_text=b'\xe5\x8d\xb3\xe7\x94\xa8\xe6\x88\xb7\xe7\x82\xb9\xe5\x87\xbb\xe8\xaf\xa5Banner\xe5\x9b\xbe\xe7\x89\x87\xe5\x90\x8e\xef\xbc\x8c\xe6\x89\x93\xe5\xbc\x80\xe7\x9a\x84\xe9\xa1\xb5\xe9\x9d\xa2\xe5\x9c\xb0\xe5\x9d\x80', max_length=100, null=True, verbose_name=b'\xe7\x9b\xae\xe6\xa0\x87\xe5\x9c\xb0\xe5\x9d\x80', blank=True)),
                ('list_order', models.PositiveIntegerField(default=0, null=True, verbose_name=b'\xe6\x98\xbe\xe7\xa4\xba\xe9\xa1\xba\xe5\xba\x8f(\xe5\xa4\xa7\xe7\x9a\x84\xe5\x9c\xa8\xe5\x89\x8d)', blank=True)),
                ('effective_date', models.DateTimeField(default=datetime.datetime.now, help_text=b'\xe5\x8f\xaa\xe6\x9c\x89\xe7\x94\x9f\xe6\x95\x88\xe6\x97\xb6\xe9\x97\xb4\xe5\x90\x8e\xe7\x9a\x84Banner\xe6\x89\x8d\xe4\xbc\x9a\xe5\xb1\x95\xe7\xa4\xba', null=True, verbose_name=b'\xe7\x94\x9f\xe6\x95\x88\xe6\x97\xb6\xe9\x97\xb4', blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe6\x9c\x89\xe6\x95\x88')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('create_by', models.IntegerField(verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe4\xba\xba', null=True, editable=False, blank=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('update_by', models.IntegerField(verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe4\xba\xba', null=True, editable=False, blank=True)),
                ('image', models.ForeignKey(related_name='banner_image+', verbose_name=b'Banner\xe5\x9b\xbe\xe7\x89\x87', to='filemgmt.BaseImage', help_text=b'\xe5\xbb\xba\xe8\xae\xae\xe4\xbd\xbf\xe7\x94\xa8\xe5\xae\xbd\xe5\xba\xa6\xe4\xb8\xba400~600\xe5\x83\x8f\xe7\xb4\xa0\xe7\x9a\x84\xe5\x9b\xbe\xe7\x89\x87\xe3\x80\x82\xe9\xab\x98\xe5\xba\xa6\xe6\xa0\xb9\xe6\x8d\xae\xe5\x8f\xaf\xe9\xa1\xb5\xe9\x9d\xa2\xe5\xb8\x83\xe5\xb1\x80\xe9\x9c\x80\xe8\xa6\x81\xe8\xae\xbe\xe8\xae\xa1\xef\xbc\x8c\xe7\xa1\xae\xe4\xbf\x9d\xe5\xa4\x9a\xe5\xbc\xa0Banner\xe5\x9b\xbe\xe7\x89\x87\xe5\xb0\xba\xe5\xaf\xb8\xe4\xb8\x80\xe8\x87\xb4\xef\xbc\x81')),
            ],
            options={
                'ordering': ('-list_order', 'id'),
                'verbose_name': '\u9996\u9875Banner',
                'verbose_name_plural': '\u9996\u9875Banner',
            },
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=20, verbose_name=b'\xe5\x93\x81\xe7\x89\x8c\xe5\x90\x8d\xe7\xa7\xb0')),
                ('list_order', models.PositiveIntegerField(default=0, help_text=b'\xe6\x95\xb0\xe5\x80\xbc\xe8\xb6\x8a\xe5\xa4\xa7\xef\xbc\x8c\xe6\x8e\x92\xe5\xba\x8f\xe8\xb6\x8a\xe9\x9d\xa0\xe5\x89\x8d', verbose_name=b'\xe6\x8e\x92\xe5\xba\x8f\xe6\xa0\x87\xe8\xae\xb0')),
            ],
            options={
                'ordering': ('-list_order',),
                'verbose_name': '\u54c1\u724c\u5217\u8868',
                'verbose_name_plural': '\u54c1\u724c\u5217\u8868',
            },
        ),
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=20, verbose_name=b'\xe9\xa2\x91\xe9\x81\x93\xe5\x90\x8d\xe7\xa7\xb0')),
                ('link_to', models.CharField(help_text=b'\xe5\x8d\xb3\xe7\x94\xa8\xe6\x88\xb7\xe7\x82\xb9\xe5\x87\xbb\xe8\xaf\xa5\xe9\xa2\x91\xe9\x81\x93\xe5\x90\x8e\xef\xbc\x8c\xe6\x89\x93\xe5\xbc\x80\xe7\x9a\x84\xe9\xa1\xb5\xe9\x9d\xa2\xe5\x9c\xb0\xe5\x9d\x80', max_length=100, null=True, verbose_name=b'\xe7\x9b\xae\xe6\xa0\x87\xe5\x9c\xb0\xe5\x9d\x80', blank=True)),
                ('list_order', models.PositiveIntegerField(default=0, null=True, verbose_name=b'\xe6\x98\xbe\xe7\xa4\xba\xe9\xa1\xba\xe5\xba\x8f(\xe5\xa4\xa7\xe7\x9a\x84\xe5\x9c\xa8\xe5\x89\x8d)', blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe6\x9c\x89\xe6\x95\x88')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('create_by', models.IntegerField(verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe4\xba\xba', null=True, editable=False, blank=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('update_by', models.IntegerField(verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe4\xba\xba', null=True, editable=False, blank=True)),
                ('image', models.ForeignKey(related_name='channel_image+', verbose_name=b'\xe9\xa2\x91\xe9\x81\x93\xe5\x9b\xbe\xe7\x89\x87', to='filemgmt.BaseImage', help_text=b'\xe8\xaf\xb7\xe6\xb3\xa8\xe6\x84\x8f\xe5\x9b\xbe\xe7\x89\x87\xe5\xb0\xba\xe5\xaf\xb8\xe4\xbb\xa5\xe9\x80\x82\xe5\xba\x94\xe9\xa6\x96\xe9\xa1\xb5\xe5\xb8\x83\xe5\xb1\x80\xef\xbc\x8c\xe6\x9c\x80\xe5\xa4\xa7\xe5\xae\xbd\xe5\xba\xa6\xe4\xb8\x8d\xe8\xa6\x81\xe8\xb6\x85\xe8\xbf\x87600\xe5\x83\x8f\xe7\xb4\xa0')),
            ],
            options={
                'ordering': ('-list_order', 'id'),
                'verbose_name': '\u9891\u9053',
                'verbose_name_plural': '\u9891\u9053',
            },
        ),
        migrations.CreateModel(
            name='ChannelProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('list_order', models.PositiveIntegerField(default=0, null=True, verbose_name=b'\xe6\x98\xbe\xe7\xa4\xba\xe9\xa1\xba\xe5\xba\x8f(\xe5\xa4\xa7\xe7\x9a\x84\xe5\x9c\xa8\xe5\x89\x8d)', blank=True)),
                ('channel', models.ForeignKey(verbose_name=b'\xe9\xa2\x91\xe9\x81\x93', to='config.Channel')),
                ('product', models.ForeignKey(verbose_name=b'\xe5\x95\x86\xe5\x93\x81', to='basedata.Product')),
            ],
            options={
                'ordering': ('-list_order', 'id'),
                'verbose_name': '\u9891\u9053\u5546\u54c1\u6620\u5c04\u8868',
                'verbose_name_plural': '\u9891\u9053\u5546\u54c1\u6620\u5c04\u8868',
            },
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20, verbose_name=b'\xe5\x90\x8d\xe7\xa7\xb0')),
                ('pinyin', models.CharField(db_index=True, max_length=80, null=True, verbose_name=b'\xe6\x8b\xbc\xe9\x9f\xb3', blank=True)),
                ('pinyin_abbr', models.CharField(db_index=True, max_length=20, null=True, verbose_name=b'\xe6\x8b\xbc\xe9\x9f\xb3\xe7\xbc\xa9\xe5\x86\x99', blank=True)),
                ('level', models.PositiveSmallIntegerField(choices=[(0, b'\xe5\x9b\xbd\xe5\xae\xb6/\xe5\x9c\xb0\xe5\x8c\xba'), (1, b'\xe7\x9c\x81/\xe7\x9b\xb4\xe8\xbe\x96\xe5\xb8\x82/\xe8\x87\xaa\xe6\xb2\xbb\xe5\x8c\xba'), (2, b'\xe5\xb8\x82/\xe5\x8c\xba\xef\xbc\x88\xe5\x9c\xb0\xe7\xba\xa7\xef\xbc\x89'), (3, b'\xe5\xb8\x82/\xe5\x8c\xba/\xe5\x8e\xbf\xef\xbc\x88\xe5\x8e\xbf\xe7\xba\xa7\xef\xbc\x89'), (4, b'\xe9\x95\x87/\xe4\xb9\xa1/\xe8\xa1\x97\xe9\x81\x93'), (5, b'\xe6\x9d\x91/\xe5\xbc\x84/\xe5\xb0\x8f\xe5\x8c\xba')])),
                ('use_type', models.PositiveIntegerField(default=0, help_text=b'\xe4\xbf\x9d\xe7\x95\x99\xe5\xad\x97\xe6\xae\xb5')),
                ('list_order', models.PositiveIntegerField(default=0, help_text=b'\xe6\x95\xb0\xe5\x80\xbc\xe8\xb6\x8a\xe5\xa4\xa7\xef\xbc\x8c\xe6\x8e\x92\xe5\xba\x8f\xe8\xb6\x8a\xe9\x9d\xa0\xe5\x89\x8d', verbose_name=b'\xe6\x8e\x92\xe5\xba\x8f\xe6\xa0\x87\xe8\xae\xb0', db_index=True)),
                ('up', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name=b'\xe4\xb8\x8a\xe7\xba\xa7', blank=True, to='config.District', null=True)),
            ],
            options={
                'ordering': ['level', '-list_order', 'name'],
                'verbose_name': '\u884c\u653f\u533a\u5212',
                'verbose_name_plural': '\u884c\u653f\u533a\u5212',
            },
        ),
        migrations.AlterUniqueTogether(
            name='district',
            unique_together=set([('name', 'level')]),
        ),
    ]
