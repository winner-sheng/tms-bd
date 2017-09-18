# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0011_useraccountbook_trans_no'),
        ('vendor', '0002_auto_20160502_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='capital_account',
            field=models.ForeignKey(related_name='+', verbose_name=b'\xe8\xb5\x84\xe9\x87\x91\xe8\xb4\xa6\xe5\x8f\xb7', blank=True, to='profile.UserCapitalAccount', null=True),
        ),
    ]
