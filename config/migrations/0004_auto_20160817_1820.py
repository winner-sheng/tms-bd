# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import ueditor.models


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0003_delete_brand'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='banner',
            options={'ordering': ('-list_order', 'id'), 'verbose_name': '\u9875\u9762\u8bbe\u7f6e-\u5e7f\u544a\u4e0e\u5bfc\u822a', 'verbose_name_plural': '\u9875\u9762\u8bbe\u7f6e-\u5e7f\u544a\u4e0e\u5bfc\u822a'},
        ),
        migrations.AlterModelOptions(
            name='channel',
            options={'ordering': ('-list_order', 'id'), 'verbose_name': '\u9875\u9762\u8bbe\u7f6e-\u9891\u9053', 'verbose_name_plural': '\u9875\u9762\u8bbe\u7f6e-\u9891\u9053'},
        ),
        migrations.AlterModelOptions(
            name='channelproduct',
            options={'ordering': ('-list_order', 'id'), 'verbose_name': '\u9875\u9762\u8bbe\u7f6e-\u9891\u9053\u5546\u54c1\u6620\u5c04\u8868', 'verbose_name_plural': '\u9875\u9762\u8bbe\u7f6e-\u9891\u9053\u5546\u54c1\u6620\u5c04\u8868'},
        ),
        migrations.AddField(
            model_name='article',
            name='brief',
            field=models.CharField(help_text='\u6587\u7ae0\u7b80\u4ecb\uff0c\u4e00\u822c\u7528\u4e8e\u6587\u7ae0\u5217\u8868\u663e\u793a\u6458\u8981', max_length=500, null=True, verbose_name='\u7b80\u4ecb', blank=True),
        ),
        migrations.AddField(
            model_name='article',
            name='category',
            field=models.PositiveIntegerField(default=1, choices=[(1, '\u5176\u5b83'), (2, '\u7cbe\u54c1\u63a8\u8350'), (3, '\u7279\u4ea7\u767e\u79d1')], blank=True, null=True, verbose_name='\u7c7b\u522b', db_index=True),
        ),
        migrations.AddField(
            model_name='banner',
            name='scenario',
            field=models.CharField(max_length=36, blank=True, help_text='\u7528\u4e8e\u6807\u8bb0\u8be5\u9879\u7528\u4e8e\u4ec0\u4e48\u6837\u7684\u573a\u666f\uff0c\u5373\u663e\u793a\u5728\u4e0d\u540c\u7684\u524d\u7aef\u9875\u9762\uff0c\u7559\u7a7a\u8868\u793a\u9ed8\u8ba4\u573a\u666f', null=True, verbose_name='\u5e94\u7528\u573a\u666f', db_index=True),
        ),
        migrations.AddField(
            model_name='channel',
            name='scenario',
            field=models.CharField(max_length=36, blank=True, help_text='\u7528\u4e8e\u6807\u8bb0\u8be5\u9879\u7528\u4e8e\u4ec0\u4e48\u6837\u7684\u573a\u666f\uff0c\u5373\u663e\u793a\u5728\u4e0d\u540c\u7684\u524d\u7aef\u9875\u9762\uff0c\u7559\u7a7a\u8868\u793a\u9ed8\u8ba4\u573a\u666f', null=True, verbose_name='\u5e94\u7528\u573a\u666f', db_index=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='content',
            field=ueditor.models.UEditorField(help_text='\u6ce8\u610f\uff1a\u5efa\u8bae\u4f7f\u7528\u4e0d\u8d85\u8fc7800\u50cf\u7d20\u5bbd\u5ea6\u7684\u56fe\u7247\u3002\u9664\u975e\u660e\u786e\u77e5\u9053\u8bbe\u7f6e\u56fe\u7247\u5927\u5c0f\u7684\u76ee\u7684\uff0c\u5426\u5219\u8bf7\u4e0d\u8981\u6307\u5b9a\u56fe\u7247\u5927\u5c0f\uff0c\u7531\u9875\u9762\u81ea\u52a8\u7f29\u653e', max_length=20000, null=True, verbose_name='\u5185\u5bb9\u63cf\u8ff0', blank=True),
        ),
        migrations.AlterField(
            model_name='banner',
            name='image',
            field=models.ForeignKey(related_name='banner_image+', verbose_name='Banner\u56fe\u7247', to='filemgmt.BaseImage', help_text='\u8bf7\u6839\u636e\u524d\u7aef\u9875\u9762\u9700\u8981\u4e0a\u4f20\u56fe\u7247\uff0c\u786e\u4fdd\u540c\u4e00\u573a\u666f\u4e0b\u591a\u5f20\u56fe\u7247\u5c3a\u5bf8\u6bd4\u4f8b\u4e00\u81f4\uff01'),
        ),
        migrations.AlterField(
            model_name='banner',
            name='link_to',
            field=models.CharField(help_text='\u5373\u7528\u6237\u70b9\u51fb\u8be5\u56fe\u7247\u540e\uff0c\u6253\u5f00\u7684\u9875\u9762\u5730\u5740', max_length=100, null=True, verbose_name='\u76ee\u6807\u5730\u5740', blank=True),
        ),
        migrations.AlterField(
            model_name='channel',
            name='image',
            field=models.ForeignKey(related_name='channel_image+', verbose_name='\u9891\u9053\u56fe\u7247', to='filemgmt.BaseImage', help_text='\u8bf7\u6ce8\u610f\u4e0a\u4f20\u56fe\u7247\u5c3a\u5bf8\u5e94\u5339\u914d\u524d\u7aef\u9875\u9762\u5e03\u5c40\u8981\u6c42'),
        ),
        migrations.AddField(
            model_name='banner',
            name='owner',
            field=models.CharField(max_length=36, blank=True, help_text='\u5f52\u5c5e\u5bf9\u8c61\u53ef\u4ee5\u662f\u7528\u6237uid\uff0c\u5982"uid:xxx"\uff0c\u4e5f\u53ef\u80fd\u662f\u4f9b\u5e94\u5546id\uff0c\u5982"sup:xxx\u7b49"', null=True, verbose_name='\u5f52\u5c5e\u5bf9\u8c61ID', db_index=True),
        ),
        migrations.AddField(
            model_name='article',
            name='product_tags',
            field=models.CharField(max_length=255, blank=True, help_text='\u7528\u4e8e\u6587\u7ae0\u4e0e\u5546\u54c1\u5339\u914d\u641c\u7d22\uff0c\u6bcf\u4e2a\u6807\u7b7e\u4e4b\u95f4\u5e94\u4f7f\u7528\u82f1\u6587\u9017\u53f7","\u5206\u9694\uff0c\u6807\u7b7e\u4e3a\u7cbe\u786e\u5339\u914d\u3002\u9700\u8981\u540c\u65f6\u5339\u914d\u591a\u4e2atag\uff0c\u8bf7\u7528","\u5206\u9694\uff0c\u53ea\u8981\u5339\u914d\u5176\u4e2d\u4e00\u4e2atag\uff0c\u8bf7\u7528"|"\u5206\u9694', null=True, verbose_name='\u5173\u8054\u5546\u54c1Tag', db_index=True),
        ),
        # migrations.AlterField(
        #     model_name='article',
        #     name='effective_date',
        #     field=models.DateTimeField(default=datetime.datetime.now, help_text='\u53ea\u6709\u751f\u6548\u65f6\u95f4\u540e\u7684\u6587\u7ae0\u624d\u4f1a\u5c55\u793a', null=True, verbose_name='\u751f\u6548\u65f6\u95f4', blank=True),
        # ),
        # migrations.AlterField(
        #     model_name='banner',
        #     name='effective_date',
        #     field=models.DateTimeField(default=datetime.datetime.now, help_text='\u53ea\u6709\u751f\u6548\u65f6\u95f4\u540e\u7684\u56fe\u7247\u624d\u4f1a\u5c55\u793a', null=True, verbose_name='\u751f\u6548\u65f6\u95f4', blank=True),
        # ),
    ]
