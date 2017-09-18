# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0002_auto_20161021_1704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='is_active',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u6709\u6548'),
        ),
        migrations.AlterField(
            model_name='article',
            name='product_tags',
            field=models.CharField(max_length=1024, blank=True, help_text='\u7528\u4e8e\u6587\u7ae0\u4e0e\u5173\u8054\u5bf9\u8c61\uff08\u5982\u5546\u54c1\u3001\u4f18\u60e0\u6d3b\u52a8\u7b49\uff09\u5339\u914d\u641c\u7d22\u3002<br>\u683c\u5f0f\u4e3a"<\u5173\u8054\u5c5e\u6027>:<\u5173\u8054\u503c>"\uff0c\u53ef\u4ee5\u6709\u591a\u4e2a\uff0c\u4e2d\u95f4\u4f7f\u7528\u82f1\u6587\u9017\u53f7","\u5206\u9694\uff0c\u4e0d\u540c\u5c5e\u6027\u7528\u82f1\u6587";"\u5206\u9694\u3002<br>\u5173\u8054\u5c5e\u6027\u53ef\u4ee5\u662f\u5546\u54c1\u540d\u79f0\u3001\u7c7b\u522b\u3001Tag\u3001\u54c1\u724c\u3001\u4ea7\u5730\u3001\u4f9b\u5e94\u5546\u4e2d\u7684\u4e00\u79cd\u6216\u51e0\u79cd\uff0c\u6216\u8005\u662f\u6d3b\u52a8\uff08\u5bf9\u5e94\u4f18\u60e0\u6d3b\u52a8\u7f16\u7801\uff09\u3002<br>\u5982\uff1a<br>  - "\u540d\u79f0:\u6708\u997c;\u7c7b\u522b:\u98df\u54c1;Tag:\u4e2d\u79cb,\u793c\u54c1,\u70d8\u57f9\u98df\u54c1;\u54c1\u724c:\u5229\u7537\u5c45;\u4ea7\u5730:\u4e0a\u6d77;\u4f9b\u5e94\u5546:TWOHOU-02"<br>  - "\u6d3b\u52a8:A-160816-TKB"', null=True, verbose_name='\u5173\u8054\u5bf9\u8c61\u8868\u8fbe\u5f0f', db_index=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='publish_date',
            field=models.DateTimeField(default=datetime.datetime.now, help_text='\u53ea\u6709\u751f\u6548\u65f6\u95f4\u540e\u7684\u6587\u7ae0\u624d\u4f1a\u5c55\u793a', null=True, verbose_name='\u53d1\u5e03\u65f6\u95f4', blank=True),
        ),
    ]
