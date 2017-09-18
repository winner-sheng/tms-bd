# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('promote', '0013_auto_20160831_1523'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='rewardrecord',
            unique_together=set([('order_no', 'referrer_id', 'activity_code')]),
        ),
    ]
