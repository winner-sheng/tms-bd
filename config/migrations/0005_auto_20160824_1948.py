# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0004_auto_20160817_1820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='subject',
            field=models.CharField(default='\u6587\u7ae0\u4e3b\u9898', max_length=20, verbose_name='\u6587\u7ae0\u4e3b\u9898'),
        ),
        migrations.AlterField(
            model_name='article',
            name='subject_image',
            field=models.ForeignKey(related_name='discovery_subject_image+', blank=True, to='filemgmt.BaseImage', help_text='\u5efa\u8bae\u4f7f\u7528\u5bbd\u5ea6\u4e3a\u4e0d\u8d85\u8fc7600\u50cf\u7d20\u7684\u56fe\u7247\uff0c\u9ad8\u5ea6\u6839\u636e\u9700\u8981\u914c\u60c5\u8bbe\u8ba1', null=True, verbose_name='\u4e3b\u9898\u56fe\u7247'),
        ),
    ]
