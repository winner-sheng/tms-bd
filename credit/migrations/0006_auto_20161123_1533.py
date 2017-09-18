# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('credit', '0005_auto_20161122_2004'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='medalcatalog',
            options={'ordering': ['-list_order', 'id'], 'verbose_name': '\u52cb\u7ae0\u76ee\u5f55', 'verbose_name_plural': '\u52cb\u7ae0\u76ee\u5f55'},
        ),
        migrations.AddField(
            model_name='medalcatalog',
            name='list_order',
            field=models.PositiveIntegerField(default=0, help_text='\u6570\u503c\u8d8a\u5927\uff0c\u6392\u5e8f\u8d8a\u9760\u524d', verbose_name='\u6392\u5e8f\u6807\u8bb0'),
        ),
    ]
