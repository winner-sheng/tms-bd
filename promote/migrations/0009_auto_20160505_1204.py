# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import ueditor.models


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0008_auto_20160428_2259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='couponrule',
            name='description',
            field=ueditor.models.UEditorField(max_length=5000, verbose_name=b'\xe8\xa7\x84\xe5\x88\x99\xe8\xaf\xb4\xe6\x98\x8e'),
        ),
    ]
