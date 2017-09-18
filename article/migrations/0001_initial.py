# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import ueditor.models


class Migration(migrations.Migration):

    dependencies = [
        ('filemgmt', '0002_auto_20160817_1013'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(default='\u6587\u7ae0\u4e3b\u9898', max_length=20, verbose_name='\u6587\u7ae0\u4e3b\u9898')),
                ('tags', models.CharField(max_length=255, blank=True, help_text='\u7528\u4e8e\u6587\u7ae0\u641c\u7d22\uff0c\u6bcf\u4e2a\u6807\u7b7e\u4e4b\u95f4\u5e94\u4f7f\u7528\u82f1\u6587\u9017\u53f7","\u5206\u9694\uff0c\u6807\u7b7e\u4e3a\u7cbe\u786e\u5339\u914d', null=True, verbose_name='\u6587\u7ae0Tag', db_index=True)),
                ('brief', models.CharField(help_text='\u6587\u7ae0\u7b80\u4ecb\uff0c\u4e00\u822c\u7528\u4e8e\u6587\u7ae0\u5217\u8868\u663e\u793a\u6458\u8981', max_length=500, null=True, verbose_name='\u7b80\u4ecb', blank=True)),
                ('content', ueditor.models.UEditorField(help_text='\u6ce8\u610f\uff1a\u5efa\u8bae\u4f7f\u7528\u4e0d\u8d85\u8fc7800\u50cf\u7d20\u5bbd\u5ea6\u7684\u56fe\u7247\u3002\u9664\u975e\u660e\u786e\u77e5\u9053\u8bbe\u7f6e\u56fe\u7247\u5927\u5c0f\u7684\u76ee\u7684\uff0c\u5426\u5219\u8bf7\u4e0d\u8981\u6307\u5b9a\u56fe\u7247\u5927\u5c0f\uff0c\u7531\u9875\u9762\u81ea\u52a8\u7f29\u653e', max_length=20000, null=True, verbose_name='\u5185\u5bb9\u63cf\u8ff0', blank=True)),
                ('link_to', models.CharField(help_text='\u5373\u7528\u6237\u70b9\u51fb\u8be5\u4e3b\u9898\u56fe\u7247\u540e\uff0c\u6253\u5f00\u7684\u5916\u94fe\u5730\u5740\uff08\u9ed8\u8ba4\u5728\u5546\u57ce\u4e2d\u6253\u5f00\uff0c\u65e0\u9700\u914d\u7f6e\uff09', max_length=100, null=True, verbose_name='\u76ee\u6807\u5730\u5740', blank=True)),
                ('list_order', models.PositiveIntegerField(default=0, null=True, verbose_name='\u663e\u793a\u987a\u5e8f(\u5927\u7684\u5728\u524d)', db_index=True, blank=True)),
                ('publish_date', models.DateTimeField(default=datetime.datetime.now, help_text='\u53ea\u6709\u751f\u6548\u65f6\u95f4\u540e\u7684\u6587\u7ae0\u624d\u4f1a\u5c55\u793a', null=True, verbose_name='\u53d1\u5e03\u65f6\u95f4', blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='\u662f\u5426\u6709\u6548')),
                ('product_tags', models.CharField(max_length=1024, blank=True, help_text='\u7528\u4e8e\u6587\u7ae0\u4e0e\u5546\u54c1\u5339\u914d\u641c\u7d22\uff0c\u683c\u5f0f\u4e3a"<\u5173\u8054\u5c5e\u6027>:<\u5173\u8054\u503c>"\uff0c\u53ef\u4ee5\u6709\u591a\u4e2a\uff0c\u4e2d\u95f4\u4f7f\u7528\u82f1\u6587\u9017\u53f7","\u5206\u9694\u3002\u5173\u8054\u5c5e\u6027\u53ef\u4ee5\u662f\u540d\u79f0\u3001\u7c7b\u522b\u3001Tag\u3001\u54c1\u724c\u3001\u4ea7\u5730\u3001\u4f9b\u5e94\u5546\u4e2d\u7684\u4e00\u79cd\u6216\u51e0\u79cd\u3002\u5982\uff1a"\u540d\u79f0:\u6708\u997c,\u7c7b\u522b:\u98df\u54c1,Tag:\u9001\u793c,\u54c1\u724c:\u5229\u7537\u5c45,\u4ea7\u5730:\u4e0a\u6d77,\u4f9b\u5e94\u5546:TWOHOU-02"', null=True, verbose_name='\u5173\u8054\u5546\u54c1Tag', db_index=True)),
                ('revision', models.PositiveSmallIntegerField(default=1, editable=False, blank=True, help_text='\u6bcf\u6b21\u4fdd\u5b58\uff0c\u7248\u672c\u53f7\u81ea\u52a8\u52a01', null=True, verbose_name='\u7248\u672c')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4', null=True)),
                ('create_by', models.CharField(verbose_name='\u521b\u5efa\u4eba', max_length=36, null=True, editable=False, blank=True)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4', null=True)),
                ('update_by', models.CharField(verbose_name='\u66f4\u65b0\u4eba', max_length=36, null=True, editable=False, blank=True)),
            ],
            options={
                'ordering': ('-list_order', '-update_time'),
                'verbose_name': '\u6587\u7ae0',
                'verbose_name_plural': '\u6587\u7ae0',
            },
        ),
        migrations.CreateModel(
            name='ArticleCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32, verbose_name='\u7c7b\u522b\u540d\u79f0')),
                ('memo', models.CharField(max_length=255, null=True, verbose_name='\u7c7b\u522b\u8bf4\u660e', blank=True)),
                ('list_order', models.PositiveIntegerField(default=0, help_text='\u6570\u503c\u8d8a\u5927\uff0c\u6392\u5e8f\u8d8a\u9760\u524d', verbose_name='\u6392\u5e8f\u6807\u8bb0')),
                ('path', models.CharField(max_length=255, blank=True, help_text='\u5305\u542b\u4e0a\u7ea7\u7f16\u7801id\u53ca\u81ea\u8eabid\uff0c\u7c7b\u4f3c"1,2,3"', null=True, verbose_name='\u8def\u5f84\uff08\u7528\u4e8e\u52a0\u901f\u67e5\u8be2\uff09', db_index=True)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='article.ArticleCategory', help_text='\u4e0a\u7ea7\u7c7b\u522b\uff0c\u5f53\u4e0a\u7ea7\u88ab\u5220\u9664\u65f6\uff0c\u4e0b\u5c5e\u5173\u8054\u7c7b\u522b\u5c06\u4e00\u5e76\u5220\u9664', null=True, verbose_name='\u4e0a\u7ea7\u7c7b\u522b')),
            ],
            options={
                'ordering': ['path', '-list_order', 'name'],
                'verbose_name': '\u6587\u7ae0\u5206\u7c7b',
                'verbose_name_plural': '\u6587\u7ae0\u5206\u7c7b',
            },
        ),
        migrations.AddField(
            model_name='article',
            name='category',
            field=models.ForeignKey(verbose_name='\u7c7b\u522b', blank=True, to='article.ArticleCategory', null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='content_image',
            field=models.ForeignKey(related_name='discovery_content_image+', blank=True, to='filemgmt.BaseImage', help_text='\u67e5\u770b\u6587\u7ae0\u7684\u8be6\u60c5\u65f6\u663e\u793a\uff0c\u9ed8\u8ba4\u4e0e\u4e3b\u9898\u56fe\u7247\u76f8\u540c', null=True, verbose_name='\u5185\u5bb9\u56fe\u7247'),
        ),
        migrations.AddField(
            model_name='article',
            name='subject_image',
            field=models.ForeignKey(related_name='discovery_subject_image+', blank=True, to='filemgmt.BaseImage', help_text='\u5efa\u8bae\u4f7f\u7528\u5bbd\u5ea6\u4e3a\u4e0d\u8d85\u8fc7600\u50cf\u7d20\u7684\u56fe\u7247\uff0c\u9ad8\u5ea6\u6839\u636e\u9700\u8981\u914c\u60c5\u8bbe\u8ba1', null=True, verbose_name='\u4e3b\u9898\u56fe\u7247'),
        ),
    ]
