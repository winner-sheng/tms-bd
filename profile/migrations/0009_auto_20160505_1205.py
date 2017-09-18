# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0008_auto_20160504_1751'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='useraccountbook',
            options={'verbose_name': '\u7528\u6237\u8d44\u91d1\u6d41\u6c34', 'verbose_name_plural': '\u7528\u6237\u8d44\u91d1\u6d41\u6c34'},
        ),
        migrations.AlterModelOptions(
            name='withdrawrequest',
            options={'ordering': ['-pk'], 'verbose_name': '\u7528\u6237\u63d0\u73b0\u7533\u8bf7\u8bb0\u5f55', 'verbose_name_plural': '\u7528\u6237\u63d0\u73b0\u7533\u8bf7\u8bb0\u5f55'},
        ),
    ]
