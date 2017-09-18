# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import promote.models
import datetime
import django.db.models.deletion
import ueditor.models


class Migration(migrations.Migration):

    dependencies = [
        ('filemgmt', '0003_auto_20161122_2004'),
        ('promote', '0015_auto_20161031_2058'),
    ]

    operations = [
        migrations.CreateModel(
            name='CouponRuleSet',
            fields=[
                ('code', models.CharField(primary_key=True, default=promote.models._set_code, serialize=False, max_length=12, help_text='\u7528\u4e8e\u5f15\u7528', verbose_name='\u5957\u9910\u7f16\u7801')),
                ('name', models.CharField(help_text='\u6bd4\u5982\uff1a\u6ee1100\u51cf10\u5143', max_length=50, verbose_name='\u5957\u9910\u540d\u79f0')),
                ('link_page', models.CharField(help_text='\u4ec5\u5f53\u5b58\u5728\u5916\u90e8\u4e13\u9898\u9875\u9762\u65f6\u4f7f\u7528', max_length=512, null=True, verbose_name='\u5957\u9910\u4e13\u9898\u9875url', blank=True)),
                ('description', ueditor.models.UEditorField(max_length=5000, null=True, verbose_name='\u5957\u9910\u4ecb\u7ecd', blank=True)),
                ('start_time', models.DateTimeField(default=datetime.datetime.now, null=True, verbose_name='\u6709\u6548\u671f\u5f00\u59cb\u65f6\u95f4', blank=True)),
                ('end_time', models.DateTimeField(null=True, verbose_name='\u6709\u6548\u671f\u7ed3\u675f\u65f6\u95f4', blank=True)),
                ('create_time', models.DateTimeField(auto_now=True, verbose_name='\u521b\u5efa\u65f6\u95f4', null=True)),
                ('create_by', models.CharField(verbose_name='\u521b\u5efa\u4eba', max_length=32, null=True, editable=False, blank=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4', null=True)),
                ('update_by', models.CharField(verbose_name='\u66f4\u65b0\u4eba', max_length=32, null=True, editable=False, blank=True)),
                ('image', models.ForeignKey(related_name='+', verbose_name='\u5957\u9910\u56fe\u7247', blank=True, to='filemgmt.BaseImage', null=True)),
            ],
            options={
                'ordering': ['-pk'],
                'verbose_name': '\u4f18\u60e0\u5957\u9910',
                'verbose_name_plural': '\u4f18\u60e0\u5957\u9910',
            },
        ),
        migrations.CreateModel(
            name='RuleSetMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.PositiveSmallIntegerField(default=1, verbose_name='\u4f18\u60e0\u5238\u6570\u91cf')),
                ('list_order', models.PositiveIntegerField(default=0, help_text='\u6570\u503c\u8d8a\u5927\uff0c\u6392\u5e8f\u8d8a\u9760\u524d', verbose_name='\u6392\u5e8f\u6807\u8bb0')),
            ],
            options={
                'ordering': ['-list_order'],
                'verbose_name': '\u5957\u9910\u6d3b\u52a8\u5173\u7cfb\u8868',
                'verbose_name_plural': '\u5957\u9910\u6d3b\u52a8\u5173\u7cfb\u8868',
            },
        ),
        migrations.AlterModelOptions(
            name='couponticket',
            options={'ordering': ['-get_time'], 'verbose_name': '\u4f18\u60e0\u6d3b\u52a8 - \u4f18\u60e0\u5238', 'verbose_name_plural': '\u4f18\u60e0\u6d3b\u52a8 - \u4f18\u60e0\u5238'},
        ),
        migrations.AlterField(
            model_name='couponrule',
            name='update_by',
            field=models.CharField(verbose_name='\u66f4\u65b0\u4eba', max_length=32, null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='rulesetmap',
            name='rule',
            field=models.ForeignKey(related_name='rulesets', on_delete=django.db.models.deletion.PROTECT, verbose_name='\u4f18\u60e0\u6d3b\u52a8', to='promote.CouponRule'),
        ),
        migrations.AddField(
            model_name='rulesetmap',
            name='rule_set',
            field=models.ForeignKey(related_name='rules', verbose_name='\u5957\u9910', to='promote.CouponRuleSet'),
        ),
    ]
