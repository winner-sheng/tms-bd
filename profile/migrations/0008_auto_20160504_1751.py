# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0007_auto_20160504_0940'),
    ]

    operations = [
        migrations.CreateModel(
            name='WithdrawRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(max_length=32, verbose_name='\u7528\u6237UID', db_index=True)),
                ('ca_no', models.CharField(help_text='\u63d0\u73b0\u5230\u6307\u5b9a\u8d44\u91d1\u8d26\u53f7\uff0c\u5982\u679c\u662f\u5fae\u4fe1\u94b1\u5305\uff0c\u5219\u4e3a\u7528\u6237openid', unique=True, max_length=32, verbose_name='\u8d44\u91d1\u5e10\u53f7')),
                ('ca_type', models.CharField(default=b'wechat', max_length=10, verbose_name='\u8d26\u53f7\u7c7b\u522b', choices=[(b'wechat', '\u5fae\u4fe1\u94b1\u5305'), (b'alipay', '\u652f\u4ed8\u5b9d'), (b'bank', '\u50a8\u84c4\u5361'), (b'credit', '\u4fe1\u7528\u5361'), (b'other', '\u5176\u5b83')])),
                ('bank_name', models.CharField(max_length=30, null=True, verbose_name='\u94f6\u884c\u540d\u79f0', blank=True)),
                ('bank_code', models.CharField(max_length=20, null=True, verbose_name='\u94f6\u884c\u7f16\u7801', blank=True)),
                ('open_bank', models.CharField(max_length=50, null=True, verbose_name='\u5f00\u6237\u884c\u540d\u79f0', blank=True)),
                ('amount', models.DecimalField(default=0, help_text='\u63d0\u73b0\u91d1\u989d\u4e0d\u5f97\u8d85\u8fc7\u7528\u6237\u8d26\u6237\u603b\u989d', verbose_name='\u63d0\u73b0\u91d1\u989d', max_digits=10, decimal_places=2)),
                ('status', models.PositiveSmallIntegerField(default=0, verbose_name='\u63d0\u73b0\u7ed3\u679c')),
                ('result', models.CharField(max_length=200, null=True, verbose_name='\u63d0\u73b0\u7ed3\u679c\u8bf4\u660e', blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4', null=True)),
            ],
            options={
                'verbose_name': '\u7528\u6237\u63d0\u73b0\u7533\u8bf7\u8bb0\u5f55',
                'verbose_name_plural': '\u7528\u6237\u63d0\u73b0\u7533\u8bf7\u8bb0\u5f55',
            },
        ),
        migrations.AlterField(
            model_name='usercapitalaccount',
            name='ca_no',
            field=models.CharField(help_text='\u5982\u679c\u662f\u5fae\u4fe1\u94b1\u5305\uff0c\u5219\u4e3a\u7528\u6237openid', unique=True, max_length=32, verbose_name=b'\xe8\xb5\x84\xe9\x87\x91\xe5\xb8\x90\xe5\x8f\xb7'),
        ),
        migrations.AlterField(
            model_name='usercapitalaccount',
            name='ca_type',
            field=models.CharField(default=b'wechat', max_length=10, verbose_name=b'\xe8\xb4\xa6\xe5\x8f\xb7\xe7\xb1\xbb\xe5\x88\xab', choices=[(b'wechat', '\u5fae\u4fe1\u94b1\u5305'), (b'alipay', '\u652f\u4ed8\u5b9d'), (b'bank', '\u50a8\u84c4\u5361'), (b'credit', '\u4fe1\u7528\u5361'), (b'other', '\u5176\u5b83')]),
        ),
        migrations.AlterField(
            model_name='withdrawrequest',
            name='ca_no',
            field=models.CharField(help_text='\u63d0\u73b0\u5230\u6307\u5b9a\u8d44\u91d1\u8d26\u53f7\uff0c\u5982\u679c\u662f\u5fae\u4fe1\u94b1\u5305\uff0c\u5219\u4e3a\u7528\u6237openid', max_length=32, verbose_name='\u8d44\u91d1\u5e10\u53f7', db_index=True),
        ),
        migrations.AlterField(
            model_name='withdrawrequest',
            name='status',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='\u63d0\u73b0\u7ed3\u679c', choices=[(0, '\u5904\u7406\u4e2d'), (1, '\u5b8c\u6210'), (2, '\u63d0\u73b0\u5931\u8d25')]),
        ),
        migrations.AddField(
            model_name='withdrawrequest',
            name='account_no',
            field=models.CharField(db_index=True, max_length=32, null=True, verbose_name=b'\xe6\xb5\x81\xe6\xb0\xb4\xe5\x8f\xb7', blank=True),
        ),
        migrations.AlterField(
            model_name='useraccountbook',
            name='type',
            field=models.CharField(default=b'other', max_length=10, verbose_name=b'\xe8\xb4\xa6\xe7\x9b\xae\xe7\xb1\xbb\xe5\x88\xab', choices=[(b'allowance', '\u8865\u8d34'), (b'bonus', '\u5956\u52b1'), (b'charge', '\u5145\u503c'), (b'expense', '\u6d88\u8d39\u652f\u51fa'), (b'penalty', '\u7f5a\u6b3e'), (b'reward', '\u56de\u4f63'), (b'roll-in', '\u8f6c\u5165'), (b'roll-out', '\u8f6c\u51fa'), (b'withdraw', '\u63d0\u73b0'), (b'deduct', '\u6263\u9664'), (b'other', '\u5176\u5b83')]),
        ),
    ]
