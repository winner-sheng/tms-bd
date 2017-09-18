# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0010_auto_20160511_2325'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccountbook',
            name='trans_no',
            field=models.CharField(help_text='\u6536\u4ed8\u6b3e\u65f6\uff0c\u7b2c\u4e09\u65b9\u652f\u4ed8\u63a5\u53e3\u8fd4\u56de\u7684\u4ea4\u6613\u5355\u53f7', max_length=32, null=True, verbose_name='\u4ea4\u6613\u5355\u53f7', blank=True),
        ),
    ]
