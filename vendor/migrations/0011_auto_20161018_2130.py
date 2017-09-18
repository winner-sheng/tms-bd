# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import util.renderutil
import ueditor.models


class Migration(migrations.Migration):

    dependencies = [
        ('filemgmt', '0002_auto_20160817_1013'),
        ('vendor', '0010_remove_supplier_capital_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(default=util.renderutil.random_code, help_text='\u53ef\u81ea\u52a8\u751f\u6210\uff0c\u5efa\u8bae\u7edf\u4e00\u4f7f\u7528\u7528\u62fc\u97f3\u9996\u5b57\u6bcd\u4f5c\u4e3a\u7f16\u7801(\u6ce8\uff1a"TWOHOU-"\u524d\u7f00\u4e3a\u571f\u7334\u4e13\u7528)', unique=True, max_length=32, verbose_name='\u7f16\u7801')),
                ('name', models.CharField(unique=True, max_length=50, verbose_name='\u540d\u79f0')),
                ('intro', ueditor.models.UEditorField(max_length=10000, null=True, verbose_name='\u7b80\u4ecb', blank=True)),
                ('homepage', models.URLField(null=True, verbose_name='\u7f51\u5740(http://)', blank=True)),
                ('logo', models.ForeignKey(related_name='company_logo+', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='filemgmt.BaseImage', null=True)),
                ('phone', models.CharField(max_length='16', null=True, verbose_name='\u8054\u7cfb\u7535\u8bdd', blank=True)),
                ('fax', models.CharField(max_length='16', null=True, verbose_name='\u4f20\u771f', blank=True)),
                ('province', models.CharField(blank=True, max_length=10, null=True, verbose_name='\u6240\u5728\u7701/\u76f4\u8f96\u5e02/\u81ea\u6cbb\u533a', choices=[('\u5b89\u5fbd', '\u5b89\u5fbd'), ('\u6fb3\u95e8', '\u6fb3\u95e8'), ('\u5317\u4eac', '\u5317\u4eac'), ('\u91cd\u5e86', '\u91cd\u5e86'), ('\u798f\u5efa', '\u798f\u5efa'), ('\u7518\u8083', '\u7518\u8083'), ('\u5e7f\u4e1c', '\u5e7f\u4e1c'), ('\u5e7f\u897f', '\u5e7f\u897f'), ('\u8d35\u5dde', '\u8d35\u5dde'), ('\u6d77\u5357', '\u6d77\u5357'), ('\u6cb3\u5317', '\u6cb3\u5317'), ('\u6cb3\u5357', '\u6cb3\u5357'), ('\u9ed1\u9f99\u6c5f', '\u9ed1\u9f99\u6c5f'), ('\u6e56\u5317', '\u6e56\u5317'), ('\u6e56\u5357', '\u6e56\u5357'), ('\u5409\u6797', '\u5409\u6797'), ('\u6c5f\u82cf', '\u6c5f\u82cf'), ('\u6c5f\u897f', '\u6c5f\u897f'), ('\u8fbd\u5b81', '\u8fbd\u5b81'), ('\u5185\u8499\u53e4', '\u5185\u8499\u53e4'), ('\u5b81\u590f', '\u5b81\u590f'), ('\u9752\u6d77', '\u9752\u6d77'), ('\u5c71\u4e1c', '\u5c71\u4e1c'), ('\u5c71\u897f', '\u5c71\u897f'), ('\u9655\u897f', '\u9655\u897f'), ('\u4e0a\u6d77', '\u4e0a\u6d77'), ('\u56db\u5ddd', '\u56db\u5ddd'), ('\u53f0\u6e7e', '\u53f0\u6e7e'), ('\u5929\u6d25', '\u5929\u6d25'), ('\u897f\u85cf', '\u897f\u85cf'), ('\u9999\u6e2f', '\u9999\u6e2f'), ('\u65b0\u7586', '\u65b0\u7586'), ('\u4e91\u5357', '\u4e91\u5357'), ('\u6d59\u6c5f', '\u6d59\u6c5f')])),
                ('city', models.CharField(max_length=10, null=True, verbose_name='\u6240\u5728\u57ce\u5e02', blank=True)),
                ('address', models.CharField(max_length=100, null=True, verbose_name='\u5730\u5740', blank=True)),
                ('post_code', models.CharField(max_length=8, null=True, verbose_name='\u90ae\u7f16', blank=True)),
                ('lng', models.FloatField(default=0, null=True, verbose_name='\u7ecf\u5ea6', blank=True)),
                ('lat', models.FloatField(default=0, null=True, verbose_name='\u7eac\u5ea6', blank=True)),
                ('geo_hash', models.CharField(db_index=True, max_length=16, null=True, editable=False, blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='\u662f\u5426\u6709\u6548')),
                ('is_verified', models.BooleanField(default=True, verbose_name='\u662f\u5426\u5df2\u8ba4\u8bc1')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4', null=True)),
                ('create_by', models.IntegerField(verbose_name='\u521b\u5efa\u4eba', null=True, editable=False, blank=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4', null=True)),
                ('update_by', models.IntegerField(verbose_name='\u66f4\u65b0\u4eba', null=True, editable=False, blank=True)),
                ('tags', models.CharField(help_text='\u591a\u4e2a\u6807\u7b7e\u7528\u82f1\u6587\u9017\u53f7\u5206\u9694\uff0c\u5982\u201c\u8d85\u503c,\u514d\u8d39wifi,\u4ea4\u901a\u65b9\u4fbf\u201d', max_length=255, null=True, verbose_name='\u6807\u7b7e', blank=True)),
                ('link_to_book1', models.CharField(max_length=255, null=True, verbose_name='\u8ba2\u623f\u94fe\u63a5', blank=True)),
                ('link_to_book2', models.CharField(max_length=255, null=True, verbose_name='\u8ba2\u623f\u94fe\u63a5', blank=True)),
                ('primary_contact', models.ForeignKey(related_name='primary_contact+', verbose_name='\u4e3b\u8054\u7cfb\u4eba', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='vendor.Contact', null=True)),
                ('backup_contact', models.ForeignKey(related_name='backup_contact+', verbose_name='\u5907\u8054\u7cfb\u4eba', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='vendor.Contact', null=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': '\u5546\u5bb6-\u9152\u5e97/\u6c11\u5bbf',
                'verbose_name_plural': '\u5546\u5bb6-\u9152\u5e97/\u6c11\u5bbf',
            },
        ),
        migrations.CreateModel(
            name='HotelImage',
            fields=[
                ('baseimage_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='filemgmt.BaseImage')),
                ('list_order', models.PositiveIntegerField(default=0, help_text='\u6570\u503c\u8d8a\u5927\uff0c\u6392\u5e8f\u8d8a\u9760\u524d', verbose_name='\u6392\u5e8f\u6807\u8bb0')),
                ('hotel', models.ForeignKey(related_name='hotel_images', verbose_name='\u9152\u5e97', to='vendor.Hotel')),
            ],
            options={
                'ordering': ('-list_order',),
                'verbose_name': '\u9152\u5e97\u56fe\u7247',
                'verbose_name_plural': '\u9152\u5e97\u56fe\u7247',
            },
            bases=('filemgmt.baseimage',),
        ),
        migrations.AddField(
            model_name='logisticsvendor',
            name='fax',
            field=models.CharField(max_length='16', null=True, verbose_name='\u4f20\u771f', blank=True),
        ),
        migrations.AddField(
            model_name='logisticsvendor',
            name='phone',
            field=models.CharField(max_length='16', null=True, verbose_name='\u8054\u7cfb\u7535\u8bdd', blank=True),
        ),
        migrations.AddField(
            model_name='manufacturer',
            name='fax',
            field=models.CharField(max_length='16', null=True, verbose_name='\u4f20\u771f', blank=True),
        ),
        migrations.AddField(
            model_name='manufacturer',
            name='phone',
            field=models.CharField(max_length='16', null=True, verbose_name='\u8054\u7cfb\u7535\u8bdd', blank=True),
        ),
        migrations.AddField(
            model_name='store',
            name='fax',
            field=models.CharField(max_length='16', null=True, verbose_name='\u4f20\u771f', blank=True),
        ),
        migrations.AddField(
            model_name='store',
            name='phone',
            field=models.CharField(max_length='16', null=True, verbose_name='\u8054\u7cfb\u7535\u8bdd', blank=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='fax',
            field=models.CharField(max_length='16', null=True, verbose_name='\u4f20\u771f', blank=True),
        ),
        migrations.AddField(
            model_name='supplier',
            name='phone',
            field=models.CharField(max_length='16', null=True, verbose_name='\u8054\u7cfb\u7535\u8bdd', blank=True),
        ),
        migrations.AlterField(
            model_name='logisticsvendor',
            name='backup_contact',
            field=models.ForeignKey(related_name='backup_contact+', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u5907\u8054\u7cfb\u4eba', blank=True, to='vendor.Contact', null=True),
        ),
        migrations.AlterField(
            model_name='logisticsvendor',
            name='primary_contact',
            field=models.ForeignKey(related_name='primary_contact+', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u4e3b\u8054\u7cfb\u4eba', blank=True, to='vendor.Contact', null=True),
        ),
        migrations.AlterField(
            model_name='manufacturer',
            name='backup_contact',
            field=models.ForeignKey(related_name='backup_contact+', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u5907\u8054\u7cfb\u4eba', blank=True, to='vendor.Contact', null=True),
        ),
        migrations.AlterField(
            model_name='manufacturer',
            name='primary_contact',
            field=models.ForeignKey(related_name='primary_contact+', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u4e3b\u8054\u7cfb\u4eba', blank=True, to='vendor.Contact', null=True),
        ),
        migrations.AlterField(
            model_name='store',
            name='backup_contact',
            field=models.ForeignKey(related_name='backup_contact+', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u5907\u8054\u7cfb\u4eba', blank=True, to='vendor.Contact', null=True),
        ),
        migrations.AlterField(
            model_name='store',
            name='primary_contact',
            field=models.ForeignKey(related_name='primary_contact+', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u4e3b\u8054\u7cfb\u4eba', blank=True, to='vendor.Contact', null=True),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='backup_contact',
            field=models.ForeignKey(related_name='backup_contact+', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u5907\u8054\u7cfb\u4eba', blank=True, to='vendor.Contact', null=True),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='primary_contact',
            field=models.ForeignKey(related_name='primary_contact+', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\u4e3b\u8054\u7cfb\u4eba', blank=True, to='vendor.Contact', null=True),
        ),
    ]
