# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import vendor.models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0012_salesagent'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupplierNotice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.CharField(max_length=1024, verbose_name='\u901a\u544a\u5185\u5bb9')),
                ('effective_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='\u751f\u6548\u65f6\u95f4')),
                ('expire_time', models.DateTimeField(default=vendor.models._expire_time, verbose_name='\u5931\u6548\u65f6\u95f4')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4', null=True)),
                ('create_by', models.CharField(help_text='\u5bf9\u4e8e\u901a\u8fc7\u540e\u53f0\u7ba1\u7406\u5165\u53e3\u6dfb\u52a0\u8005\uff0c\u8bb0\u5f55username\uff0c\u901a\u8fc7\u63a5\u53e3\u7684\u8bb0\u5f55\u7528\u6237uid\u4fe1\u606f', max_length=32, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4', null=True)),
                ('update_by', models.CharField(help_text='\u5bf9\u4e8e\u901a\u8fc7\u540e\u53f0\u7ba1\u7406\u5165\u53e3\u6dfb\u52a0\u8005\uff0c\u8bb0\u5f55username\uff0c\u901a\u8fc7\u63a5\u53e3\u7684\u8bb0\u5f55\u7528\u6237uid\u4fe1\u606f', max_length=32, null=True, verbose_name='\u66f4\u65b0\u4eba', blank=True)),
                ('supplier', models.ForeignKey(verbose_name='\u6240\u5c5e\u4f9b\u5e94\u5546', to='vendor.Supplier')),
            ],
            options={
                'ordering': ['effective_time'],
                'verbose_name': '\u5546\u5bb6-\u4ea7\u54c1\u4f9b\u5e94\u5546',
                'verbose_name_plural': '\u5546\u5bb6-\u4ea7\u54c1\u4f9b\u5e94\u5546',
            },
        ),
        migrations.AlterModelOptions(
            name='suppliermanager',
            options={'verbose_name': '\u4f9b\u5e94\u5546\u7ba1\u7406\u5458\u8d26\u53f7', 'verbose_name_plural': '\u4f9b\u5e94\u5546\u7ba1\u7406\u5458\u8d26\u53f7'},
        ),
    ]
