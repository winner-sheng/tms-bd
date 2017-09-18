# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CreditBook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(help_text='\u5bf9\u4e8e\u666e\u901a\u7528\u6237\u662f\u7528\u6237\u7684UID\uff0c\u5bf9\u4e8e\u4f9b\u5e94\u5546\uff0c\u5219\u662f"SUP-"\u524d\u7f00 + \u4f9b\u5e94\u5546\u7f16\u7801\uff0c\u5982"SUP-TWOHOU"', max_length=32, verbose_name='\u7528\u6237UID', db_index=True)),
                ('figure', models.PositiveIntegerField(default=0, help_text='\u51fa/\u5165\u8d26\u5747\u8ba1\u5165\u6b64\u680f\uff0c\u6b63\u503c\u8868\u793a\u6536\u5165\uff0c\u8d1f\u503c\u8868\u793a\u652f\u51fa', verbose_name='\u5165\u8d26\u571f\u7334\u5e01')),
                ('is_income', models.BooleanField(default=True, help_text='\u5982\u679c\u662f\u652f\u51fa\uff0c\u5e94\u8bbe\u4e3aFalse', verbose_name='\u662f\u5426\u6536\u5165')),
                ('source', models.CharField(help_text='\u8bf4\u660e\u571f\u7334\u5e01\u7684\u6765\u6e90\u4fe1\u606f\uff0c\u6bd4\u5982\u67d0\u4e2a\u4efb\u52a1\u5956\u52b1', max_length=200, verbose_name='\u571f\u7334\u5e01\u6765\u6e90')),
                ('extra_type', models.CharField(max_length=30, null=True, verbose_name='\u5173\u8054\u5bf9\u8c61\u7c7b\u578b', blank=True)),
                ('extra_data', models.CharField(help_text='\u7528\u4e8e\u4fdd\u5b58\u989d\u5916\u7684\u5173\u8054\u6570\u636e\uff0c\u6bd4\u5982\u8ba2\u5355\u53f7\u7b49', max_length=500, null=True, verbose_name='\u8865\u5145\u4fe1\u606f', blank=True)),
                ('scenario', models.CharField(help_text='\u7528\u4e8e\u533a\u5206\u83b7\u53d6\u79ef\u5206\u7684\u4e0d\u540c\u573a\u666f\u548c\u5e94\u7528\uff0c\u9884\u7559', max_length=50, null=True, verbose_name='\u573a\u666f', blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4', null=True)),
                ('expire_time', models.DateTimeField(null=True, verbose_name='\u5931\u6548\u65f6\u95f4', blank=True)),
                ('create_by', models.CharField(help_text='\u5bf9\u4e8e\u901a\u8fc7\u540e\u53f0\u7ba1\u7406\u5165\u53e3\u6dfb\u52a0\u8005\uff0c\u8bb0\u5f55\u7528\u6237\u4fe1\u606f"', max_length=32, verbose_name='\u521b\u5efa\u4eba', db_index=True)),
            ],
            options={
                'ordering': ['-pk'],
                'verbose_name': '\u79ef\u5206\u6d41\u6c34',
                'verbose_name_plural': '\u79ef\u5206\u6d41\u6c34',
            },
        ),
    ]
