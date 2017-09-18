# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0019_auto_20160930_1743'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='withdrawrequest',
            name='bank_code',
        ),
        migrations.RemoveField(
            model_name='withdrawrequest',
            name='bank_name',
        ),
        migrations.RemoveField(
            model_name='withdrawrequest',
            name='open_bank',
        ),
        migrations.AddField(
            model_name='usercapitalaccount',
            name='ca_mobile',
            field=models.CharField(help_text='\u5728\u94f6\u884c\u5f00\u6237\u65f6\u9884\u7559\u7684\u624b\u673a\u53f7', max_length=15, null=True, verbose_name='\u9884\u7559\u624b\u673a\u53f7', blank=True),
        ),
        migrations.AddField(
            model_name='usercapitalaccount',
            name='ca_name',
            field=models.CharField(help_text='\u4ec5\u7528\u4e8e\u94f6\u884c\u8d26\u6237', max_length=50, null=True, verbose_name='\u5f00\u6237\u540d\u79f0', blank=True),
        ),
        migrations.AlterField(
            model_name='usercapitalaccount',
            name='ca_type',
            field=models.CharField(default='wechat', max_length=10, verbose_name='\u8d26\u53f7\u7c7b\u522b', choices=[('wechat', '\u5fae\u4fe1\u94b1\u5305'), ('alipay', '\u652f\u4ed8\u5b9d'), ('deposit', '\u50a8\u84c4\u5361'), ('credit', '\u4fe1\u7528\u5361'), ('other', '\u5176\u5b83')]),
        ),
        migrations.AlterField(
            model_name='usercapitalaccount',
            name='uid',
            field=models.CharField(help_text='\u5916\u90e8\u7528\u6237\u586b\u5199\u7528\u6237uid\uff0c\u5185\u90e8\u4f9b\u5e94\u5546\u586b\u5199\u201cSUP-\u4f9b\u5e94\u5546\u7f16\u7801\u201d', max_length=32, verbose_name='\u7528\u6237UID', db_index=True),
        ),
        migrations.AlterField(
            model_name='withdrawrequest',
            name='amount',
            field=models.DecimalField(default=0, help_text='\u63d0\u73b0\u91d1\u989d\u4e0d\u5f97\u8d85\u8fc7\u5f53\u65f6\u7528\u6237\u8d26\u6237\u53ef\u7528\u4f59\u989d', verbose_name='\u63d0\u73b0\u91d1\u989d', max_digits=10, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='withdrawrequest',
            name='ca_type',
            field=models.CharField(default='wechat', max_length=10, verbose_name='\u8d26\u53f7\u7c7b\u522b', choices=[('wechat', '\u5fae\u4fe1\u94b1\u5305'), ('alipay', '\u652f\u4ed8\u5b9d'), ('deposit', '\u50a8\u84c4\u5361'), ('credit', '\u4fe1\u7528\u5361'), ('other', '\u5176\u5b83')]),
        ),
    ]
