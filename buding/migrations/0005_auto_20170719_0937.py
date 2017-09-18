# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buding', '0004_auto_20170713_1721'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopmanagerinfo',
            name='is_active',
            field=models.BooleanField(default=True, help_text='\u662f\u5426\u6709\u6548\uff0c\u63a8\u8350\u4eba\u5173\u7cfb\u5220\u9664\u7684\u8bdd\uff0c\u5c06\u7f6e\u4e3aFalse', verbose_name='\u662f\u5426\u6709\u6548'),
        ),
        migrations.AlterField(
            model_name='shopmanagerinfo',
            name='pid',
            field=models.CharField(help_text='\u63a8\u8350\u4eba\u7684UID', max_length=32, verbose_name='\u63a8\u8350\u4ebaUID', db_index=True),
        ),
        migrations.AlterField(
            model_name='shopmanagerinfo',
            name='uid',
            field=models.CharField(help_text='\u5e03\u4e01\u5e10\u53f7\u7cfb\u7edf\u7684\u7528\u6237UID', max_length=32, verbose_name='\u7528\u6237UID', db_index=True),
        ),
    ]
