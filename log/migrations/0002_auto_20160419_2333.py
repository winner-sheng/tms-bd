# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailRecipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                # ('mail', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='UserMailLog', verbose_name=u'邮件', blank=False, null=False)),
                ('mail_to', models.CharField(max_length=60, verbose_name=b'\xe6\x94\xb6\xe4\xbb\xb6\xe5\x9c\xb0\xe5\x9d\x80')),
                ('mail_type', models.CharField(default=b'to', max_length=3, verbose_name=b'\xe5\x8f\x91\xe9\x80\x81\xe7\xb1\xbb\xe5\x9e\x8b', blank=True, choices=[(b'to', '\u6b63\u5e38'), (b'cc', '\u6284\u9001'), (b'bcc', '\u5bc6\u9001')])),
            ],
            options={
                'verbose_name': 'Email\u6536\u4ef6\u4eba',
                'verbose_name_plural': 'Email\u6536\u4ef6\u4eba',
            },
        ),
        migrations.AlterModelOptions(
            name='usermaillog',
            options={'ordering': ['-send_time'], 'verbose_name': 'Email\u901a\u77e5\u53d1\u9001\u65e5\u5fd7', 'verbose_name_plural': 'Email\u901a\u77e5\u53d1\u9001\u65e5\u5fd7'},
        ),
        migrations.RemoveField(
            model_name='usermaillog',
            name='mail_bcc',
        ),
        migrations.RemoveField(
            model_name='usermaillog',
            name='mail_cc',
        ),
        migrations.RemoveField(
            model_name='usermaillog',
            name='mail_to',
        ),
        migrations.AlterField(
            model_name='usermaillog',
            name='retries',
            field=models.PositiveSmallIntegerField(default=0, verbose_name=b'\xe5\x8f\x91\xe9\x80\x81\xe6\xac\xa1\xe6\x95\xb0'),
        ),
        migrations.AlterField(
            model_name='wechatmsglog',
            name='business_code',
            field=models.CharField(max_length=32, blank=True, help_text=b'\xe7\x94\xa8\xe4\xba\x8e\xe4\xb8\x8d\xe5\x90\x8c\xe4\xb8\x9a\xe5\x8a\xa1\xe5\x9c\xba\xe6\x99\xaf', null=True, verbose_name=b'\xe4\xb8\x9a\xe5\x8a\xa1\xe4\xbb\xa3\xe7\xa0\x81', db_index=True),
        ),
        migrations.AlterField(
            model_name='wechatmsglog',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', db_index=True),
        ),
        migrations.AlterField(
            model_name='wechatmsglog',
            name='retries',
            field=models.PositiveSmallIntegerField(default=0, verbose_name=b'\xe5\x8f\x91\xe9\x80\x81\xe6\xac\xa1\xe6\x95\xb0'),
        ),
        migrations.AlterField(
            model_name='wechatmsglog',
            name='sender',
            field=models.CharField(max_length=18, blank=True, help_text=b'\xe7\x94\xa8\xe4\xba\x8e\xe5\xa4\x9a\xe4\xbb\xbb\xe5\x8a\xa1\xe5\xa4\x84\xe7\x90\x86\xe9\x81\xbf\xe5\x85\x8d\xe8\xae\xbf\xe9\x97\xae\xe5\x86\xb2\xe7\xaa\x81', null=True, verbose_name=b'\xe5\x8f\x91\xe9\x80\x81\xe8\x80\x85', db_index=True),
        ),
        migrations.AddField(
            model_name='emailrecipient',
            name='mail',
            field=models.ForeignKey(verbose_name=b'\xe9\x82\xae\xe4\xbb\xb6', to='log.UserMailLog'),
        ),
    ]
