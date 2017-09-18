# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0007_brand'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='brand',
            options={'ordering': ('-list_order', 'name'), 'verbose_name': '\u54c1\u724c', 'verbose_name_plural': '\u54c1\u724c'},
        ),
    ]
