# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0015_auto_20161124_2135'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='salesagent',
            options={'ordering': ['code'], 'verbose_name': '\u9500\u552e\u6e20\u9053', 'verbose_name_plural': '\u9500\u552e\u6e20\u9053'},
        ),
    ]
