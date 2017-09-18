# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0014_auto_20160906_1733'),
    ]

    operations = [
        migrations.AddField(
            model_name='couponrule',
            name='link_page',
            field=models.CharField(help_text='\u4ec5\u5f53\u5b58\u5728\u5916\u90e8\u4e13\u9898\u9875\u9762\u65f6\u4f7f\u7528', max_length=512, null=True, verbose_name='\u6d3b\u52a8\u4e13\u9898\u9875url', blank=True),
        ),
        migrations.AlterField(
            model_name='couponrule',
            name='format',
            field=models.CharField(default='', max_length=64, blank=True, help_text='\u5982"abcd-{digit-3}", \u751f\u6210\u7c7b\u4f3c"abcd-666"\u7684\u4f18\u60e0\u7801\uff0c\u53ef\u7528\u5982\u4e0b\u51e0\u79cd\u53d8\u91cf\uff1a<br>{year}{month}{day}{hour}{minute}{second}{char-X}{digit-X}{letter-X}",<br>\u5206\u522b\u8868\u793a\u7528\u5e74\u3001\u6708\u3001\u65e5\u3001\u65f6\u3001\u5206\u3001\u79d2\u3001\u5b57\u7b26\uff08\u542b\u6570\u5b57\u548c\u5b57\u6bcd\uff09\u3001\u6570\u5b57\u3001\u5b57\u6bcd\u3002<br>X\u8868\u793a\u5305\u542b\u51e0\u4e2a\u5b57\u6bcd\u6216\u6570\u5b57\u3002\u7559\u7a7a\u8868\u793a\u7531\u7cfb\u7edf\u81ea\u52a8\u7f16\u7801\uff0c\u5e26\u6821\u9a8c\u529f\u80fd', null=True, verbose_name='\u4f18\u60e0\u5238\u7f16\u7801\u683c\u5f0f(\u7f16\u7801\u6700\u957f18\u4f4d)'),
        ),
        migrations.AlterField(
            model_name='rewardrecord',
            name='source_uid',
            field=models.CharField(max_length=32, blank=True, help_text='- \u5982\u679c\u662f\u9500\u552e\u56de\u4f63\uff0c\u5219\u4e3a\u4e70\u5bb6uid\uff0c<br>- \u5982\u679c\u662f\u4f19\u4f34\u9500\u552e\u5956\u52b1\uff0c\u5219\u4e3a\u4f19\u4f34uid\uff0c<br>- \u5982\u679c\u662f\u4f01\u4e1a\u7ba1\u7406\u8d39\u7528\uff0c\u5219\u4e3a\u4e0b\u5c5e\u4f01\u4e1auid', null=True, verbose_name='\u6536\u76ca\u6765\u6e90\u7528\u6237UID', db_index=True),
        ),
    ]
