# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import vendor.models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0013_auto_20161122_1620'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'ordering': ['name'], 'verbose_name': '\u5546\u5bb6 - \u8054\u7cfb\u4eba', 'verbose_name_plural': '\u5546\u5bb6 - \u8054\u7cfb\u4eba'},
        ),
        migrations.AlterModelOptions(
            name='hotel',
            options={'ordering': ['name'], 'verbose_name': '\u5546\u5bb6 - \u9152\u5e97/\u6c11\u5bbf', 'verbose_name_plural': '\u5546\u5bb6 - \u9152\u5e97/\u6c11\u5bbf'},
        ),
        migrations.AlterModelOptions(
            name='logisticsvendor',
            options={'ordering': ['-is_active', 'code'], 'verbose_name': '\u5546\u5bb6 - \u7269\u6d41\u670d\u52a1\u5546', 'verbose_name_plural': '\u5546\u5bb6 - \u7269\u6d41\u670d\u52a1\u5546'},
        ),
        migrations.AlterModelOptions(
            name='manufacturer',
            options={'ordering': ['code'], 'verbose_name': '\u5546\u5bb6 - \u751f\u4ea7\u5382\u5bb6', 'verbose_name_plural': '\u5546\u5bb6 - \u751f\u4ea7\u5382\u5bb6'},
        ),
        migrations.AlterModelOptions(
            name='salesagent',
            options={'ordering': ['code'], 'verbose_name': '\u5546\u5bb6 - \u9500\u552e\u6e20\u9053', 'verbose_name_plural': '\u5546\u5bb6 - \u9500\u552e\u6e20\u9053'},
        ),
        migrations.AlterModelOptions(
            name='store',
            options={'ordering': ['code'], 'verbose_name': '\u5546\u5bb6 - \u95e8\u5e97', 'verbose_name_plural': '\u5546\u5bb6 - \u95e8\u5e97'},
        ),
        migrations.AlterModelOptions(
            name='storeagent',
            options={'verbose_name': '\u95e8\u5e97 - \u524d\u53f0\u7528\u6237', 'verbose_name_plural': '\u95e8\u5e97 - \u524d\u53f0\u7528\u6237'},
        ),
        migrations.AlterModelOptions(
            name='supplier',
            options={'ordering': ['code'], 'verbose_name': '\u5546\u5bb6 - \u5546\u54c1\u4f9b\u5e94\u5546', 'verbose_name_plural': '\u5546\u5bb6 - \u5546\u54c1\u4f9b\u5e94\u5546'},
        ),
        migrations.AlterModelOptions(
            name='suppliermanager',
            options={'verbose_name': '\u5546\u5bb6 - \u5546\u54c1\u4f9b\u5e94\u5546 - \u7ba1\u7406\u5458\u8d26\u53f7', 'verbose_name_plural': '\u5546\u5bb6 - \u5546\u54c1\u4f9b\u5e94\u5546 - \u7ba1\u7406\u5458\u8d26\u53f7'},
        ),
        migrations.AlterModelOptions(
            name='suppliernotice',
            options={'ordering': ['effective_time'], 'verbose_name': '\u5546\u5bb6 - \u5546\u54c1\u4f9b\u5e94\u5546 - \u6d88\u606f\u901a\u544a', 'verbose_name_plural': '\u5546\u5bb6 - \u5546\u54c1\u4f9b\u5e94\u5546 - \u6d88\u606f\u901a\u544a'},
        ),
        migrations.AlterField(
            model_name='suppliernotice',
            name='content',
            field=models.CharField(help_text='\u8bf7\u586b\u5199\u7eaf\u6587\u672c\u5185\u5bb9', max_length=1024, verbose_name='\u901a\u544a\u5185\u5bb9'),
        ),
        migrations.AlterField(
            model_name='suppliernotice',
            name='expire_time',
            field=models.DateTimeField(default=vendor.models._expire_time, help_text='\u9ed8\u8ba4\u6709\u6548\u671f\u4e3a7\u5929', verbose_name='\u5931\u6548\u65f6\u95f4'),
        ),
        migrations.AlterField(
            model_name='suppliernotice',
            name='supplier',
            field=models.ForeignKey(related_name='notices', verbose_name='\u6240\u5c5e\u4f9b\u5e94\u5546', to='vendor.Supplier'),
        ),
    ]
