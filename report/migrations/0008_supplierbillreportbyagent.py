# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0007_tmsreport_version'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupplierBillReportByAgent',
            fields=[
            ],
            options={
                'verbose_name': '\u4f9b\u5e94\u5546\u9500\u552e\u8d26\u5355(\u5206\u6e20\u9053)',
                'proxy': True,
                'verbose_name_plural': '\u4f9b\u5e94\u5546\u9500\u552e\u8d26\u5355(\u5206\u6e20\u9053)',
                'permissions': (('manage_supplier_bill', '\u7ba1\u7406\u4f9b\u5e94\u5546\u8d26\u5355'),),
            },
            bases=('report.tmsreport',),
        ),
    ]
