# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0015_auto_20160826_1803'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserOrgSnapShot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(max_length=32, verbose_name='\u7528\u6237/\u7ec4\u7ec7\u7528\u6237UID', db_index=True)),
                ('org_uid', models.CharField(max_length=32, verbose_name='\u6240\u5c5e\u7ec4\u7ec7\u7528\u6237UID', db_index=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4', db_index=True)),
            ],
            options={
                'verbose_name': '\u7528\u6237\u7ec4\u7ec7\u5173\u7cfb\u5feb\u7167',
                'verbose_name_plural': '\u7528\u6237\u7ec4\u7ec7\u5173\u7cfb\u5feb\u7167',
            },
        ),
        migrations.AddField(
            model_name='enduserenterprise',
            name='overhead_rate',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='\u62bd\u6210\u6bd4\u4f8b(0-100)', validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='enduserext',
            name='ex_id_type',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='\u7b2c\u4e09\u65b9\u8d26\u53f7\u7c7b\u578b', choices=[(0, '\u5fae\u4fe1openID'), (1, '\u5fae\u4fe1unionID'), (2, 'QQ\u5f00\u653e\u8d26\u53f7ID'), (3, '\u652f\u4ed8\u5b9d\u5f00\u653e\u8d26\u53f7ID'), (4, '\u5fae\u535a\u5f00\u653e\u8d26\u53f7ID'), (5, '\u666e\u901a\u6d4f\u89c8\u5668uuid\uff08\u533f\u540d\u7528\u6237\uff09'), (99, '\u4ea4\u6613\u5e73\u53f0\u7ba1\u7406\u8d26\u53f7')]),
        ),
    ]
