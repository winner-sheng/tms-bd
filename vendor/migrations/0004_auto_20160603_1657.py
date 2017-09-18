# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0012_enduser_update_time'),
        ('vendor', '0003_supplier_capital_account'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='store',
            options={'ordering': ['code'], 'verbose_name': '\u5e97\u94fa', 'verbose_name_plural': '\u5e97\u94fa'},
        ),
        migrations.RenameField(
            model_name='logisticsvendor',
            old_name='latitude',
            new_name='lat',
        ),
        migrations.RenameField(
            model_name='logisticsvendor',
            old_name='longitude',
            new_name='lng',
        ),
        migrations.RenameField(
            model_name='manufacturer',
            old_name='latitude',
            new_name='lat',
        ),
        migrations.RenameField(
            model_name='manufacturer',
            old_name='longitude',
            new_name='lng',
        ),
        migrations.RenameField(
            model_name='store',
            old_name='latitude',
            new_name='lat',
        ),
        migrations.RenameField(
            model_name='store',
            old_name='longitude',
            new_name='lng',
        ),
        migrations.RenameField(
            model_name='supplier',
            old_name='latitude',
            new_name='lat',
        ),
        migrations.RenameField(
            model_name='supplier',
            old_name='longitude',
            new_name='lng',
        ),
        migrations.AddField(
            model_name='store',
            name='capital_account',
            field=models.ForeignKey(related_name='+', blank=True, to='profile.UserCapitalAccount', help_text='\u7528\u4e8e\u7ed9\u5e97\u94fa\u8d26\u53f7\u6253\u6b3e', null=True, verbose_name='\u8d44\u91d1\u8d26\u53f7'),
        ),
        migrations.AddField(
            model_name='store',
            name='owner_uid',
            field=models.CharField(db_index=True, max_length=32, null=True, verbose_name='\u5e97\u4e3bUID', blank=True),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='capital_account',
            field=models.ForeignKey(related_name='+', blank=True, to='profile.UserCapitalAccount', help_text=b'\xe7\x94\xa8\xe4\xba\x8e\xe7\xbb\x99\xe4\xbe\x9b\xe5\xba\x94\xe5\x95\x86\xe8\xb4\xa6\xe5\x8f\xb7\xe6\x89\x93\xe6\xac\xbe', null=True, verbose_name=b'\xe8\xb5\x84\xe9\x87\x91\xe8\xb4\xa6\xe5\x8f\xb7'),
        ),
    ]
