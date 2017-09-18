# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('filemgmt', '0003_auto_20161122_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseimage',
            name='origin',
            field=models.ImageField(help_text='\u5e94\u5c3d\u91cf\u907f\u514d\u4f7f\u7528\u975e\u82f1\u6587\u5b57\u7b26\u547d\u540d\u7684\u56fe\u7247\u6587\u4ef6<br>\u5934\u56fe\u6700\u4f731200\u50cf\u7d20-660\u50cf\u7d20\uff0c\u5176\u6b21600\u50cf\u7d20-330\u50cf\u7d20\uff0c\u5bbd\u9ad8\u6bd416:9', upload_to='%Y/%m/%d', max_length=200, verbose_name='\u539f\u59cb\u56fe\u7247'),
        ),
    ]
