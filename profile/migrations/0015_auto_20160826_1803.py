# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0014_auto_20160824_2215'),
    ]

    operations = [
        migrations.AddField(
            model_name='enduserenterprise',
            name='address',
            field=models.CharField(max_length=100, null=True, verbose_name='\u5730\u5740', blank=True),
        ),
        migrations.AddField(
            model_name='enduserenterprise',
            name='city',
            field=models.CharField(max_length=10, null=True, verbose_name='\u6240\u5728\u57ce\u5e02', blank=True),
        ),
        migrations.AddField(
            model_name='enduserenterprise',
            name='geo_hash',
            field=models.CharField(db_index=True, max_length=16, null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='enduserenterprise',
            name='lat',
            field=models.FloatField(default=0, null=True, verbose_name='\u7eac\u5ea6', blank=True),
        ),
        migrations.AddField(
            model_name='enduserenterprise',
            name='lng',
            field=models.FloatField(default=0, null=True, verbose_name='\u7ecf\u5ea6', blank=True),
        ),
        migrations.AddField(
            model_name='enduserenterprise',
            name='post_code',
            field=models.CharField(max_length=8, null=True, verbose_name='\u90ae\u7f16', blank=True),
        ),
        migrations.AddField(
            model_name='enduserenterprise',
            name='province',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='\u6240\u5728\u7701/\u76f4\u8f96\u5e02/\u81ea\u6cbb\u533a', choices=[('\u5b89\u5fbd', '\u5b89\u5fbd'), ('\u6fb3\u95e8', '\u6fb3\u95e8'), ('\u5317\u4eac', '\u5317\u4eac'), ('\u91cd\u5e86', '\u91cd\u5e86'), ('\u798f\u5efa', '\u798f\u5efa'), ('\u7518\u8083', '\u7518\u8083'), ('\u5e7f\u4e1c', '\u5e7f\u4e1c'), ('\u5e7f\u897f', '\u5e7f\u897f'), ('\u8d35\u5dde', '\u8d35\u5dde'), ('\u6d77\u5357', '\u6d77\u5357'), ('\u6cb3\u5317', '\u6cb3\u5317'), ('\u6cb3\u5357', '\u6cb3\u5357'), ('\u9ed1\u9f99\u6c5f', '\u9ed1\u9f99\u6c5f'), ('\u6e56\u5317', '\u6e56\u5317'), ('\u6e56\u5357', '\u6e56\u5357'), ('\u5409\u6797', '\u5409\u6797'), ('\u6c5f\u82cf', '\u6c5f\u82cf'), ('\u6c5f\u897f', '\u6c5f\u897f'), ('\u8fbd\u5b81', '\u8fbd\u5b81'), ('\u5185\u8499\u53e4', '\u5185\u8499\u53e4'), ('\u5b81\u590f', '\u5b81\u590f'), ('\u9752\u6d77', '\u9752\u6d77'), ('\u5c71\u4e1c', '\u5c71\u4e1c'), ('\u5c71\u897f', '\u5c71\u897f'), ('\u9655\u897f', '\u9655\u897f'), ('\u4e0a\u6d77', '\u4e0a\u6d77'), ('\u56db\u5ddd', '\u56db\u5ddd'), ('\u53f0\u6e7e', '\u53f0\u6e7e'), ('\u5929\u6d25', '\u5929\u6d25'), ('\u897f\u85cf', '\u897f\u85cf'), ('\u9999\u6e2f', '\u9999\u6e2f'), ('\u65b0\u7586', '\u65b0\u7586'), ('\u4e91\u5357', '\u4e91\u5357'), ('\u6d59\u6c5f', '\u6d59\u6c5f')]),
        ),
        migrations.AlterField(
            model_name='enduserrole',
            name='role',
            field=models.CharField(default='staff', max_length=10, verbose_name='\u7528\u6237\u89d2\u8272', choices=[('sp', '\u8d85\u7ea7\u7ba1\u7406\u5458'), ('admin', '\u7ba1\u7406\u5458'), ('staff', '\u804c\u5458')]),
        ),
    ]
