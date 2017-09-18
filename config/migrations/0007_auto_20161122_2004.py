# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0006_auto_20160826_1813'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='content_image',
        ),
        migrations.RemoveField(
            model_name='article',
            name='subject_image',
        ),
        migrations.RemoveField(
            model_name='articleproduct',
            name='article',
        ),
        migrations.RemoveField(
            model_name='articleproduct',
            name='product',
        ),
        migrations.RemoveField(
            model_name='channel',
            name='image',
        ),
        migrations.RemoveField(
            model_name='channelproduct',
            name='channel',
        ),
        migrations.RemoveField(
            model_name='channelproduct',
            name='product',
        ),
        migrations.DeleteModel(
            name='Article',
        ),
        migrations.DeleteModel(
            name='ArticleProduct',
        ),
        migrations.DeleteModel(
            name='Channel',
        ),
        migrations.DeleteModel(
            name='ChannelProduct',
        ),
    ]
