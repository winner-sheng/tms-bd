# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0013_auto_20160622_2300'),
    ]

    operations = [
        migrations.CreateModel(
            name='EndUserEnterprise',
            fields=[
                ('enduser_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='profile.EndUser')),
                ('license_image', models.URLField(help_text='\u79c1\u5bc6\u56fe\u7247\uff0c\u7528\u4e8e\u4f01\u4e1a\u8d44\u8d28\u5ba1\u6838', max_length=255, null=True, verbose_name='\u6267\u7167/\u8d44\u8d28\u8bc1\u7167', blank=True)),
                ('id_card_image', models.URLField(help_text='\u79c1\u5bc6\u56fe\u7247\uff0c\u7528\u4e8e\u4f01\u4e1a\u8d1f\u8d23\u4eba\u8eab\u4efd\u8ba4\u8bc1', max_length=255, null=True, verbose_name='\u8d23\u4efb\u4eba\u8eab\u4efd\u8bc1\u7167', blank=True)),
                ('contact_name', models.CharField(max_length=30, null=True, verbose_name='\u8054\u7cfb\u4eba', blank=True)),
                ('contact_mobile', models.CharField(max_length=13, null=True, verbose_name='\u8054\u7cfb\u4eba\u624b\u673a', blank=True)),
                ('contact_phone', models.CharField(max_length=15, null=True, verbose_name='\u56fa\u5b9a\u7535\u8bdd', blank=True)),
                ('contact_email', models.EmailField(max_length=60, null=True, verbose_name='Email', blank=True)),
                ('review_status', models.CharField(default='pending', max_length=8, verbose_name='\u5ba1\u6838\u72b6\u6001', choices=[('pending', '\u5f85\u5ba1\u6838'), ('passed', '\u5df2\u901a\u8fc7'), ('rejected', '\u5df2\u62d2\u7edd'), ('hold', '\u6682\u65f6\u6401\u7f6e')])),
                ('review_note', models.CharField(max_length=255, null=True, verbose_name='\u5ba1\u6838\u610f\u89c1', blank=True)),
                ('reviewed_time', models.DateTimeField(verbose_name='\u5ba1\u6838\u65f6\u95f4', null=True, editable=False, blank=True)),
            ],
            options={
                'verbose_name': '\u4f01\u4e1a\u8d26\u53f7',
                'verbose_name_plural': '\u4f01\u4e1a\u8d26\u53f7',
            },
            bases=('profile.enduser',),
        ),
        migrations.CreateModel(
            name='EndUserLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(max_length=32, verbose_name='\u7528\u6237UID', db_index=True)),
                ('link', models.CharField(max_length=200, null=True, verbose_name='\u94fe\u63a5\u5730\u5740', blank=True)),
                ('link_type', models.CharField(default='website', max_length=10, verbose_name='\u94fe\u63a5\u7c7b\u578b', choices=[('weibo', '\u5fae\u535a'), ('wechat', '\u5fae\u4fe1\u516c\u4f17\u53f7'), ('website', '\u7f51\u7ad9\u5730\u5740')])),
            ],
            options={
                'verbose_name': '\u7528\u6237\u5173\u8054\u5730\u5740',
                'verbose_name_plural': '\u7528\u6237\u5173\u8054\u5730\u5740',
            },
        ),
        migrations.CreateModel(
            name='EndUserRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_uid', models.CharField(max_length=32, verbose_name='\u7528\u6237UID', db_index=True)),
                ('org_uid', models.CharField(max_length=32, verbose_name='\u4f01\u4e1a\u7528\u6237UID', db_index=True)),
                ('role', models.CharField(default='staff', max_length=10, verbose_name='\u7528\u6237\u89d2\u8272', choices=[('admin', '\u7ba1\u7406\u5458'), ('staff', '\u804c\u5458')])),
            ],
            options={
                'verbose_name': '\u7528\u6237\u89d2\u8272',
                'verbose_name_plural': '\u7528\u6237\u89d2\u8272',
            },
        ),
        migrations.AlterModelOptions(
            name='enduserext',
            options={'verbose_name': '\u7ec8\u7aef\u7528\u6237 - \u7b2c\u4e09\u65b9\u8d26\u53f7', 'verbose_name_plural': '\u7ec8\u7aef\u7528\u6237 - \u7b2c\u4e09\u65b9\u8d26\u53f7'},
        ),
        migrations.AddField(
            model_name='enduser',
            name='entry_uid',
            field=models.CharField(max_length=36, blank=True, help_text='\u5373\u7528\u6237\u9996\u6b21\u626b\u7801\u8fdb\u5165\uff0c\u6210\u4e3a\u65b0\u7528\u6237\u65f6\u5165\u53e3\u7528\u6237\u7684uid', null=True, verbose_name='\u5165\u53e3UID', db_index=True),
        ),
        migrations.AddField(
            model_name='enduser',
            name='intro',
            field=models.CharField(max_length=1024, null=True, verbose_name='\u7b80\u4ecb', blank=True),
        ),
        migrations.AddField(
            model_name='enduser',
            name='is_org_staff',
            field=models.BooleanField(default=False, help_text='\u8be5\u8bbe\u7f6e\u4ec5\u5bf9\u666e\u901a\u7c7b\u578b\u7528\u6237\u6709\u6548\uff0c\u5f53\u8bbe\u7f6e\u4e3a\u662f\u65f6\uff0c\u9700\u68c0\u67e5\u7528\u6237\u4e0e\u7ec4\u7ec7\u7684\u5173\u7cfb', verbose_name='\u662f\u5426\u7ec4\u7ec7\u7ba1\u7406\u8005'),
        ),
        migrations.AddField(
            model_name='enduser',
            name='org_uid',
            field=models.CharField(db_index=True, max_length=36, null=True, verbose_name='\u5f52\u5c5e\u7ec4\u7ec7UID', blank=True),
        ),
        migrations.AddField(
            model_name='enduser',
            name='user_type',
            field=models.CharField(default='P', max_length=10, verbose_name='\u7528\u6237\u7c7b\u578b', choices=[('P', '\u666e\u901a\u7528\u6237'), ('E', '\u4f01\u4e1a\u7528\u6237'), ('G', '\u96c6\u56e2\u4f01\u4e1a')]),
        ),
        migrations.AlterField(
            model_name='enduser',
            name='avatar',
            field=models.URLField(help_text='\u7528\u6237\u81ea\u5b9a\u4e49\u5934\u50cf\uff0c\u4f18\u5148\u4e8e\u7b2c\u4e09\u65b9\u5934\u50cf\u8bbe\u7f6e\uff0c\u5bf9\u4e8e\u4f01\u4e1a\u800c\u8a00\u5c31\u662f\u4f01\u4e1a\u7684Logo', max_length=255, null=True, verbose_name='\u5934\u50cf', blank=True),
        ),
        migrations.AlterField(
            model_name='enduser',
            name='real_name',
            field=models.CharField(max_length=30, blank=True, help_text='\u5907\u7528\uff0c\u7f51\u5b89\u5b9e\u540d\u5236\u8981\u6c42\uff0c\u5bf9\u4e8e\u4f01\u4e1a\u8d26\u53f7\u5c31\u662f\u4f01\u4e1a\u540d\u79f0', null=True, verbose_name='\u59d3\u540d/\u540d\u79f0', db_index=True),
        ),
        migrations.AlterField(
            model_name='enduser',
            name='referrer',
            field=models.CharField(max_length=36, blank=True, help_text='\u7528\u6237\u88ab\u63a8\u8350\u6210\u4e3a\u5bfc\u6e38\u65f6\u63a8\u8350\u4eba\u7684uid', null=True, verbose_name='\u63a8\u8350\u4eba', db_index=True),
        ),
    ]
