# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentQueryLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('query_time', models.DateTimeField(auto_now_add=True, null=True, verbose_name=b'\xe6\x9f\xa5\xe8\xaf\xa2\xe6\x97\xb6\xe9\x97\xb4', db_index=True)),
                ('query_result', models.SmallIntegerField(default=0, help_text=b'\xe5\x89\x8d\xe5\x8f\xb0\xe6\x9f\xa5\xe8\xaf\xa2\xe8\xae\xa2\xe5\x8d\x95\xe5\x90\x8e\xe6\x93\x8d\xe4\xbd\x9c\xe7\xbb\x93\xe6\x9e\x9c', verbose_name=b'\xe8\xae\xa2\xe5\x8d\x95\xe7\xbb\x93\xe6\x9e\x9c', choices=[(0, b'\xe6\x97\xa0\xe6\x93\x8d\xe4\xbd\x9c'), (4, b'\xe5\xb7\xb2\xe5\x85\xa5\xe8\xb4\xa6PMS'), (1, b'\xe5\xb7\xb2\xe6\x94\xaf\xe4\xbb\x98'), (3, b'\xe5\xb7\xb2\xe8\x87\xaa\xe6\x8f\x90'), (2, b'\xe5\xb7\xb2\xe5\x8f\x96\xe6\xb6\x88')])),
                ('order_no', models.CharField(max_length=20, verbose_name=b'\xe8\xae\xa2\xe5\x8d\x95\xe7\xbc\x96\xe5\x8f\xb7', db_index=True)),
                ('user_id', models.CharField(max_length=36, verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7\xe6\x89\x8b\xe6\x9c\xba\xe5\x8f\xb7', db_index=True)),
                ('pay_amount', models.DecimalField(help_text=b'\xe5\x90\xab\xe8\xae\xa2\xe5\x8d\x95\xe5\x95\x86\xe5\x93\x81\xe6\x80\xbb\xe9\xa2\x9d\xe3\x80\x81\xe8\xbf\x90\xe8\xb4\xb9\xe3\x80\x81\xe4\xbc\x98\xe6\x83\xa0\xe7\xad\x89\xe8\xb4\xb9\xe7\x94\xa8', verbose_name=b'\xe6\x94\xaf\xe4\xbb\x98\xe6\x80\xbb\xe9\xa2\x9d\xef\xbf\xa5', max_digits=10, decimal_places=2)),
                ('is_checked', models.BooleanField(default=False, help_text=b'\xe5\xa6\x82\xe6\x9e\x9c\xe5\xad\x98\xe5\x9c\xa8\xe5\x8f\xaf\xe7\x96\x91\xe8\xa1\x8c\xe4\xb8\xba\xef\xbc\x8c\xe6\xad\xa4\xe9\xa1\xb9\xe8\xae\xb0\xe5\xbd\x95\xe5\xb7\xb2\xe7\xbb\x8f\xe9\xaa\x8c\xe8\xaf\x81\xe8\xbf\x87\xef\xbc\x8c\xe6\x97\xa0\xe9\x9c\x80\xe5\x86\x8d\xe6\x8f\x90\xe7\xa4\xba', verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe5\xb7\xb2\xe9\xaa\x8c\xe8\xaf\x81')),
                ('agent', models.ForeignKey(verbose_name=b'\xe5\x89\x8d\xe5\x8f\xb0', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u524d\u53f0\u8ba2\u5355\u67e5\u8be2\u65e5\u5fd7',
                'verbose_name_plural': '\u524d\u53f0\u8ba2\u5355\u67e5\u8be2\u65e5\u5fd7',
            },
        ),
        migrations.CreateModel(
            name='PingppHookLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_id', models.CharField(max_length=32, null=True, verbose_name=b'\xe4\xba\x8b\xe4\xbb\xb6id', blank=True)),
                ('object', models.CharField(default=b'event', max_length=32, null=True, verbose_name=b'\xe5\xaf\xb9\xe8\xb1\xa1\xef\xbc\x88\xe5\x80\xbc\xe4\xb8\xbaevent\xef\xbc\x89', blank=True)),
                ('livemode', models.BooleanField(verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe7\x94\x9f\xe4\xba\xa7')),
                ('created', models.PositiveIntegerField(null=True, verbose_name=b'\xe6\x97\xb6\xe9\x97\xb4\xe6\x88\xb3', blank=True)),
                ('data', models.CharField(max_length=2000, null=True, verbose_name=b'\xe4\xba\x8b\xe4\xbb\xb6\xe7\xbb\x91\xe5\xae\x9a\xe6\x95\xb0\xe6\x8d\xae', blank=True)),
                ('pending_webhooks', models.PositiveIntegerField(default=0, null=True, verbose_name=b'\xe6\x8e\xa8\xe9\x80\x81\xe6\x9c\xaa\xe6\x88\x90\xe5\x8a\x9f\xe6\x95\xb0', blank=True)),
                ('type', models.CharField(max_length=50, null=True, verbose_name=b'\xe4\xba\x8b\xe4\xbb\xb6\xe7\xb1\xbb\xe5\x9e\x8b', blank=True)),
                ('request', models.CharField(max_length=32, null=True, verbose_name=b'API Request ID', blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True)),
            ],
            options={
                'verbose_name': 'PingppHook\u4e8b\u4ef6\u53cd\u9988\u53ca\u7edf\u8ba1\u8bb0\u5f55',
                'verbose_name_plural': 'PingppHook\u4e8b\u4ef6\u53cd\u9988\u53ca\u7edf\u8ba1\u8bb0\u5f55',
            },
        ),
        migrations.CreateModel(
            name='TaskLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name=b'\xe4\xbb\xbb\xe5\x8a\xa1\xe5\x90\x8d\xe7\xa7\xb0', db_index=True)),
                ('start_time', models.DateTimeField(db_index=True, null=True, verbose_name=b'\xe5\xbc\x80\xe5\xa7\x8b\xe6\x97\xb6\xe9\x97\xb4', blank=True)),
                ('end_time', models.DateTimeField(null=True, verbose_name=b'\xe7\xbb\x93\xe6\x9d\x9f\xe6\x97\xb6\xe9\x97\xb4', blank=True)),
                ('time_cost', models.PositiveIntegerField(default=0, verbose_name=b'\xe8\x80\x97\xe6\x97\xb6(\xe7\xa7\x92)')),
                ('exec_result', models.CharField(max_length=256, null=True, verbose_name=b'\xe6\x89\xa7\xe8\xa1\x8c\xe7\xbb\x93\xe6\x9e\x9c', blank=True)),
                ('is_ok', models.BooleanField(default=True, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe6\xad\xa3\xe5\xb8\xb8')),
                ('result_file', models.FilePathField(max_length=200, null=True, verbose_name=b'\xe7\xbb\x93\xe6\x9e\x9c\xe6\x96\x87\xe4\xbb\xb6', blank=True)),
            ],
            options={
                'verbose_name': '\u8ba1\u5212\u4efb\u52a1\u6267\u884c\u65e5\u5fd7',
                'verbose_name_plural': '\u8ba1\u5212\u4efb\u52a1\u6267\u884c\u65e5\u5fd7',
            },
        ),
        migrations.CreateModel(
            name='UserFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('feedback', models.TextField(max_length=500, verbose_name=b'\xe6\x84\x8f\xe8\xa7\x81\xe6\x88\x96\xe8\x80\x85\xe5\xbb\xba\xe8\xae\xae')),
                ('answer', models.CharField(max_length=200, null=True, verbose_name=b'\xe7\xad\x94\xe5\xa4\x8d', blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('create_by', models.IntegerField(verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe4\xba\xba', null=True, editable=False, blank=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('update_by', models.IntegerField(verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe4\xba\xba', null=True, editable=False, blank=True)),
                ('user', models.ForeignKey(verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7', blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u7528\u6237\u53cd\u9988',
                'verbose_name_plural': '\u7528\u6237\u53cd\u9988',
            },
        ),
        migrations.CreateModel(
            name='UserMailLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mail_from', models.CharField(default=b'OMS <oms@sh-anze.com>', max_length=60, null=True, verbose_name=b'\xe5\x8f\x91\xe4\xbb\xb6\xe5\x9c\xb0\xe5\x9d\x80', blank=True)),
                ('mail_to', models.CharField(max_length=60, verbose_name=b'\xe6\x94\xb6\xe4\xbb\xb6\xe5\x9c\xb0\xe5\x9d\x80')),
                ('mail_cc', models.CharField(max_length=60, null=True, verbose_name=b'\xe6\x8a\x84\xe9\x80\x81\xe5\x9c\xb0\xe5\x9d\x80', blank=True)),
                ('mail_bcc', models.CharField(max_length=60, null=True, verbose_name=b'\xe5\xaf\x86\xe4\xbb\xb6\xe6\x8a\x84\xe9\x80\x81\xe5\x9c\xb0\xe5\x9d\x80', blank=True)),
                ('subject', models.CharField(max_length=100, verbose_name=b'\xe4\xb8\xbb\xe9\xa2\x98')),
                ('body', models.CharField(max_length=1000, null=True, verbose_name=b'\xe6\xad\xa3\xe6\x96\x87', blank=True)),
                ('attachments', models.CharField(help_text=b'\xe5\xa4\x9a\xe4\xb8\xaa\xe9\x99\x84\xe4\xbb\xb6\xe4\xbb\xa5\xe5\x88\x86\xe5\x8f\xb7\xe5\x88\x86\xe9\x9a\x94', max_length=1000, null=True, verbose_name=b'\xe9\x99\x84\xe4\xbb\xb6\xe5\x9c\xb0\xe5\x9d\x80', blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('send_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9c\x80\xe8\xbf\x91\xe5\x8f\x91\xe9\x80\x81\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('retries', models.PositiveSmallIntegerField(default=0, verbose_name=b'\xe9\x87\x8d\xe8\xaf\x95\xe6\xac\xa1\xe6\x95\xb0')),
                ('is_sent', models.BooleanField(default=False, db_index=True, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe5\xb7\xb2\xe5\x8f\x91\xe9\x80\x81')),
            ],
            options={
                'ordering': ['-send_time'],
                'verbose_name': '\u90ae\u4ef6\u901a\u77e5\u53d1\u9001\u65e5\u5fd7',
                'verbose_name_plural': '\u90ae\u4ef6\u901a\u77e5\u53d1\u9001\u65e5\u5fd7',
            },
        ),
        migrations.CreateModel(
            name='UserPayLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(max_length=32, verbose_name=b'\xe4\xbb\x98\xe6\xac\xbe\xe4\xba\xbaUID', db_index=True)),
                ('pay_code', models.CharField(max_length=32, verbose_name=b'\xe6\x94\xaf\xe4\xbb\x98\xe7\xa0\x81', db_index=True)),
                ('order_no', models.CharField(max_length=20, verbose_name=b'\xe8\xae\xa2\xe5\x8d\x95\xe7\xbc\x96\xe5\x8f\xb7', db_index=True)),
                ('pay_type', models.IntegerField(default=0, verbose_name=b'\xe6\x94\xaf\xe4\xbb\x98\xe6\x96\xb9\xe5\xbc\x8f', choices=[(0, b'\xe6\x9c\xaa\xe7\x9f\xa5'), (1, b'\xe7\xba\xbf\xe4\xb8\x8b\xe6\x94\xaf\xe4\xbb\x98'), (2, b'\xe5\xbe\xae\xe4\xbf\xa1'), (3, b'\xe6\x94\xaf\xe4\xbb\x98\xe5\xae\x9d'), (4, b'\xe9\x93\xb6\xe8\x81\x94'), (999, b'\xe6\xb7\xb7\xe5\x90\x88\xe6\x94\xaf\xe4\xbb\x98'), (1000, b'\xe6\x9c\xaa\xe7\x9f\xa5\xe6\x94\xaf\xe4\xbb\x98\xe6\x96\xb9\xe5\xbc\x8f')])),
                ('pay_amount', models.DecimalField(verbose_name=b'\xe6\x94\xaf\xe4\xbb\x98\xe6\x80\xbb\xe9\xa2\x9d', max_digits=10, decimal_places=2)),
                ('pay_time', models.DateTimeField(auto_now_add=True, null=True, verbose_name=b'\xe6\x94\xaf\xe4\xbb\x98\xe6\x97\xb6\xe9\x97\xb4', db_index=True)),
                ('pay_log', models.TextField(max_length=2000, null=True, verbose_name=b'\xe6\x94\xaf\xe4\xbb\x98\xe8\xae\xb0\xe5\xbd\x95', blank=True)),
                ('is_confirmed', models.BooleanField(default=False, help_text=b'\xe6\x94\xaf\xe4\xbb\x98\xe5\x90\x8e\xe8\xb7\x9f\xe6\x94\xaf\xe4\xbb\x98\xe5\xb9\xb3\xe5\x8f\xb0\xe7\xa1\xae\xe8\xae\xa4\xe6\x94\xaf\xe4\xbb\x98\xe7\xbb\x93\xe6\x9e\x9c', verbose_name=b'\xe6\x94\xaf\xe4\xbb\x98\xe7\xa1\xae\xe8\xae\xa4')),
                ('is_refund', models.BooleanField(default=False, help_text=b'\xe4\xbb\x85\xe5\xbd\x93\xe9\x80\x80\xe6\xac\xbe\xe6\x97\xb6\xe6\xa0\x87\xe8\xae\xb0\xe4\xb8\xbaTrue', verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe9\x80\x80\xe6\xac\xbe')),
            ],
            options={
                'verbose_name': '\u8ba2\u5355\u652f\u4ed8/\u9000\u6b3e\u8bb0\u5f55',
                'verbose_name_plural': '\u8ba2\u5355\u652f\u4ed8/\u9000\u6b3e\u8bb0\u5f55',
            },
        ),
        migrations.CreateModel(
            name='UserSmsLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mobile', models.CharField(max_length=15, verbose_name=b'\xe6\x89\x8b\xe6\x9c\xba', db_index=True)),
                ('send_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x8f\x91\xe9\x80\x81\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('sms', models.CharField(max_length=300, verbose_name=b'\xe7\x9f\xad\xe4\xbf\xa1\xe5\x86\x85\xe5\xae\xb9')),
                ('log', models.CharField(max_length=300, null=True, verbose_name=b'\xe6\x93\x8d\xe4\xbd\x9c\xe7\xbb\x93\xe6\x9e\x9c', blank=True)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u77ed\u4fe1\u53d1\u9001\u65e5\u5fd7',
                'verbose_name_plural': '\u77ed\u4fe1\u53d1\u9001\u65e5\u5fd7',
            },
        ),
        migrations.CreateModel(
            name='WechatMsgLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('business_code', models.CharField(help_text=b'\xe7\x94\xa8\xe4\xba\x8e\xe4\xb8\x8d\xe5\x90\x8c\xe4\xb8\x9a\xe5\x8a\xa1\xe5\x9c\xba\xe6\x99\xaf', max_length=32, null=True, verbose_name=b'\xe4\xb8\x9a\xe5\x8a\xa1\xe4\xbb\xa3\xe7\xa0\x81', blank=True)),
                ('uid', models.CharField(max_length=32, verbose_name=b'\xe6\x8e\xa5\xe6\x94\xb6\xe7\x94\xa8\xe6\x88\xb7ID', db_index=True)),
                ('open_id', models.CharField(null=True, max_length=32, blank=True, unique=True, verbose_name=b'\xe5\xbe\xae\xe4\xbf\xa1OpenID', db_index=True)),
                ('subject', models.CharField(max_length=100, verbose_name=b'\xe4\xb8\xbb\xe9\xa2\x98')),
                ('body', models.CharField(max_length=1000, null=True, verbose_name=b'\xe6\xad\xa3\xe6\x96\x87', blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('send_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9c\x80\xe8\xbf\x91\xe5\x8f\x91\xe9\x80\x81\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('retries', models.PositiveSmallIntegerField(default=0, verbose_name=b'\xe9\x87\x8d\xe8\xaf\x95\xe6\xac\xa1\xe6\x95\xb0')),
                ('is_sent', models.BooleanField(default=False, db_index=True, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe5\xb7\xb2\xe5\x8f\x91\xe9\x80\x81')),
                ('sender', models.CharField(max_length=10, null=True, verbose_name=b'\xe5\x8f\x91\xe9\x80\x81\xe8\x80\x85', blank=True)),
                ('claim_time', models.DateTimeField(null=True, verbose_name=b'\xe5\x8f\x91\xe9\x80\x81\xe8\x80\x85\xe9\xa2\x86\xe5\x8f\x96\xe4\xbb\xbb\xe5\x8a\xa1\xe6\x97\xb6\xe9\x97\xb4', blank=True)),
            ],
            options={
                'verbose_name': '\u5fae\u4fe1\u6d88\u606f\u53d1\u9001\u65e5\u5fd7',
                'verbose_name_plural': '\u5fae\u4fe1\u6d88\u606f\u53d1\u9001\u65e5\u5fd7',
            },
        ),
        migrations.AlterUniqueTogether(
            name='userpaylog',
            unique_together=set([('order_no', 'is_refund')]),
        ),
    ]
