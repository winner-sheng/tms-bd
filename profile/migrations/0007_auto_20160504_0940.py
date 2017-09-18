# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0006_usercapitalaccount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enduserext',
            name='ex_id',
            field=models.CharField(db_index=True, max_length=32, null=True, verbose_name=b'\xe7\xac\xac\xe4\xb8\x89\xe6\x96\xb9\xe8\xb4\xa6\xe5\x8f\xb7', blank=True),
        ),
    ]
