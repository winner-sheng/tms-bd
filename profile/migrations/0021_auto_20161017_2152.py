# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0020_auto_20161014_1344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccountbook',
            name='effective_time',
            field=models.DateTimeField(null=True, verbose_name='\u751f\u6548\u65f6\u95f4', blank=True),
        ),
        migrations.AlterField(
            model_name='usercapitalaccount',
            name='ca_type',
            field=models.CharField(default='wechat', max_length=10, verbose_name='\u8d26\u53f7\u7c7b\u522b', choices=[('wechat', '\u5fae\u4fe1\u94b1\u5305'), ('alipay', '\u652f\u4ed8\u5b9d'), ('deposit', '\u50a8\u84c4\u5361'), ('credit', '\u4fe1\u7528\u5361'), ('enterprise', '\u4f01\u4e1a\u8d26\u53f7'), ('other', '\u5176\u5b83')]),
        ),
        migrations.AlterField(
            model_name='usercapitalaccount',
            name='uid',
            field=models.CharField(help_text='\u5916\u90e8\u7528\u6237\u586b\u5199\u7528\u6237uid\uff0c\u5185\u90e8\u4f9b\u5e94\u5546\u586b\u5199\u201cSUP-\u4f9b\u5e94\u5546id\u201d(id\u4e0d\u8db312\u4f4d\u7684\u9700\u7528"0"\u5728\u5de6\u4fa7\u8865\u9f50)\uff0c\u5982SUP-000000000001', max_length=32, verbose_name='\u7528\u6237UID', db_index=True),
        ),
        migrations.AlterField(
            model_name='withdrawrequest',
            name='ca_type',
            field=models.CharField(default='wechat', max_length=10, verbose_name='\u8d26\u53f7\u7c7b\u522b', choices=[('wechat', '\u5fae\u4fe1\u94b1\u5305'), ('alipay', '\u652f\u4ed8\u5b9d'), ('deposit', '\u50a8\u84c4\u5361'), ('credit', '\u4fe1\u7528\u5361'), ('enterprise', '\u4f01\u4e1a\u8d26\u53f7'), ('other', '\u5176\u5b83')]),
        ),
    ]
