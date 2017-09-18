# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filemgmt', '0002_auto_20160817_1013'),
        ('credit', '0002_auto_20161107_1828'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedalCatalog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=20, verbose_name='\u7f16\u7801')),
                ('name', models.CharField(max_length=20, verbose_name='\u540d\u79f0')),
                ('threshold', models.PositiveIntegerField(default=1, help_text='\u6bd4\u5982\u8ba2\u5355\u7ed3\u7b97\u8fbe\u523010000\u5143\uff0c\u56de\u7b54\u95ee\u7b54\u6570\u91cf\u8fbe\u523050\u6b21\u7b49', verbose_name='\u83b7\u53d6\u6761\u4ef6\u9608\u503c')),
                ('remark', models.CharField(max_length=512, verbose_name='\u8bf4\u660e')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4', null=True)),
                ('create_by', models.CharField(help_text='\u5bf9\u4e8e\u901a\u8fc7\u540e\u53f0\u7ba1\u7406\u5165\u53e3\u6dfb\u52a0\u8005\uff0c\u8bb0\u5f55\u7528\u6237\u4fe1\u606f"', max_length=32, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4', null=True)),
                ('update_by', models.CharField(help_text='\u5bf9\u4e8e\u901a\u8fc7\u540e\u53f0\u7ba1\u7406\u5165\u53e3\u6dfb\u52a0\u8005\uff0c\u8bb0\u5f55\u7528\u6237\u4fe1\u606f"', max_length=32, null=True, verbose_name='\u66f4\u65b0\u4eba', blank=True)),
                ('image', models.ForeignKey(related_name='+', verbose_name='\u52cb\u7ae0\u56fe\u7247', to='filemgmt.BaseImage', help_text='\u52cb\u7ae0\u5bf9\u5e94\u7684\u56fe\u7247')),
            ],
            options={
                'verbose_name': '\u52cb\u7ae0\u76ee\u5f55',
                'verbose_name_plural': '\u52cb\u7ae0\u76ee\u5f55',
            },
        ),
        migrations.CreateModel(
            name='RankSeries',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20, verbose_name='\u7cfb\u5217\u540d\u79f0')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4', null=True)),
                ('create_by', models.CharField(help_text='\u5bf9\u4e8e\u901a\u8fc7\u540e\u53f0\u7ba1\u7406\u5165\u53e3\u6dfb\u52a0\u8005\uff0c\u8bb0\u5f55\u7528\u6237\u4fe1\u606f"', max_length=32, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4', null=True)),
                ('update_by', models.CharField(help_text='\u5bf9\u4e8e\u901a\u8fc7\u540e\u53f0\u7ba1\u7406\u5165\u53e3\u6dfb\u52a0\u8005\uff0c\u8bb0\u5f55\u7528\u6237\u4fe1\u606f"', max_length=32, null=True, verbose_name='\u66f4\u65b0\u4eba', blank=True)),
            ],
            options={
                'verbose_name': '\u7b49\u7ea7\u7cfb\u5217',
                'verbose_name_plural': '\u7b49\u7ea7\u7cfb\u5217',
            },
        ),
        migrations.CreateModel(
            name='RankTitle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20, verbose_name='\u7b49\u7ea7\u540d\u79f0')),
                ('left_value', models.PositiveIntegerField(default=0, help_text='\u5373\u8be5\u7b49\u7ea7\u5bf9\u5e94\u7684\u6307\u6807\u4e0b\u9650\uff0c\u5927\u4e8e\u8be5\u6307\u6807\u5219\u4e3a\u8be5\u6307\u5b9a\u79f0\u53f7', verbose_name='\u6307\u6807\u4e0b\u9650')),
                ('right_value', models.PositiveIntegerField(default=0, help_text='\u5373\u8be5\u7b49\u7ea7\u5bf9\u5e94\u7684\u6307\u6807\u4e0a\u9650\uff0c\u5927\u4e8e\u8be5\u6307\u6807\u5219\u4e3a\u4e0a\u4e00\u7ea7\u6307\u5b9a\u79f0\u53f7', verbose_name='\u6307\u6807\u4e0a\u4e0b\u9650')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4', null=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4', null=True)),
                ('image', models.ForeignKey(related_name='+', blank=True, to='filemgmt.BaseImage', help_text='\u7b49\u7ea7\u5bf9\u5e94\u7684\u56fe\u7247\uff0c\u53ef\u4ee5\u6ca1\u6709', null=True, verbose_name='\u7b49\u7ea7\u56fe\u7247')),
                ('series', models.ForeignKey(help_text='\u6240\u5c5e\u7b49\u7ea7\u7cfb\u5217', to='credit.RankSeries')),
            ],
            options={
                'verbose_name': '\u7b49\u7ea7\u540d\u79f0',
                'verbose_name_plural': '\u7b49\u7ea7\u540d\u79f0',
            },
        ),
        migrations.CreateModel(
            name='UserMedal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(help_text='\u5bf9\u4e8e\u666e\u901a\u7528\u6237\u662f\u7528\u6237\u7684UID\uff0c\u5bf9\u4e8e\u4f9b\u5e94\u5546\uff0c\u5219\u662f"SUP-"\u524d\u7f00 + \u4f9b\u5e94\u5546\u7f16\u7801\uff0c\u5982"SUP-TWOHOU"', max_length=32, verbose_name='\u7528\u6237UID', db_index=True)),
                ('grant_time', models.DateTimeField(auto_now=True, verbose_name='\u6388\u4e88\u65f6\u95f4', null=True)),
                ('medal', models.ForeignKey(help_text='\u7528\u6237\u83b7\u5f97\u7684\u52cb\u7ae0', to='credit.MedalCatalog')),
            ],
            options={
                'verbose_name': '\u7528\u6237\u52cb\u7ae0',
                'verbose_name_plural': '\u7528\u6237\u52cb\u7ae0',
            },
        ),
        migrations.CreateModel(
            name='UserTitle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(help_text='\u5bf9\u4e8e\u666e\u901a\u7528\u6237\u662f\u7528\u6237\u7684UID\uff0c\u5bf9\u4e8e\u4f9b\u5e94\u5546\uff0c\u5219\u662f"SUP-"\u524d\u7f00 + \u4f9b\u5e94\u5546\u7f16\u7801\uff0c\u5982"SUP-TWOHOU"', max_length=32, verbose_name='\u7528\u6237UID', db_index=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4', null=True)),
                ('series', models.ForeignKey(help_text='\u6240\u5c5e\u7b49\u7ea7\u7cfb\u5217', to='credit.RankSeries')),
            ],
            options={
                'verbose_name': '\u7528\u6237\u79f0\u53f7',
                'verbose_name_plural': '\u7528\u6237\u79f0\u53f7',
            },
        ),
        migrations.AlterField(
            model_name='creditbook',
            name='figure',
            field=models.PositiveIntegerField(default=0, help_text='\u51fa/\u5165\u8d26\u5747\u8ba1\u5165\u6b64\u680f\uff0c\u6b63\u503c\u8868\u793a\u6536\u5165\uff0c\u8d1f\u503c\u8868\u793a\u652f\u51fa', verbose_name='\u5165\u8d26\u79ef\u5206'),
        ),
        migrations.AlterField(
            model_name='creditbook',
            name='source',
            field=models.CharField(help_text='\u8bf4\u660e\u79ef\u5206\u7684\u6765\u6e90\u4fe1\u606f\uff0c\u6bd4\u5982\u67d0\u4e2a\u4efb\u52a1\u5956\u52b1', max_length=200, verbose_name='\u79ef\u5206\u6765\u6e90'),
        ),
    ]
