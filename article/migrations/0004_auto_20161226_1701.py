# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ueditor.models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0003_auto_20161122_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='content',
            field=ueditor.models.UEditorField(help_text='\u6ce8\u610f\uff1a\u5efa\u8bae\u4f7f\u7528\u4e0d\u8d85\u8fc7800\u50cf\u7d20\u5bbd\u5ea6\u7684\u56fe\u7247\u3002\u9664\u975e\u660e\u786e\u77e5\u9053\u8bbe\u7f6e\u56fe\u7247\u5927\u5c0f\u7684\u76ee\u7684\uff0c\u5426\u5219\u8bf7\u4e0d\u8981\u6307\u5b9a\u56fe\u7247\u5927\u5c0f\uff0c\u7531\u9875\u9762\u81ea\u52a8\u7f29\u653e', max_length=200000, null=True, verbose_name='\u5185\u5bb9\u63cf\u8ff0', blank=True),
        ),
    ]
