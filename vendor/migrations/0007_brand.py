# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0006_suppliersalesincome'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=20, verbose_name='\u54c1\u724c\u540d\u79f0')),
                ('list_order', models.PositiveIntegerField(default=0, help_text='\u6570\u503c\u8d8a\u5927\uff0c\u6392\u5e8f\u8d8a\u9760\u524d', verbose_name='\u6392\u5e8f\u6807\u8bb0')),
                ('supplier', models.ForeignKey(verbose_name='\u4f9b\u5e94\u5546', blank=True, to='vendor.Supplier', null=True)),
            ],
            options={
                'ordering': ('-list_order',),
                'verbose_name': '\u54c1\u724c',
                'verbose_name_plural': '\u54c1\u724c',
            },
        ),
    ]
