# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0004_auto_20160603_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logisticsvendor',
            name='province',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name=b'\xe6\x89\x80\xe5\x9c\xa8\xe7\x9c\x81/\xe7\x9b\xb4\xe8\xbe\x96\xe5\xb8\x82/\xe8\x87\xaa\xe6\xb2\xbb\xe5\x8c\xba', choices=[('\u5b89\u5fbd', '\u5b89\u5fbd'), ('\u6fb3\u95e8', '\u6fb3\u95e8'), ('\u5317\u4eac', '\u5317\u4eac'), ('\u91cd\u5e86', '\u91cd\u5e86'), ('\u798f\u5efa', '\u798f\u5efa'), ('\u7518\u8083', '\u7518\u8083'), ('\u5e7f\u4e1c', '\u5e7f\u4e1c'), ('\u5e7f\u897f', '\u5e7f\u897f'), ('\u8d35\u5dde', '\u8d35\u5dde'), ('\u6d77\u5357', '\u6d77\u5357'), ('\u6cb3\u5317', '\u6cb3\u5317'), ('\u6cb3\u5357', '\u6cb3\u5357'), ('\u9ed1\u9f99\u6c5f', '\u9ed1\u9f99\u6c5f'), ('\u6e56\u5317', '\u6e56\u5317'), ('\u6e56\u5357', '\u6e56\u5357'), ('\u5409\u6797', '\u5409\u6797'), ('\u6c5f\u82cf', '\u6c5f\u82cf'), ('\u6c5f\u897f', '\u6c5f\u897f'), ('\u8fbd\u5b81', '\u8fbd\u5b81'), ('\u5185\u8499\u53e4', '\u5185\u8499\u53e4'), ('\u5b81\u590f', '\u5b81\u590f'), ('\u9752\u6d77', '\u9752\u6d77'), ('\u5c71\u4e1c', '\u5c71\u4e1c'), ('\u5c71\u897f', '\u5c71\u897f'), ('\u9655\u897f', '\u9655\u897f'), ('\u4e0a\u6d77', '\u4e0a\u6d77'), ('\u56db\u5ddd', '\u56db\u5ddd'), ('\u53f0\u6e7e', '\u53f0\u6e7e'), ('\u5929\u6d25', '\u5929\u6d25'), ('\u897f\u85cf', '\u897f\u85cf'), ('\u9999\u6e2f', '\u9999\u6e2f'), ('\u65b0\u7586', '\u65b0\u7586'), ('\u4e91\u5357', '\u4e91\u5357'), ('\u6d59\u6c5f', '\u6d59\u6c5f')]),
        ),
        migrations.AlterField(
            model_name='manufacturer',
            name='province',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name=b'\xe6\x89\x80\xe5\x9c\xa8\xe7\x9c\x81/\xe7\x9b\xb4\xe8\xbe\x96\xe5\xb8\x82/\xe8\x87\xaa\xe6\xb2\xbb\xe5\x8c\xba', choices=[('\u5b89\u5fbd', '\u5b89\u5fbd'), ('\u6fb3\u95e8', '\u6fb3\u95e8'), ('\u5317\u4eac', '\u5317\u4eac'), ('\u91cd\u5e86', '\u91cd\u5e86'), ('\u798f\u5efa', '\u798f\u5efa'), ('\u7518\u8083', '\u7518\u8083'), ('\u5e7f\u4e1c', '\u5e7f\u4e1c'), ('\u5e7f\u897f', '\u5e7f\u897f'), ('\u8d35\u5dde', '\u8d35\u5dde'), ('\u6d77\u5357', '\u6d77\u5357'), ('\u6cb3\u5317', '\u6cb3\u5317'), ('\u6cb3\u5357', '\u6cb3\u5357'), ('\u9ed1\u9f99\u6c5f', '\u9ed1\u9f99\u6c5f'), ('\u6e56\u5317', '\u6e56\u5317'), ('\u6e56\u5357', '\u6e56\u5357'), ('\u5409\u6797', '\u5409\u6797'), ('\u6c5f\u82cf', '\u6c5f\u82cf'), ('\u6c5f\u897f', '\u6c5f\u897f'), ('\u8fbd\u5b81', '\u8fbd\u5b81'), ('\u5185\u8499\u53e4', '\u5185\u8499\u53e4'), ('\u5b81\u590f', '\u5b81\u590f'), ('\u9752\u6d77', '\u9752\u6d77'), ('\u5c71\u4e1c', '\u5c71\u4e1c'), ('\u5c71\u897f', '\u5c71\u897f'), ('\u9655\u897f', '\u9655\u897f'), ('\u4e0a\u6d77', '\u4e0a\u6d77'), ('\u56db\u5ddd', '\u56db\u5ddd'), ('\u53f0\u6e7e', '\u53f0\u6e7e'), ('\u5929\u6d25', '\u5929\u6d25'), ('\u897f\u85cf', '\u897f\u85cf'), ('\u9999\u6e2f', '\u9999\u6e2f'), ('\u65b0\u7586', '\u65b0\u7586'), ('\u4e91\u5357', '\u4e91\u5357'), ('\u6d59\u6c5f', '\u6d59\u6c5f')]),
        ),
        migrations.AlterField(
            model_name='store',
            name='province',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name=b'\xe6\x89\x80\xe5\x9c\xa8\xe7\x9c\x81/\xe7\x9b\xb4\xe8\xbe\x96\xe5\xb8\x82/\xe8\x87\xaa\xe6\xb2\xbb\xe5\x8c\xba', choices=[('\u5b89\u5fbd', '\u5b89\u5fbd'), ('\u6fb3\u95e8', '\u6fb3\u95e8'), ('\u5317\u4eac', '\u5317\u4eac'), ('\u91cd\u5e86', '\u91cd\u5e86'), ('\u798f\u5efa', '\u798f\u5efa'), ('\u7518\u8083', '\u7518\u8083'), ('\u5e7f\u4e1c', '\u5e7f\u4e1c'), ('\u5e7f\u897f', '\u5e7f\u897f'), ('\u8d35\u5dde', '\u8d35\u5dde'), ('\u6d77\u5357', '\u6d77\u5357'), ('\u6cb3\u5317', '\u6cb3\u5317'), ('\u6cb3\u5357', '\u6cb3\u5357'), ('\u9ed1\u9f99\u6c5f', '\u9ed1\u9f99\u6c5f'), ('\u6e56\u5317', '\u6e56\u5317'), ('\u6e56\u5357', '\u6e56\u5357'), ('\u5409\u6797', '\u5409\u6797'), ('\u6c5f\u82cf', '\u6c5f\u82cf'), ('\u6c5f\u897f', '\u6c5f\u897f'), ('\u8fbd\u5b81', '\u8fbd\u5b81'), ('\u5185\u8499\u53e4', '\u5185\u8499\u53e4'), ('\u5b81\u590f', '\u5b81\u590f'), ('\u9752\u6d77', '\u9752\u6d77'), ('\u5c71\u4e1c', '\u5c71\u4e1c'), ('\u5c71\u897f', '\u5c71\u897f'), ('\u9655\u897f', '\u9655\u897f'), ('\u4e0a\u6d77', '\u4e0a\u6d77'), ('\u56db\u5ddd', '\u56db\u5ddd'), ('\u53f0\u6e7e', '\u53f0\u6e7e'), ('\u5929\u6d25', '\u5929\u6d25'), ('\u897f\u85cf', '\u897f\u85cf'), ('\u9999\u6e2f', '\u9999\u6e2f'), ('\u65b0\u7586', '\u65b0\u7586'), ('\u4e91\u5357', '\u4e91\u5357'), ('\u6d59\u6c5f', '\u6d59\u6c5f')]),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='province',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name=b'\xe6\x89\x80\xe5\x9c\xa8\xe7\x9c\x81/\xe7\x9b\xb4\xe8\xbe\x96\xe5\xb8\x82/\xe8\x87\xaa\xe6\xb2\xbb\xe5\x8c\xba', choices=[('\u5b89\u5fbd', '\u5b89\u5fbd'), ('\u6fb3\u95e8', '\u6fb3\u95e8'), ('\u5317\u4eac', '\u5317\u4eac'), ('\u91cd\u5e86', '\u91cd\u5e86'), ('\u798f\u5efa', '\u798f\u5efa'), ('\u7518\u8083', '\u7518\u8083'), ('\u5e7f\u4e1c', '\u5e7f\u4e1c'), ('\u5e7f\u897f', '\u5e7f\u897f'), ('\u8d35\u5dde', '\u8d35\u5dde'), ('\u6d77\u5357', '\u6d77\u5357'), ('\u6cb3\u5317', '\u6cb3\u5317'), ('\u6cb3\u5357', '\u6cb3\u5357'), ('\u9ed1\u9f99\u6c5f', '\u9ed1\u9f99\u6c5f'), ('\u6e56\u5317', '\u6e56\u5317'), ('\u6e56\u5357', '\u6e56\u5357'), ('\u5409\u6797', '\u5409\u6797'), ('\u6c5f\u82cf', '\u6c5f\u82cf'), ('\u6c5f\u897f', '\u6c5f\u897f'), ('\u8fbd\u5b81', '\u8fbd\u5b81'), ('\u5185\u8499\u53e4', '\u5185\u8499\u53e4'), ('\u5b81\u590f', '\u5b81\u590f'), ('\u9752\u6d77', '\u9752\u6d77'), ('\u5c71\u4e1c', '\u5c71\u4e1c'), ('\u5c71\u897f', '\u5c71\u897f'), ('\u9655\u897f', '\u9655\u897f'), ('\u4e0a\u6d77', '\u4e0a\u6d77'), ('\u56db\u5ddd', '\u56db\u5ddd'), ('\u53f0\u6e7e', '\u53f0\u6e7e'), ('\u5929\u6d25', '\u5929\u6d25'), ('\u897f\u85cf', '\u897f\u85cf'), ('\u9999\u6e2f', '\u9999\u6e2f'), ('\u65b0\u7586', '\u65b0\u7586'), ('\u4e91\u5357', '\u4e91\u5357'), ('\u6d59\u6c5f', '\u6d59\u6c5f')]),
        ),
    ]
