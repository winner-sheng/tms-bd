# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logistic', '0006_auto_20160730_2348'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='expresstemplate',
            options={'ordering': ['name', '-update_time'], 'verbose_name': '\u6a21\u677f - \u5feb\u9012\u5355', 'verbose_name_plural': '\u6a21\u677f - \u5feb\u9012\u5355'},
        ),
        migrations.AlterModelOptions(
            name='shapeimage',
            options={'verbose_name': '\u6a21\u677f - \u5feb\u9012\u5355\u56fe\u7247', 'verbose_name_plural': '\u6a21\u677f - \u5feb\u9012\u5355\u56fe\u7247'},
        ),
    ]
