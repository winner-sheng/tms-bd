# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='review_by',
            field=models.CharField(verbose_name='\u5ba1\u6838\u4eba', max_length=36, null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='article',
            name='review_date',
            field=models.DateTimeField(help_text='\u9884\u7559\uff0c\u5f53\u7528\u6237\u6587\u7ae0\u9700\u8981\u88ab\u5ba1\u6838\u65f6\u4f7f\u7528', verbose_name='\u5ba1\u6838\u65f6\u95f4', null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='publish_date',
            field=models.DateTimeField(help_text='\u53ea\u6709\u751f\u6548\u65f6\u95f4\u540e\u7684\u6587\u7ae0\u624d\u4f1a\u5c55\u793a', null=True, verbose_name='\u53d1\u5e03\u65f6\u95f4', blank=True),
        ),
    ]
