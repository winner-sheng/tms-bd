# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import promote.models


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0016_auto_20161123_1741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='couponruleset',
            name='code',
            field=models.CharField(primary_key=True, default=promote.models._set_code, serialize=False, max_length=32, help_text='\u7528\u4e8e\u5f15\u7528', verbose_name='\u5957\u9910\u7f16\u7801'),
        ),
    ]
