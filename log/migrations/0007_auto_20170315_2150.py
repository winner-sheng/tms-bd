# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0006_auto_20161129_1246'),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='usermaillog',
        #     name='msg_type',
        #     field=models.PositiveSmallIntegerField(default=3, verbose_name='\u90ae\u4ef6\u7c7b\u578b', choices=[(0, '\u6765\u8ba2\u5355\u4e86'), (1, '\u8ba2\u5355\u5904\u7406\u8d85\u65f6'), (2, '\u5546\u54c1\u5e93\u5b58\u4f4e'), (3, '\u5176\u4ed6')]),
        # ),
        # migrations.AddField(
        #     model_name='wechatmsglog',
        #     name='msg_type',
        #     field=models.PositiveSmallIntegerField(default=3, verbose_name='\u6d88\u606f\u7c7b\u578b', choices=[(0, '\u6765\u8ba2\u5355\u4e86'), (1, '\u8ba2\u5355\u5904\u7406\u8d85\u65f6'), (2, '\u5546\u54c1\u5e93\u5b58\u4f4e'), (3, '\u5176\u4ed6')]),
        # ),
    ]
