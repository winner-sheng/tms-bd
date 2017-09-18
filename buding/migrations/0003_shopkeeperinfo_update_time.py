# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buding', '0002_auto_20170713_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopkeeperinfo',
            name='update_time',
            field=models.DateTimeField(null=True, verbose_name='\u66f4\u65b0\u65f6\u95f4', blank=True),
        ),
    ]
