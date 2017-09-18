# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0005_auto_20160621_2154'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupplierSalesIncome',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order_no', models.CharField(max_length=20, verbose_name='\u8ba2\u5355\u7f16\u53f7', db_index=True)),
                ('activity_code', models.CharField(help_text='\u7528\u4e8e\u7279\u5b9a\u573a\u666f\u4e0b\u4ea7\u751f\u7684\u8ba2\u5355\uff0c\u6bd4\u5982\u67d0\u4e2a\u8425\u9500\u6d3b\u52a8', max_length=32, null=True, verbose_name='\u6d3b\u52a8\u4ee3\u7801', blank=True)),
                ('product_cost', models.DecimalField(decimal_places=2, default=0, max_digits=10, blank=True, help_text='\u5373\u8ba2\u5355\u4e2d\u8be5\u4f9b\u5e94\u5546\u9500\u552e\u7684\u5546\u54c1\u6210\u672c*\u5546\u54c1\u6570\u91cf', null=True, verbose_name='\u5546\u54c1\u9500\u552e\u6536\u5165')),
                ('ship_fee', models.DecimalField(decimal_places=2, default=0, max_digits=10, blank=True, help_text='\u90ae\u8d39\u6536\u5165\u5e94\u6263\u9664\u90ae\u8d39\u4f18\u60e0\u90e8\u5206', null=True, verbose_name='\u90ae\u8d39\u6536\u5165')),
                ('adjust_fee', models.DecimalField(decimal_places=2, default=0, max_digits=10, blank=True, help_text='\u6839\u636e\u9700\u8981\u624b\u5de5\u8c03\u8282', null=True, verbose_name='\u624b\u5de5\u8c03\u8282\u7684\u8d39\u7528')),
                ('has_doubt', models.BooleanField(default=False, help_text='\u6536\u5165\u5982\u679c\u6807\u6ce8\u4e3a\u6709\u7591\u95ee\uff0c\u5219\u6682\u65f6\u4e0d\u53ef\u7ed3\u7b97\uff0c\u5df2\u7ed3\u7b97\u7684\u4e5f\u5c06\u64a4\u9500', verbose_name='\u662f\u5426\u6709\u7591\u95ee')),
                ('memo', models.CharField(max_length=32, null=True, verbose_name='\u5907\u6ce8', blank=True)),
                ('status', models.PositiveSmallIntegerField(default=0, verbose_name='\u6536\u5165\u72b6\u6001', choices=[(0, '\u5f85\u786e\u8ba4'), (1, '\u5f85\u7ed3\u7b97'), (2, '\u5df2\u7ed3\u7b97'), (3, '\u5df2\u53d6\u6d88')])),
                ('settled_time', models.DateTimeField(help_text='\u7ed3\u7b97\u4e3a\u624b\u5de5\u7ed3\u7b97\uff0c\u672a\u624b\u5de5\u7ed3\u7b97\u7684\uff0c\u5219\u5728\u8ba2\u5355\u7b7e\u6536\u540e\u6307\u5b9a\u7ed3\u7b97\u5468\u671f\u5185\u81ea\u52a8\u7ed3\u7b97\u8fdb\u5165\u4f9b\u5e94\u5546\u6d41\u6c34', null=True, verbose_name='\u7ed3\u7b97\u65f6\u95f4', blank=True)),
                ('revoked_time', models.DateTimeField(help_text='\u5f53\u8ba2\u5355\u88ab\u9000\u6b3e\u65f6\u7acb\u5373\u64a4\u9500', null=True, verbose_name='\u64a4\u9500\u65f6\u95f4', blank=True)),
                ('account_no', models.CharField(help_text='\u5df2\u7ed3\u7b97\u6536\u76ca\u5fc5\u987b\u6709\u6d41\u6c34\u53f7\u540e\uff0c\u624d\u610f\u5473\u7740\u8be5\u6536\u76ca\u5230\u8d26', max_length=32, null=True, verbose_name='\u6d41\u6c34\u53f7', blank=True)),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='\u521b\u5efa\u65f6\u95f4', blank=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4', null=True)),
                ('supplier', models.ForeignKey(verbose_name='\u4f9b\u5e94\u5546', to='vendor.Supplier')),
            ],
            options={
                'verbose_name': '\u4f9b\u5e94\u5546\u9500\u552e\u6536\u5165',
                'verbose_name_plural': '\u4f9b\u5e94\u5546\u9500\u552e\u6536\u5165',
            },
        ),
    ]
