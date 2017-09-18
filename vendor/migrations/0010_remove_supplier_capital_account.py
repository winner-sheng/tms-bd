# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0009_auto_20161010_1013'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supplier',
            name='capital_account',
        ),
    ]
