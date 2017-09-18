# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0014_auto_20161122_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suppliernotice',
            name='content',
            field=models.CharField(help_text='\u8bf7\u586b\u5199\u7eaf\u6587\u672c\u5185\u5bb9\u3002<br><strong>\u6ce8\u610f\uff0c\u6b64\u5904\u586b\u5199\u7684\u5185\u5bb9\uff0c\u5c06\u5728\u7528\u6237\u6dfb\u52a0\u5546\u54c1\u5230\u8d2d\u7269\u8f66\u65f6\uff0c\u63d0\u793a\u7ed9\u7528\u6237</strong>', max_length=1024, verbose_name='\u901a\u544a\u5185\u5bb9'),
        ),
    ]
