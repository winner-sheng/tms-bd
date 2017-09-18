# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logistic', '0005_auto_20160726_2007'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipitem',
            name='code',
            field=models.CharField('编码', default='', null=False, max_length=36),
        ),
        migrations.RunSQL('update logistic_shipitem set code = concat(package_no, ":", prd_code);'),
        migrations.AlterField(
            model_name='shipitem',
            name='code',
            field=models.CharField('编码', null=False, max_length=36, primary_key=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='shipitem',
            name='package_no',
            field=models.CharField(max_length=20, verbose_name='\u5305\u88f9\u7f16\u53f7', db_index=True),
        ),
    ]
