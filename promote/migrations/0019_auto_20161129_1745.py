# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ueditor.models


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0018_auto_20161127_1155'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='couponruleset',
            options={'ordering': ['-pk'], 'verbose_name': '\u4f18\u60e0\u6d3b\u52a8\u7ec4\u5408(\u9886\u5238\u7528)', 'verbose_name_plural': '\u4f18\u60e0\u6d3b\u52a8\u7ec4\u5408(\u9886\u5238\u7528)'},
        ),
        migrations.AlterModelOptions(
            name='rulesetmap',
            options={'ordering': ['-list_order'], 'verbose_name': '\u7ec4\u5408\u6d3b\u52a8\u5173\u7cfb\u8868', 'verbose_name_plural': '\u7ec4\u5408\u6d3b\u52a8\u5173\u7cfb\u8868'},
        ),
        migrations.AlterField(
            model_name='couponruleset',
            name='code',
            field=models.CharField(primary_key=True, serialize=False, max_length=32, blank=True, help_text='\u7528\u4e8e\u5f15\u7528\uff0c\u5982\u679c\u4e0d\u586b\u5199\u5219\u7531\u7cfb\u7edf\u81ea\u52a8\u751f\u6210\u3002\u6ce8\u610f\uff1a\u586b\u5199\u540e\u5c06\u4e0d\u80fd\u518d\u4fee\u6539\uff01', verbose_name='\u7ec4\u5408\u7f16\u7801'),
        ),
        migrations.AlterField(
            model_name='couponruleset',
            name='description',
            field=ueditor.models.UEditorField(max_length=5000, null=True, verbose_name='\u7ec4\u5408\u4ecb\u7ecd', blank=True),
        ),
        migrations.AlterField(
            model_name='couponruleset',
            name='link_page',
            field=models.CharField(help_text='\u4ec5\u5f53\u5b58\u5728\u5916\u90e8\u4e13\u9898\u9875\u9762\u65f6\u4f7f\u7528', max_length=512, null=True, verbose_name='\u7ec4\u5408\u4e13\u9898\u9875url', blank=True),
        ),
        migrations.AlterField(
            model_name='couponruleset',
            name='name',
            field=models.CharField(help_text='\u6bd4\u5982\uff1a\u6ee1100\u51cf10\u5143', max_length=50, verbose_name='\u7ec4\u5408\u540d\u79f0'),
        ),
        migrations.AlterField(
            model_name='rulesetmap',
            name='rule_set',
            field=models.ForeignKey(related_name='rules', verbose_name='\u7ec4\u5408', to='promote.CouponRuleSet'),
        ),
    ]
