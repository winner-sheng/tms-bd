# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('buding', '0005_auto_20170719_0937'),
    ]

    operations = [
        migrations.AddField(
            model_name='saleshopproduct',
            name='status',
            field=models.PositiveSmallIntegerField(default=0, help_text='\u53ea\u6709\u4e0a\u67b6\u5546\u54c1\u624d\u80fd\u5728\u5546\u57ce\u5c55\u793a\uff0c\u4e0a\u67b6\u9700\u8981\u786e\u4fdd\u76f8\u5173\u4ef7\u683c\u4fe1\u606f\u586b\u5199\u5b8c\u6574', db_index=True, verbose_name='\u5546\u54c1\u72b6\u6001', choices=[(0, '\u5f85\u4e0a\u67b6'), (1, '\u4e0a\u67b6'), (2, '\u5df2\u4e0b\u67b6')]),
        ),
    ]
