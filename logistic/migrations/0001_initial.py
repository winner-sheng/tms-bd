# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        # ('basedata', '0001_initial'),
        ('vendor', '0001_initial'),
        ('filemgmt', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpressSender',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name=b'\xe5\xaf\x84\xe4\xbb\xb6\xe4\xba\xba')),
                ('mobile', models.CharField(max_length=13, null=True, verbose_name=b'\xe6\x89\x8b\xe6\x9c\xba', blank=True)),
                ('phone', models.CharField(max_length=20, null=True, verbose_name=b'\xe5\x9b\xba\xe5\xae\x9a\xe7\x94\xb5\xe8\xaf\x9d', blank=True)),
                ('province', models.CharField(max_length=10, verbose_name=b'\xe6\x89\x80\xe5\x9c\xa8\xe7\x9c\x81/\xe7\x9b\xb4\xe8\xbe\x96\xe5\xb8\x82/\xe8\x87\xaa\xe6\xb2\xbb\xe5\x8c\xba')),
                ('city', models.CharField(max_length=10, null=True, verbose_name=b'\xe6\x89\x80\xe5\x9c\xa8\xe5\x9f\x8e\xe5\xb8\x82', blank=True)),
                ('address', models.CharField(max_length=100, verbose_name=b'\xe5\x9c\xb0\xe5\x9d\x80')),
                ('post_code', models.CharField(max_length=8, null=True, verbose_name=b'\xe9\x82\xae\xe7\xbc\x96', blank=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('create_by', models.IntegerField(verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe4\xba\xba', null=True, editable=False, blank=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('update_by', models.IntegerField(verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe4\xba\xba', null=True, editable=False, blank=True)),
                ('supplier', models.ForeignKey(verbose_name=b'\xe4\xbe\x9b\xe5\xba\x94\xe5\x95\x86', to='vendor.Supplier')),
            ],
            options={
                'verbose_name': '\u5feb\u9012\u5355\u53d1\u4ef6\u4eba',
                'verbose_name_plural': '\u5feb\u9012\u5355\u53d1\u4ef6\u4eba',
            },
        ),
        migrations.CreateModel(
            name='ExpressTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name=b'\xe6\xa8\xa1\xe6\x9d\xbf\xe5\x90\x8d\xe7\xa7\xb0', db_index=True)),
                ('template', models.TextField(max_length=5000, null=True, verbose_name=b'\xe6\xa8\xa1\xe6\x9d\xbf', blank=True)),
                ('type', models.SmallIntegerField(default=0, null=True, verbose_name=b'\xe7\xb1\xbb\xe5\x9e\x8b', blank=True, choices=[(0, b'\xe7\xa7\x81\xe6\x9c\x89'), (1, b'\xe5\x85\xb1\xe4\xba\xab')])),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('create_by', models.IntegerField(verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe4\xba\xba', null=True, editable=False, blank=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('update_by', models.IntegerField(verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe4\xba\xba', null=True, editable=False, blank=True)),
            ],
            options={
                'ordering': ['name', '-update_time'],
                'verbose_name': '\u6a21\u677f-\u5feb\u9012\u5355',
                'verbose_name_plural': '\u6a21\u677f-\u5feb\u9012\u5355',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(default=b'N', choices=[(b'N', b'\xe6\x99\xae\xe9\x80\x9a\xe5\x8f\x91\xe7\xa5\xa8'), (b'VAT', b'\xe5\xa2\x9e\xe5\x80\xbc\xe7\xa8\x8e\xe5\x8f\x91\xe7\xa5\xa8')], max_length=3, blank=True, null=True, verbose_name=b'\xe5\x8f\x91\xe7\xa5\xa8\xe7\xb1\xbb\xe5\x9e\x8b')),
                ('mode', models.CharField(default=b'N', choices=[(b'N', b'\xe6\x99\xae\xe9\x80\x9a\xe5\x8f\x91\xe7\xa5\xa8'), (b'E', b'\xe7\x94\xb5\xe5\xad\x90\xe5\x8f\x91\xe7\xa5\xa8')], max_length=3, blank=True, null=True, verbose_name=b'\xe5\xbc\x80\xe7\xa5\xa8\xe6\x96\xb9\xe5\xbc\x8f')),
                ('invoice_no', models.CharField(default=b'', max_length=12, null=True, verbose_name=b'\xe5\x8f\x91\xe7\xa5\xa8\xe4\xbb\xa3\xe7\xa0\x81', blank=True)),
                ('title', models.CharField(help_text=b'\xe7\x95\x99\xe7\xa9\xba\xe8\xa1\xa8\xe7\xa4\xba\xe4\xb8\xaa\xe4\xba\xba\xef\xbc\x8c\xe5\x90\xa6\xe5\x88\x99\xe5\xba\x94\xe5\xa1\xab\xe5\x86\x99\xe5\x85\xac\xe5\x8f\xb8\xe5\x90\x8d\xe7\xa7\xb0', max_length=50, null=True, verbose_name=b'\xe5\x8f\x91\xe7\xa5\xa8\xe6\x8a\xac\xe5\xa4\xb4', blank=True)),
                ('amount', models.DecimalField(verbose_name=b'\xe5\x8f\x91\xe7\xa5\xa8\xe9\x87\x91\xe9\xa2\x9d', max_digits=10, decimal_places=2)),
                ('require_detail', models.BooleanField(default=False, help_text=b'\xe5\xa6\x82\xe6\x9e\x9c\xe9\x9c\x80\xe8\xa6\x81\xe8\xaf\xa6\xe6\x83\x85\xef\xbc\x8c\xe5\x88\x99\xe6\x8c\x89\xe8\xae\xa2\xe5\x8d\x95\xe5\x86\x85\xe5\xae\xb9\xe7\x94\x9f\xe6\x88\x90', verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe9\x9c\x80\xe8\xa6\x81\xe8\xaf\xa6\xe6\x83\x85')),
                ('content', models.CharField(help_text=b'\xe5\xa6\x82\xe9\xa3\x9f\xe5\x93\x81\xef\xbc\x8c\xe5\xb7\xa5\xe8\x89\xba\xe5\x93\x81\xef\xbc\x8c\xe6\x97\xa5\xe7\x94\xa8\xe5\x93\x81\xe7\xad\x89\xef\xbc\x8c\xe5\xa6\x82\xe6\x9e\x9c\xe9\x9c\x80\xe8\xa6\x81\xe8\xaf\xa6\xe6\x83\x85\xef\xbc\x8c\xe5\x88\x99\xe5\xbf\xbd\xe7\x95\xa5\xe8\xaf\xa5\xe9\xa1\xb9', max_length=30, null=True, verbose_name=b'\xe5\x8f\x91\xe7\xa5\xa8\xe5\x86\x85\xe5\xae\xb9', blank=True)),
                ('made_date', models.DateTimeField(help_text=b'\xe6\x9c\xaa\xe5\xbc\x80\xe7\xa5\xa8\xe6\x97\xb6\xef\xbc\x8c\xe8\xaf\xa5\xe9\xa1\xb9\xe7\x95\x99\xe7\xa9\xba', null=True, verbose_name=b'\xe5\xbc\x80\xe7\xa5\xa8\xe6\x97\xb6\xe9\x97\xb4', blank=True)),
                ('order', models.OneToOneField(verbose_name=b'\xe8\xae\xa2\xe5\x8d\x95', to='basedata.Order')),
            ],
            options={
                'verbose_name': '\u53d1\u7968',
                'verbose_name_plural': '\u53d1\u7968',
            },
        ),
        migrations.CreateModel(
            name='InvoiceTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name=b'\xe6\xa8\xa1\xe6\x9d\xbf\xe5\x90\x8d\xe7\xa7\xb0', db_index=True)),
                ('template', models.TextField(max_length=5000, null=True, verbose_name=b'\xe6\xa8\xa1\xe6\x9d\xbf', blank=True)),
                ('type', models.SmallIntegerField(default=0, null=True, verbose_name=b'\xe7\xb1\xbb\xe5\x9e\x8b', blank=True, choices=[(0, b'\xe7\xa7\x81\xe6\x9c\x89'), (1, b'\xe5\x85\xb1\xe4\xba\xab')])),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('create_by', models.IntegerField(verbose_name=b'\xe5\x88\x9b\xe5\xbb\xba\xe4\xba\xba', null=True, editable=False, blank=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4', null=True)),
                ('update_by', models.IntegerField(verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe4\xba\xba', null=True, editable=False, blank=True)),
                ('supplier', models.ForeignKey(verbose_name=b'\xe4\xbe\x9b\xe5\xba\x94\xe5\x95\x86', blank=True, to='vendor.Supplier', null=True)),
            ],
            options={
                'ordering': ['name', '-update_time'],
                'verbose_name': '\u6a21\u677f-\u53d1\u8d27\u5355',
                'verbose_name_plural': '\u6a21\u677f-\u53d1\u8d27\u5355',
            },
        ),
        migrations.CreateModel(
            name='ShipItem',
            fields=[
                ('package_no', models.CharField(max_length=20, serialize=False, verbose_name=b'\xe5\x8c\x85\xe8\xa3\xb9\xe7\xbc\x96\xe5\x8f\xb7', primary_key=True)),
                ('prd_code', models.CharField(max_length=16, verbose_name=b'\xe5\x95\x86\xe5\x93\x81\xe7\xbc\x96\xe7\xa0\x81')),
                ('prd_name', models.CharField(max_length=40, verbose_name=b'\xe5\x95\x86\xe5\x93\x81\xe5\x90\x8d\xe7\xa7\xb0', db_index=True)),
                ('prd_pcs', models.PositiveIntegerField(default=1, verbose_name=b'\xe6\x95\xb0\xe9\x87\x8f')),
            ],
            options={
                'verbose_name': '\u7269\u6d41\u5305\u88f9\u5546\u54c1\u9879',
                'verbose_name_plural': '\u7269\u6d41\u5305\u88f9\u5546\u54c1\u9879',
            },
        ),
        migrations.CreateModel(
            name='ShipPackage',
            fields=[
                ('package_no', models.CharField(help_text=b'\xe9\xbb\x98\xe8\xae\xa4\xe4\xb8\x8e\xe8\xae\xa2\xe5\x8d\x95\xe5\x8f\xb7\xe7\x9b\xb8\xe5\x90\x8c\xef\xbc\x8c\xe9\x99\xa4\xe9\x9d\x9e\xe7\x89\xb9\xe6\xae\x8a\xe6\x8b\x86\xe5\x8d\x95\xe6\x83\x85\xe5\xbd\xa2\xe4\xbd\xbf\xe7\x94\xa8\xe8\xae\xa2\xe5\x8d\x95\xe5\x8f\xb7\xe4\xb8\xba\xe5\x89\x8d\xe7\xbc\x80', max_length=20, serialize=False, verbose_name=b'\xe5\x8c\x85\xe8\xa3\xb9\xe7\xbc\x96\xe5\x8f\xb7', primary_key=True)),
                ('order_no', models.CharField(help_text=b'\xe4\xbf\x9d\xe7\x95\x99', max_length=20, verbose_name=b'\xe8\xae\xa2\xe5\x8d\x95\xe7\xbc\x96\xe5\x8f\xb7', db_index=True)),
                ('receiver', models.CharField(max_length=30, null=True, verbose_name=b'\xe6\x94\xb6\xe4\xbb\xb6\xe4\xba\xba', blank=True)),
                ('receiver_mobile', models.CharField(max_length=20, null=True, verbose_name=b'\xe6\x94\xb6\xe4\xbb\xb6\xe4\xba\xba\xe7\x94\xb5\xe8\xaf\x9d', blank=True)),
                ('ship_province', models.CharField(blank=True, max_length=3, null=True, verbose_name=b'\xe6\x94\xb6\xe4\xbb\xb6\xe7\x9c\x81\xe4\xbb\xbd', choices=[('\u5b89\u5fbd', '\u5b89\u5fbd'), ('\u6fb3\u95e8', '\u6fb3\u95e8'), ('\u5317\u4eac', '\u5317\u4eac'), ('\u91cd\u5e86', '\u91cd\u5e86'), ('\u798f\u5efa', '\u798f\u5efa'), ('\u7518\u8083', '\u7518\u8083'), ('\u5e7f\u4e1c', '\u5e7f\u4e1c'), ('\u5e7f\u897f', '\u5e7f\u897f'), ('\u8d35\u5dde', '\u8d35\u5dde'), ('\u6d77\u5357', '\u6d77\u5357'), ('\u6cb3\u5317', '\u6cb3\u5317'), ('\u6cb3\u5357', '\u6cb3\u5357'), ('\u9ed1\u9f99\u6c5f', '\u9ed1\u9f99\u6c5f'), ('\u6e56\u5317', '\u6e56\u5317'), ('\u6e56\u5357', '\u6e56\u5357'), ('\u5409\u6797', '\u5409\u6797'), ('\u6c5f\u82cf', '\u6c5f\u82cf'), ('\u6c5f\u897f', '\u6c5f\u897f'), ('\u8fbd\u5b81', '\u8fbd\u5b81'), ('\u5185\u8499\u53e4', '\u5185\u8499\u53e4'), ('\u5b81\u590f', '\u5b81\u590f'), ('\u9752\u6d77', '\u9752\u6d77'), ('\u5c71\u4e1c', '\u5c71\u4e1c'), ('\u5c71\u897f', '\u5c71\u897f'), ('\u9655\u897f', '\u9655\u897f'), ('\u4e0a\u6d77', '\u4e0a\u6d77'), ('\u56db\u5ddd', '\u56db\u5ddd'), ('\u53f0\u6e7e', '\u53f0\u6e7e'), ('\u5929\u6d25', '\u5929\u6d25'), ('\u897f\u85cf', '\u897f\u85cf'), ('\u9999\u6e2f', '\u9999\u6e2f'), ('\u65b0\u7586', '\u65b0\u7586'), ('\u4e91\u5357', '\u4e91\u5357'), ('\u6d59\u6c5f', '\u6d59\u6c5f')])),
                ('ship_address', models.CharField(max_length=50, null=True, verbose_name=b'\xe6\x94\xb6\xe4\xbb\xb6\xe5\x9c\xb0\xe5\x9d\x80', blank=True)),
                ('ship_code', models.CharField(db_index=True, max_length=20, null=True, verbose_name=b'\xe7\x89\xa9\xe6\xb5\x81\xe5\x8d\x95\xe5\x8f\xb7', blank=True)),
                ('ship_vendor', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name=b'\xe7\x89\xa9\xe6\xb5\x81\xe5\x85\xac\xe5\x8f\xb8', blank=True, to='vendor.LogisticsVendor', null=True)),
            ],
            options={
                'verbose_name': '\u7269\u6d41\u5305\u88f9',
                'verbose_name_plural': '\u7269\u6d41\u5305\u88f9',
            },
        ),
        migrations.CreateModel(
            name='ShipReport',
            fields=[
                ('package_no', models.CharField(max_length=20, serialize=False, verbose_name=b'\xe5\x8c\x85\xe8\xa3\xb9\xe7\xbc\x96\xe5\x8f\xb7', primary_key=True)),
                ('vendor_code', models.CharField(max_length=16, verbose_name=b'\xe7\x89\xa9\xe6\xb5\x81\xe5\x85\xac\xe5\x8f\xb8\xe7\xbc\x96\xe7\xa0\x81')),
                ('ship_code', models.CharField(max_length=20, null=True, verbose_name=b'\xe7\x89\xa9\xe6\xb5\x81\xe5\x8d\x95\xe5\x8f\xb7', blank=True)),
                ('report', models.CharField(max_length=2000, null=True, verbose_name=b'\xe7\x89\xa9\xe6\xb5\x81\xe7\x8a\xb6\xe6\x80\x81\xe6\x8a\xa5\xe5\x91\x8a', blank=True)),
                ('state', models.PositiveSmallIntegerField(default=99, verbose_name=b'\xe5\xbd\x93\xe5\x89\x8d\xe7\xad\xbe\xe6\x94\xb6\xe7\x8a\xb6\xe6\x80\x81', choices=[(99, b'\xe6\x9c\xaa\xe7\x9f\xa5'), (0, b'\xe5\x9c\xa8\xe9\x80\x94\xef\xbc\x8c\xe5\x8d\xb3\xe8\xb4\xa7\xe7\x89\xa9\xe5\xa4\x84\xe4\xba\x8e\xe8\xbf\x90\xe8\xbe\x93\xe8\xbf\x87\xe7\xa8\x8b\xe4\xb8\xad'), (1, b'\xe6\x8f\xbd\xe4\xbb\xb6\xef\xbc\x8c\xe8\xb4\xa7\xe7\x89\xa9\xe5\xb7\xb2\xe7\x94\xb1\xe5\xbf\xab\xe9\x80\x92\xe5\x85\xac\xe5\x8f\xb8\xe6\x8f\xbd\xe6\x94\xb6\xe5\xb9\xb6\xe4\xb8\x94\xe4\xba\xa7\xe7\x94\x9f\xe4\xba\x86\xe7\xac\xac\xe4\xb8\x80\xe6\x9d\xa1\xe8\xb7\x9f\xe8\xb8\xaa\xe4\xbf\xa1\xe6\x81\xaf'), (2, b'\xe7\x96\x91\xe9\x9a\xbe\xef\xbc\x8c\xe8\xb4\xa7\xe7\x89\xa9\xe5\xaf\x84\xe9\x80\x81\xe8\xbf\x87\xe7\xa8\x8b\xe5\x87\xba\xe4\xba\x86\xe9\x97\xae\xe9\xa2\x98'), (3, b'\xe7\xad\xbe\xe6\x94\xb6\xef\xbc\x8c\xe6\x94\xb6\xe4\xbb\xb6\xe4\xba\xba\xe5\xb7\xb2\xe7\xad\xbe\xe6\x94\xb6'), (4, b'\xe9\x80\x80\xe7\xad\xbe\xef\xbc\x8c\xe5\x8d\xb3\xe8\xb4\xa7\xe7\x89\xa9\xe7\x94\xb1\xe4\xba\x8e\xe7\x94\xa8\xe6\x88\xb7\xe6\x8b\x92\xe7\xad\xbe\xe3\x80\x81\xe8\xb6\x85\xe5\x8c\xba\xe7\xad\x89\xe5\x8e\x9f\xe5\x9b\xa0\xe9\x80\x80\xe5\x9b\x9e\xef\xbc\x8c\xe8\x80\x8c\xe4\xb8\x94\xe5\x8f\x91\xe4\xbb\xb6\xe4\xba\xba\xe5\xb7\xb2\xe7\xbb\x8f\xe7\xad\xbe\xe6\x94\xb6'), (5, b'\xe6\xb4\xbe\xe4\xbb\xb6\xef\xbc\x8c\xe5\x8d\xb3\xe5\xbf\xab\xe9\x80\x92\xe6\xad\xa3\xe5\x9c\xa8\xe8\xbf\x9b\xe8\xa1\x8c\xe5\x90\x8c\xe5\x9f\x8e\xe6\xb4\xbe\xe4\xbb\xb6'), (6, b'\xe9\x80\x80\xe5\x9b\x9e\xef\xbc\x8c\xe8\xb4\xa7\xe7\x89\xa9\xe6\xad\xa3\xe5\xa4\x84\xe4\xba\x8e\xe9\x80\x80\xe5\x9b\x9e\xe5\x8f\x91\xe4\xbb\xb6\xe4\xba\xba\xe7\x9a\x84\xe9\x80\x94\xe4\xb8\xad')])),
                ('latest_status', models.CharField(max_length=50, null=True, verbose_name=b'\xe6\x9c\x80\xe6\x96\xb0\xe7\x8a\xb6\xe6\x80\x81\xe6\x8f\x8f\xe8\xbf\xb0', blank=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x97\xb6\xe9\x97\xb4', null=True)),
            ],
            options={
                'ordering': ['-update_time'],
                'verbose_name': '\u7269\u6d41\u72b6\u6001\u62a5\u544a',
                'verbose_name_plural': '\u7269\u6d41\u72b6\u6001\u62a5\u544a',
            },
        ),
        migrations.CreateModel(
            name='ShapeImage',
            fields=[
            ],
            options={
                'verbose_name': '\u6a21\u677f-\u5feb\u9012\u5355\u56fe\u7247',
                'proxy': True,
                'verbose_name_plural': '\u6a21\u677f-\u5feb\u9012\u5355\u56fe\u7247',
            },
            bases=('filemgmt.baseimage',),
        ),
        migrations.AlterUniqueTogether(
            name='shipreport',
            unique_together=set([('vendor_code', 'ship_code')]),
        ),
        migrations.AddField(
            model_name='expresstemplate',
            name='shape_image',
            field=models.ForeignKey(verbose_name=b'\xe5\xba\x95\xe6\x9d\xbf\xe5\x9b\xbe\xe7\x89\x87\xe6\xa8\xa1\xe6\x9d\xbf', blank=True, to='logistic.ShapeImage', null=True),
        ),
        migrations.AddField(
            model_name='expresstemplate',
            name='supplier',
            field=models.ForeignKey(verbose_name=b'\xe4\xbe\x9b\xe5\xba\x94\xe5\x95\x86', blank=True, to='vendor.Supplier', null=True),
        ),
    ]
