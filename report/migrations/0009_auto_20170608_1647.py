# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0008_supplierbillreportbyagent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tmsreport',
            options={'verbose_name': '\u7edf\u8ba1\u62a5\u8868', 'verbose_name_plural': '\u7edf\u8ba1\u62a5\u8868', 'permissions': (('view_order_income_by_pay', '\u67e5\u770b\u8ba2\u5355\u6536\u5165/\u9000\u6b3e\u7edf\u8ba1\uff08\u6309\u4ed8\u6b3e\u65f6\u95f4\uff09'), ('view_order_income_by_signoff', '\u67e5\u770b\u8ba2\u5355\u6536\u5165/\u9000\u6b3e\u7edf\u8ba1\uff08\u6309\u7b7e\u6536\u65f6\u95f4\uff09'), ('view_order_monthly_summary', '\u67e5\u770b\u8ba2\u5355\u9500\u552e\u7edf\u8ba1\uff08\u6bcf\u6708\uff09'), ('view_order_daily_summary', '\u67e5\u770b\u8ba2\u5355\u9500\u552e\u7edf\u8ba1\uff08\u6bcf\u65e5\uff09'), ('view_order_hourly_summary', '\u67e5\u770b\u8ba2\u5355\u9500\u552e\u7edf\u8ba1\uff08\u5206\u65f6\uff09'), ('view_order_summary_by_state', '\u67e5\u770b\u8ba2\u5355\u9500\u552e\u7edf\u8ba1\uff08\u6309\u72b6\u6001\uff09'), ('view_order_summary_by_province', '\u67e5\u770b\u8ba2\u5355\u9500\u552e\u7edf\u8ba1\uff08\u6309\u7701\u4efd\uff09'), ('view_product_sales', '\u67e5\u770b\u5546\u54c1\u9500\u552e\u7edf\u8ba1'), ('view_product_sales_by_supplier', '\u67e5\u770b\u5546\u54c1\u9500\u552e\u7edf\u8ba1\uff08\u6309\u4f9b\u5e94\u5546\uff09'), ('view_user_daily_summary', '\u67e5\u770b\u7528\u6237\u6ce8\u518c\u7edf\u8ba1\uff08\u6bcf\u65e5\uff09'), ('view_user_reward_summary', '\u67e5\u770b\u7528\u6237\u6536\u76ca\u7edf\u8ba1'), ('view_user_reward_summary_local', '\u67e5\u770b\u7528\u6237\u6536\u76ca\u7edf\u8ba1\uff08\u672c\u5730\u914d\u9001\uff09'), ('view_user_referrer_summary', '\u67e5\u770b\u7528\u6237\u63a8\u5e7f\u7edf\u8ba1'), ('view_user_cascade_reward', '\u67e5\u770b\u4f19\u4f34\u63a8\u5e7f\u6536\u76ca\u7edf\u8ba1'), ('view_account_book_summary', '\u67e5\u770b\u7528\u6237\u8d44\u91d1\u8d26\u6237\u7edf\u8ba1'), ('view_finance_margin_detail', '\u67e5\u770b\u9500\u552e\u5229\u6da6\u8868'), ('view_finance_sale_report', '\u67e5\u770b\u8ba2\u5355\u9500\u552e\u62a5\u8868'), ('view_finance_purchase_report', '\u67e5\u770b\u91c7\u8d2d\u62a5\u8868'), ('view_finance_supplier_detail', '\u67e5\u770b\u4f9b\u5e94\u5546\u4fe1\u606f\u8868'))},
        ),
    ]
