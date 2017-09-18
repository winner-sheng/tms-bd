# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0002_auto_20160428_2259'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Brand',
        ),
    ]
