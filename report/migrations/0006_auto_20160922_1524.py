# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0005_auto_20160914_1640'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupplierBillReport',
            fields=[
            ],
            options={
                'verbose_name': '\u4f9b\u5e94\u5546\u9500\u552e\u8d26\u5355',
                'proxy': True,
                'verbose_name_plural': '\u4f9b\u5e94\u5546\u9500\u552e\u8d26\u5355',
                'permissions': (('manage_supplier_bill', '\u7ba1\u7406\u4f9b\u5e94\u5546\u8d26\u5355'),),
            },
            bases=('report.tmsreport',),
        ),
        migrations.RemoveField(
            model_name='tmsreport',
            name='is_confirmed',
        ),
        migrations.AddField(
            model_name='tmsreport',
            name='status',
            field=models.PositiveSmallIntegerField(default=0, help_text='\u62a5\u8868\u63d0\u4ea4\u7ed9\u6307\u5b9a\u5bf9\u8c61\u5ba1\u6838\u540e\u7684\u5ba1\u6838\u7ed3\u679c', verbose_name='\u72b6\u6001', choices=[(0, '\u5f85\u5ba1\u6838'), (1, '\u5df2\u786e\u8ba4'), (2, '\u6709\u7591\u95ee')]),
        ),
    ]
