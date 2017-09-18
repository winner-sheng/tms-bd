# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0007_auto_20160427_1638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='couponrule',
            name='update_by',
            field=models.IntegerField(verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe4\xba\xba', null=True, editable=False, blank=True),
        ),
    ]
