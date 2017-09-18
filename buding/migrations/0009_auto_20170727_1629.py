# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buding', '0008_saleshopincome'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopmanagerinfo',
            name='pid',
            field=models.CharField(max_length=32, blank=True, help_text='\u63a8\u8350\u4eba\u7684UID', null=True, verbose_name='\u63a8\u8350\u4ebaUID', db_index=True),
        ),
    ]
