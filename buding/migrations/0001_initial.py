# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SaleShop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(help_text='\u5e97\u94fa\u4ee3\u7801', max_length=32, verbose_name='\u5e97\u94fa\u4ee3\u7801', db_index=True)),
                ('name', models.CharField(help_text='\u5e97\u94fa\u540d\u79f0', max_length=32, verbose_name='\u5e97\u94fa\u540d\u79f0', db_index=True)),
                ('qrcode', models.CharField(help_text='\u5e97\u94fa\u540d\u79f0', max_length=255, null=True, verbose_name='\u5e97\u94fa\u4e8c\u7ef4\u7801', blank=True)),
                ('keeperqrcode', models.CharField(help_text='\u5e97\u4e3b\u9080\u8bf7\u4e8c\u7ef4\u7801', max_length=255, null=True, verbose_name='\u5e97\u4e3b\u9080\u8bf7\u4e8c\u7ef4\u7801', blank=True)),
                ('shopicon', models.CharField(help_text='\u5e97\u94fa\u5934\u50cf', max_length=255, null=True, verbose_name='\u5e97\u94fa\u5934\u50cf', blank=True)),
                ('cover', models.CharField(help_text='\u5c01\u9762', max_length=255, null=True, verbose_name='\u5c01\u9762', blank=True)),
                ('watchcount', models.PositiveIntegerField(default=0, help_text='\u5fae\u4fe1\u5173\u6ce8\u4eba\u6570', verbose_name='\u5173\u6ce8\u4eba\u6570')),
                ('state', models.PositiveSmallIntegerField(default=0, help_text='\u5e97\u94fa\u72b6\u6001', db_index=True, verbose_name='\u5e97\u94fa\u72b6\u6001', choices=[(0, '\u5ba1\u6838\u4e2d'), (1, '\u5f00\u4e1a\u4e2d'), (2, '\u4f11\u606f\u4e2d')])),
                ('shopkeeperuid', models.CharField(help_text='\u5e97\u4e3bUID', max_length=64, verbose_name='\u5e97\u4e3bUID', db_index=True)),
                ('province', models.CharField(help_text='\u6240\u5728\u7701\u4efd', max_length=32, null=True, verbose_name='\u7701', blank=True)),
                ('city', models.CharField(help_text='\u6240\u5728\u57ce\u5e02', max_length=32, null=True, verbose_name='\u5e02', blank=True)),
                ('district', models.CharField(help_text='\u6240\u5728\u533a', max_length=32, null=True, verbose_name='\u533a', blank=True)),
                ('address', models.CharField(help_text='\u8be6\u7ec6\u5730\u5740', max_length=512, null=True, verbose_name='\u5730\u5740', blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4', null=True)),
                ('create_by', models.CharField(help_text='\u5bf9\u4e8e\u901a\u8fc7\u540e\u53f0\u7ba1\u7406\u5165\u53e3\u6dfb\u52a0\u8005\uff0c\u8bb0\u5f55\u7528\u6237\u4fe1\u606f', max_length=32, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True)),
            ],
            options={
                'verbose_name': '\u5e97\u94fa\u4fe1\u606f\u8868',
                'verbose_name_plural': '\u5e97\u94fa\u4fe1\u606f\u8868',
            },
        ),
        migrations.CreateModel(
            name='SaleShopProduct',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shopcode', models.CharField(help_text='\u5e97\u94fa\u4ee3\u7801', max_length=64, verbose_name='\u5e97\u94fa\u4ee3\u7801', db_index=True)),
                ('productid', models.CharField(help_text='\u5546\u54c1\u4ee3\u7801', max_length=64, verbose_name='\u5546\u54c1\u4ee3\u7801')),
                ('retail_price', models.DecimalField(decimal_places=2, max_digits=10, blank=True, help_text='\u96f6\u552e\u4ef7\u683c', null=True, verbose_name='\u96f6\u552e\u4ef7\uffe5')),
                ('settle_price', models.DecimalField(decimal_places=2, max_digits=10, blank=True, help_text='\u7ed3\u7b97\u4ef7\u683c', null=True, verbose_name='\u7ed3\u7b97\u4ef7\uffe5')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4', null=True)),
                ('create_by', models.CharField(help_text='\u5bf9\u4e8e\u901a\u8fc7\u540e\u53f0\u7ba1\u7406\u5165\u53e3\u6dfb\u52a0\u8005\uff0c\u8bb0\u5f55\u7528\u6237\u4fe1\u606f', max_length=32, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True)),
            ],
            options={
                'verbose_name': '\u5e97\u94fa\u5546\u54c1\u8868',
                'verbose_name_plural': '\u5e97\u94fa\u5546\u54c1\u8868',
            },
        ),
        migrations.CreateModel(
            name='ShopkeeperInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(help_text='\u5e03\u4e01\u5e10\u53f7\u7cfb\u7edf\u7684\u7528\u6237UID', max_length=32, verbose_name='\u7528\u6237UID', db_index=True)),
                ('wx_openid', models.CharField(help_text='\u5fae\u4fe1\u516c\u4f17\u53f7ID', max_length=64, verbose_name='\u5fae\u4fe1\u516c\u4f17\u53f7ID', db_index=True)),
                ('truename', models.CharField(help_text='\u4e2a\u4eba\u771f\u5b9e\u540d\u79f0', max_length=64, verbose_name='\u59d3\u540d/\u540d\u79f0', db_index=True)),
                ('mobile', models.CharField(help_text='\u624b\u673a\u53f7\u7801', max_length=15, null=True, verbose_name='\u624b\u673a\u53f7\u7801', blank=True)),
                ('city', models.CharField(help_text='\u6240\u5728\u57ce\u5e02\u62fc\u97f3', max_length=30, null=True, verbose_name='\u6240\u5728\u57ce\u5e02', blank=True)),
                ('id_card', models.CharField(help_text='\u8eab\u4efd\u8bc1\u53f7\u7801', max_length=32, verbose_name='\u8eab\u4efd\u8bc1\u53f7\u7801')),
                ('photo', models.CharField(help_text='\u8eab\u4efd\u8bc1\u6b63\u9762', max_length=255, verbose_name='\u8eab\u4efd\u8bc1\u6b63\u9762')),
                ('photoReverse', models.CharField(help_text='\u8eab\u4efd\u8bc1\u53cd\u9762', max_length=255, verbose_name='\u8eab\u4efd\u8bc1\u53cd\u9762')),
                ('rejectmessage', models.CharField(help_text='\u62d2\u7edd\u4fe1\u606f', max_length=45, null=True, verbose_name='\u62d2\u7edd\u4fe1\u606f', blank=True)),
                ('state', models.PositiveSmallIntegerField(default=0, help_text='\u4e1a\u4e3b\u5ba1\u6838\u72b6\u6001', db_index=True, verbose_name='\u4e1a\u4e3b\u5ba1\u6838\u72b6\u6001', choices=[(0, '\u5f85\u5ba1\u6838'), (1, '\u5ba1\u6838\u901a\u8fc7'), (2, '\u5ba1\u6838\u4e0d\u901a\u8fc7')])),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4', null=True)),
                ('create_by', models.CharField(help_text='\u5bf9\u4e8e\u901a\u8fc7\u540e\u53f0\u7ba1\u7406\u5165\u53e3\u6dfb\u52a0\u8005\uff0c\u8bb0\u5f55\u7528\u6237\u4fe1\u606f', max_length=32, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True)),
            ],
            options={
                'ordering': ['-pk'],
                'verbose_name': '\u5e97\u4e3b\u4fe1\u606f\u8868',
                'verbose_name_plural': '\u5e97\u4e3b\u4fe1\u606f\u8868',
            },
        ),
        migrations.CreateModel(
            name='ShopManagerInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(help_text='\u5e03\u4e01\u5e10\u53f7\u7cfb\u7edf\u7684\u7528\u6237UID', max_length=64, verbose_name='\u7528\u6237UID', db_index=True)),
                ('wx_openid', models.CharField(help_text='\u5fae\u4fe1\u516c\u4f17\u53f7ID', max_length=64, verbose_name='\u5fae\u4fe1\u516c\u4f17\u53f7ID', db_index=True)),
                ('truename', models.CharField(help_text='\u4e2a\u4eba\u771f\u5b9e\u540d\u79f0', max_length=64, verbose_name='\u59d3\u540d/\u540d\u79f0', db_index=True)),
                ('mobile', models.CharField(help_text='\u624b\u673a\u53f7\u7801', max_length=15, null=True, verbose_name='\u624b\u673a\u53f7\u7801', blank=True)),
                ('shopcode', models.CharField(default='', help_text='\u5e97\u94fa\u4ee3\u7801', max_length=64, verbose_name='\u5e97\u94fa\u4ee3\u7801', db_index=True)),
                ('role', models.PositiveSmallIntegerField(default=0, help_text='\u804c\u4f4d', db_index=True, verbose_name='\u804c\u4f4d', choices=[(0, '\u5458\u5de5'), (1, '\u7ecf\u7406')])),
                ('pid', models.PositiveIntegerField(default=0, verbose_name='pid')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4', null=True)),
                ('create_by', models.CharField(help_text='\u5bf9\u4e8e\u901a\u8fc7\u540e\u53f0\u7ba1\u7406\u5165\u53e3\u6dfb\u52a0\u8005\uff0c\u8bb0\u5f55\u7528\u6237\u4fe1\u606f', max_length=32, null=True, verbose_name='\u521b\u5efa\u4eba', blank=True)),
            ],
            options={
                'verbose_name': '\u5e97\u957f\u53ca\u5e97\u5458\u4fe1\u606f\u8868',
                'verbose_name_plural': '\u5e97\u957f\u53ca\u5e97\u5458\u4fe1\u606f\u8868',
            },
        ),
    ]
