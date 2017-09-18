# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0009_auto_20160505_1204'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='couponticket',
            options={'ordering': ['-get_time'], 'verbose_name': '\u4f18\u60e0\u6d3b\u52a8-\u4f18\u60e0\u5238', 'verbose_name_plural': '\u4f18\u60e0\u6d3b\u52a8-\u4f18\u60e0\u5238'},
        ),
        migrations.AlterModelOptions(
            name='rewardrecord',
            options={'ordering': ['-create_time'], 'verbose_name': '\u7528\u6237\u63a8\u5e7f\u6536\u76ca\u8bb0\u5f55', 'verbose_name_plural': '\u7528\u6237\u63a8\u5e7f\u6536\u76ca\u8bb0\u5f55'},
        ),
        migrations.AddField(
            model_name='couponrule',
            name='most_tickets',
            field=models.PositiveSmallIntegerField(default=10, help_text='\u9ed8\u8ba4\u7528\u6237\u6700\u591a\u53ef\u4ee5\u9886\u53d6\u540c\u7c7b\u4f18\u60e0\u5238\u7684\u6570\u91cf\uff0c\u9ed8\u8ba4\u4e3a10', null=True, verbose_name='\u6700\u591a\u53ef\u9886\u5238\u6570\u91cf', blank=True),
        ),
        migrations.AddField(
            model_name='couponrule',
            name='tickets_onetime',
            field=models.PositiveSmallIntegerField(default=1, help_text='\u9ed8\u8ba4\u7528\u6237\u6bcf\u6b21\u53ef\u4ee5\u9886\u53d6\u540c\u7c7b\u4f18\u60e0\u5238\u7684\u6570\u91cf\uff0c\u6700\u5c0f\u4e3a1', null=True, verbose_name='\u6bcf\u6b21\u53ef\u9886\u5238\u6570\u91cf', blank=True),
        ),
        migrations.AddField(
            model_name='rewardrecord',
            name='reward_type',
            field=models.PositiveSmallIntegerField(default=0, null=True, verbose_name='\u6536\u76ca\u7c7b\u578b', blank=True, choices=[(0, '\u9500\u552e\u56de\u4f63'), (1, '\u4f19\u4f34\u6fc0\u52b1')]),
        ),
        migrations.AlterField(
            model_name='couponrule',
            name='allow_addon',
            field=models.BooleanField(default=False, help_text='\u662f\u5426\u5141\u8bb8\u4e0e\u5176\u4ed6\u8d2d\u7269\u4f18\u60e0\u89c4\u5219\uff08\u975e\u4f18\u60e0\u5238\uff09\u53e0\u52a0\u4f7f\u7528', verbose_name='\u5141\u8bb8\u53e0\u52a0'),
        ),
        migrations.AlterField(
            model_name='couponrule',
            name='applied_to_products',
            field=models.CharField(default=b'', max_length=500, blank=True, help_text='\u586b\u5199\u5546\u54c1\u7f16\u53f7\uff0c\u591a\u4e2a\u5546\u54c1\u7528\u82f1\u6587\u9017\u53f7\u5206\u9694\uff0c\u7559\u7a7a\u5219\u4e0d\u4f5c\u9650\u5236', null=True, verbose_name='\u9002\u7528\u5546\u54c1\u5217\u8868'),
        ),
        migrations.AlterField(
            model_name='couponrule',
            name='applied_to_stores',
            field=models.CharField(default=b'', max_length=500, blank=True, help_text='\u586b\u5199\u5e97\u94fa\u7f16\u53f7\uff0c\u591a\u4e2a\u5e97\u94fa\u7528\u82f1\u6587\u9017\u53f7\u5206\u9694\uff0c\u7559\u7a7a\u5219\u4e0d\u4f5c\u9650\u5236', null=True, verbose_name='\u9002\u7528\u5e97\u94fa\u5217\u8868'),
        ),
        migrations.AlterField(
            model_name='couponrule',
            name='applied_to_suppliers',
            field=models.CharField(default=b'', max_length=500, blank=True, help_text='\u586b\u5199\u4f9b\u5e94\u5546\u7f16\u7801\uff0c\u591a\u4e2a\u4f9b\u5e94\u5546\u7528\u82f1\u6587\u9017\u53f7\u5206\u9694\uff0c\u7559\u7a7a\u5219\u4e0d\u4f5c\u9650\u5236', null=True, verbose_name='\u9002\u7528\u4f9b\u5e94\u5546\u5217\u8868'),
        ),
        migrations.AlterField(
            model_name='couponrule',
            name='pub_number',
            field=models.PositiveIntegerField(default=100, null=True, verbose_name='\u4f18\u60e0\u5238\u53d1\u884c\u6570\u91cf', blank=True),
        ),
        migrations.AlterField(
            model_name='couponrule',
            name='repeatable',
            field=models.BooleanField(default=False, help_text='\u540c\u4e00\u8ba2\u5355\u662f\u5426\u5141\u8bb8\u4f7f\u7528\u591a\u5f20\u4f18\u60e0\u5238', verbose_name='\u5141\u8bb8\u591a\u5f20'),
        ),
        migrations.AlterField(
            model_name='rewardrecord',
            name='order_no',
            field=models.CharField(max_length=20, verbose_name='\u63a8\u5e7f\u8ba2\u5355\u53f7'),
        ),
    ]
