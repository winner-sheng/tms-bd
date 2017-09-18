# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0003_auto_20160428_2259'),
    ]

    operations = [
        migrations.CreateModel(
            name='TmsReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('report_type', models.CharField(max_length=32, verbose_name='\u62a5\u8868\u7c7b\u578b')),
                ('title', models.CharField(max_length=64, verbose_name='\u62a5\u8868\u540d\u79f0')),
                ('start_time', models.DateTimeField(help_text='\u5373\u62a5\u8868\u7edf\u8ba1\u5468\u671f\u7684\u5f00\u59cb\u65f6\u95f4', null=True, verbose_name='\u62a5\u8868\u5f00\u59cb\u65f6\u95f4', db_index=True, blank=True)),
                ('end_time', models.DateTimeField(help_text='\u5373\u62a5\u8868\u7edf\u8ba1\u5468\u671f\u7684\u7ed3\u675f\u65f6\u95f4', null=True, verbose_name='\u62a5\u8868\u7ed3\u675f\u65f6\u95f4', db_index=True, blank=True)),
                ('data', models.TextField(help_text='\u62a5\u8868\u4e3b\u6570\u636e', null=True, verbose_name='\u62a5\u8868\u6570\u636e', blank=True)),
                ('summary', models.CharField(help_text='\u62a5\u8868\u6c47\u603b\u6570\u636e', max_length=1024, null=True, verbose_name='\u62a5\u8868\u6570\u636e', blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, help_text='\u5373\u62a5\u8868\u7edf\u8ba1\u5468\u671f\u7684\u7ed3\u675f\u65f6\u95f4', verbose_name='\u62a5\u8868\u521b\u5efa\u65f6\u95f4', db_index=True)),
                ('owner', models.CharField(help_text='\u7ec4\u5408\u503c\uff0c\u5f62\u5982"\u7c7b\u578b-\u5bf9\u8c61id"\u3002\u53ef\u4ee5\u662f\u4f9b\u5e94\u5546\uff0c\u5982SUP-<supplier_id>\uff0c\u4e5f\u53ef\u4ee5\u662f\u7528\u6237\uff0c\u5982UID-<end_user_uid>\u7b49', max_length=36, null=True, verbose_name='\u62a5\u8868\u5f52\u5c5e', blank=True)),
                ('is_sent', models.BooleanField(default=False, help_text='\u7528\u4e8e\u6807\u8bb0\u62a5\u8868\u662f\u5426\u5df2\u53d1\u9001\u7ed9\u76f8\u5173\u65b9', verbose_name='\u662f\u5426\u5df2\u53d1\u9001')),
                ('is_confirmed', models.BooleanField(default=False, help_text='\u62a5\u8868\u63d0\u4ea4\u7ed9\u6307\u5b9a\u5bf9\u8c61\u5ba1\u6838\u540e\u88ab\u8ba4\u53ef', verbose_name='\u662f\u5426\u786e\u8ba4')),
                ('confirmed_by', models.CharField(max_length=32, null=True, verbose_name='\u7528\u6237ID', blank=True)),
                ('confirmed_time', models.DateTimeField(help_text='\u5373\u62a5\u8868\u88ab\u6307\u5b9a\u5bf9\u8c61\u5ba1\u6838\u786e\u8ba4\u7684\u65f6\u95f4', null=True, verbose_name='\u786e\u8ba4\u65f6\u95f4', db_index=True, blank=True)),
                ('memo', models.CharField(help_text='\u901a\u5e38\u7528\u4e8e\u62a5\u8868\u6709\u8c03\u6574\u65f6\u586b\u5199', max_length=1024, null=True, verbose_name='\u5907\u6ce8', blank=True)),
            ],
            options={
                'verbose_name': '\u7edf\u8ba1\u62a5\u8868',
                'verbose_name_plural': '\u7edf\u8ba1\u62a5\u8868',
            },
        ),
        migrations.AlterModelOptions(
            name='rewardsummary',
            options={'ordering': ['-settled_reward', '-not_settled_reward'], 'managed': False, 'verbose_name': '\u6536\u76ca\u7edf\u8ba1', 'verbose_name_plural': '\u6536\u76ca\u7edf\u8ba1'},
        ),
    ]
