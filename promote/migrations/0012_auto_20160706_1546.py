# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0011_auto_20160602_1149'),
    ]

    operations = [
        migrations.AddField(
            model_name='couponrule',
            name='allow_dynamic',
            field=models.BooleanField(default=False, help_text='\u5982\u679c\u5141\u8bb8\uff0c\u5219\u4f18\u60e0\u5238\u7684\u6709\u6548\u671f\u4ece\u7528\u6237\u9886\u53d6\u65f6\u5f00\u59cb\u7b97\u8d77\uff0c\u81ea\u52a8\u987a\u5ef6\u6307\u5b9a\u7684\u6709\u6548\u5929\u6570', verbose_name='\u5141\u8bb8\u52a8\u6001\u6709\u6548\u671f'),
        ),
        migrations.AddField(
            model_name='couponrule',
            name='dynamic_days',
            field=models.PositiveSmallIntegerField(default=30, help_text='\u81ea\u7528\u6237\u9886\u5238\u5f00\u59cb\uff0c\u4f18\u60e0\u5238\u5728x\u5929\u5185\u6709\u6548\uff0c\u5373\u4fbf\u8be5\u65f6\u95f4\u8d85\u8fc7\u6709\u6548\u671f\u7ed3\u675f\u65f6\u95f4', verbose_name='动态有效期（天）'),
        ),
        migrations.AddField(
            model_name='couponticket',
            name='expiry_date',
            field=models.DateTimeField(help_text='\u5bf9\u4e8e\u652f\u6301\u52a8\u6001\u8fc7\u671f\u65f6\u95f4\u7684\u4f18\u60e0\u5238\uff0c\u8fc7\u671f\u65f6\u95f4\u4ee5\u6b64\u4e3a\u51c6', null=True, verbose_name='\u8fc7\u671f\u65f6\u95f4', blank=True),
        ),
    ]
