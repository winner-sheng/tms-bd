# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import buding.models


class Migration(migrations.Migration):

    dependencies = [
        ('buding', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='saleshop',
            name='id',
        ),
        migrations.RemoveField(
            model_name='saleshop',
            name='shopkeeperuid',
        ),
        migrations.AddField(
            model_name='saleshop',
            name='uid',
            field=models.CharField(max_length=32, blank=True, help_text='\u5e97\u4e3bUID', null=True, verbose_name='\u5e97\u4e3bUID', db_index=True),
        ),
        migrations.AlterField(
            model_name='saleshop',
            name='code',
            field=models.CharField(primary_key=True, default=buding.models._default_shop_code, serialize=False, max_length=16, help_text='\u5e97\u94fa\u4ee3\u7801', verbose_name='\u5e97\u94fa\u4ee3\u7801'),
        ),
        migrations.AlterField(
            model_name='saleshopproduct',
            name='productid',
            field=models.CharField(help_text='\u5546\u54c1\u4ee3\u7801', max_length=32, verbose_name='\u5546\u54c1\u4ee3\u7801'),
        ),
        migrations.AlterField(
            model_name='saleshopproduct',
            name='shopcode',
            field=models.CharField(help_text='\u5e97\u94fa\u4ee3\u7801', max_length=16, verbose_name='\u5e97\u94fa\u4ee3\u7801', db_index=True),
        ),
        migrations.AlterField(
            model_name='shopmanagerinfo',
            name='shopcode',
            field=models.CharField(default='', help_text='\u5e97\u94fa\u4ee3\u7801', max_length=16, verbose_name='\u5e97\u94fa\u4ee3\u7801', db_index=True),
        ),
    ]
