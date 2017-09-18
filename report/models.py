# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.forms.models import model_to_dict


class RewardSummary(models.Model):
    """
    收益统计，对应数据库视图：
        drop view `v_reward_summary`;
        CREATE VIEW `v_reward_summary` AS
        SELECT `b`.`real_name` AS `real_name`,`b`.`mobile` AS `mobile`,
        `b`.`ex_nick_name` AS `ex_nick_name`,`b`.`nick_name` AS `nick_name`,
        COUNT(0) AS `total_cnt`,
        SUM(IF((`a`.`status` = 0),`a`.`reward`,0)) AS `not_settled_reward`,
        SUM(IF((`a`.`status` = 1) AND (`a`.`account_no` is NULL or `a`.`account_no`=""),`a`.`reward`,0))
        AS `must_settled_reward`,
        SUM(IF((`a`.`status` = 1),`a`.`achieved`,0)) AS `settled_reward`,
        SUM(IF((`a`.`status` = 2),`a`.`reward`,0)) AS `revoked_reward`,`a`.`referrer_id` AS `uid`
        FROM (`promote_rewardrecord` `a`
        JOIN `profile_enduser` `b` ON((`a`.`referrer_id` = `b`.`uid`)))
        WHERE (`a`.`create_time` < '2016-04-17')
        GROUP BY `a`.`referrer_id`
        ORDER BY `settled_reward`,`not_settled_reward` DESC;
    """
    uid = models.CharField('用户ID', max_length=32, null=False, blank=False, primary_key=True)
    real_name = models.CharField('姓名', max_length=30, null=True, blank=True,
                                 help_text='备用，网安实名制要求')
    nick_name = models.CharField('昵称', max_length=30, null=True, blank=True,
                                 help_text='用户自定义昵称')
    ex_nick_name = models.CharField('昵称（第三方）', max_length=30, null=True, blank=True)
    mobile = models.CharField('手机', max_length=15, null=True, blank=True)
    not_settled_reward = models.DecimalField('未结算收益', max_digits=10, decimal_places=2, default=0,
                                             blank=True, null=True,
                                             help_text="订单未完成，暂未结算的收益")
    must_settled_reward = models.DecimalField('已结算未入账收益', max_digits=10, decimal_places=2, default=0,
                                              blank=True, null=True,
                                              help_text="已结算，尚未入账的收益金额（即无流水号，不含被撤销的）")
    settled_reward = models.DecimalField('已结算收益', max_digits=10, decimal_places=2, default=0,
                                         blank=True, null=True,
                                         help_text="订单已完成，已结算可入账的收益")
    revoked_reward = models.DecimalField('已撤销收益', max_digits=10, decimal_places=2, default=0,
                                         blank=True, null=True,
                                         help_text="因为订单被撤销或者退款而撤销的收益")
    total_cnt = models.PositiveIntegerField('收益总笔数', default=0, blank=True, null=True,
                                            help_text="包含所有未结算、已结算和被撤销的收益记录")

    def __unicode__(self):
        return "%s - 收益统计" % self.real_name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        return False

    class Meta:
        ordering = ['-settled_reward', '-not_settled_reward']
        verbose_name_plural = verbose_name = '收益统计'
        db_table = 'v_reward_summary'
        managed = False


class TmsReport(models.Model):
    REPORT_TYPES = (
        ('order_income_by_pay', '订单收入/退款统计（按付款时间）'),
        ('order_income_by_signoff', '订单收入/退款统计（按签收时间）'),
        ('order_monthly_summary', '订单销售统计（每月）'),
        ('order_daily_summary', '订单销售统计（每日）'),
        ('order_hourly_summary', '订单销售统计（分时）'),
        ('order_summary_by_state', '订单销售统计（按状态）'),
        ('order_summary_by_province', '订单销售统计（按省份）'),
        ('product_sales', '商品销售统计'),
        ('product_sales_by_supplier', '商品销售统计（按供应商）'),
        ('user_daily_summary', '用户注册统计（每日）'),
        ('user_reward_summary', '用户收益统计'),
        ('user_reward_summary_local', '用户收益统计（本地配送）'),
        ('user_reward_summary_express', '用户收益统计（非本地配送）'),
        ('user_referrer_summary', '用户推广统计'),
        ('user_cascade_reward', '伙伴推广收益统计'),
        ('account_book_summary', '用户资金账户统计'),
        ('finance_margin_detail', '销售利润表'),
        ('finance_sale_report', '订单销售报表'),
        ('finance_purchase_report', '采购报表'),
        ('finance_supplier_detail', '供应商信息表'),
    )
    STATUS_TBD = 0
    STATUS_CONFIRMED = 1
    STATUS_QUESTION = 2
    REPORT_STATUSES = (
        (0, '待审核'),
        (1, '已确认'),
        (2, '有疑问'),
    )
    report_type = models.CharField('报表类型', max_length=32, null=False, blank=False,
                                   choices=REPORT_TYPES)
    version = models.PositiveSmallIntegerField('版本', default=1, null=False, blank=False,
                                               help_text='考虑到由于需求的变化，报表数据格式可能会有所调整，用于说明数据的版本')
    title = models.CharField('报表名称', max_length=64, null=False, blank=False)
    start_time = models.DateTimeField('报表开始时间', null=True, blank=True, db_index=True,
                                      help_text='即报表统计周期的开始时间')
    end_time = models.DateTimeField('报表结束时间', null=True, blank=True, db_index=True,
                                    help_text='即报表统计周期的结束时间')
    header = models.CharField('统计字段标题', max_length=1024, null=True, blank=True,
                              help_text='报表数据中的标题字段列表，JSON格式')
    data = models.TextField('报表数据', null=True, blank=True,
                            help_text='报表主数据，JSON格式')
    summary = models.CharField('报表数据', max_length=1024, null=True, blank=True,
                               help_text='报表汇总数据, JSON格式')
    create_time = models.DateTimeField('报表创建时间', auto_now_add=True, db_index=True,
                                       help_text='即报表统计周期的结束时间')
    owner = models.CharField('报表归属', max_length=36, null=True, blank=True,
                             help_text='组合值，形如"类型-对象id"。可以是供应商，如SUP-<supplier_id>，'
                                       '也可以是用户，如UID-<end_user_uid>等')
    is_sent = models.BooleanField('是否已发送', default=False,
                                  help_text='用于标记报表是否已发送给相关方')
    status = models.PositiveSmallIntegerField('状态', default=STATUS_TBD, choices=REPORT_STATUSES,
                                              help_text='报表提交给指定对象审核后的审核结果')
    confirmed_by = models.CharField('用户ID', max_length=32, null=True, blank=True)
    confirmed_time = models.DateTimeField('确认时间', null=True, blank=True, db_index=True,
                                          help_text='即报表被指定对象审核确认的时间')
    memo = models.CharField('备注', max_length=1024, null=True, blank=True,
                            help_text='通常用于报表有调整时填写')

    def __unicode__(self):
        return self.title

    @property
    def is_confirmed(self):
        return self.status == TmsReport.STATUS_CONFIRMED

    def to_dict(self, detail=False):
        if detail:
            res = model_to_dict(self)
        else:
            res = model_to_dict(self, fields=("id", "report_type", "title", "start_time", "end_time", "is_sent",
                                              "owner", "status"))

        res['is_confirmed'] = self.is_confirmed
        return res

    class Meta:
        verbose_name = verbose_name_plural = '统计报表'
        permissions = (
            ('view_order_income_by_pay', '查看订单收入/退款统计（按付款时间）'),
            ('view_order_income_by_signoff', '查看订单收入/退款统计（按签收时间）'),
            ('view_order_monthly_summary', '查看订单销售统计（每月）'),
            ('view_order_daily_summary', '查看订单销售统计（每日）'),
            ('view_order_hourly_summary', '查看订单销售统计（分时）'),
            ('view_order_summary_by_state', '查看订单销售统计（按状态）'),
            ('view_order_summary_by_province', '查看订单销售统计（按省份）'),
            ('view_product_sales', '查看商品销售统计'),
            ('view_product_sales_by_supplier', '查看商品销售统计（按供应商）'),
            ('view_user_daily_summary', '查看用户注册统计（每日）'),
            ('view_user_reward_summary', '查看用户收益统计'),
            ('view_user_reward_summary_local', '查看用户收益统计（本地配送）'),
            ('view_user_reward_summary_express', '查看用户收益统计（非本地配送）'),
            ('view_user_referrer_summary', '查看用户推广统计'),
            ('view_user_cascade_reward', '查看伙伴推广收益统计'),
            ('view_account_book_summary', '查看用户资金账户统计'),
            ('view_finance_margin_detail', '查看销售利润表'),
            ('view_finance_sale_report', '查看订单销售报表'),
            ('view_finance_purchase_report', '查看采购报表'),
            ('view_finance_supplier_detail', '查看供应商信息表'),
        )


class SupplierBillReport(TmsReport):
    pass

    class Meta:
        proxy = True
        verbose_name = verbose_name_plural = '供应商销售账单'
        permissions = (
            ('manage_supplier_bill', '管理供应商账单'),
        )


class SupplierBillReportByAgent(TmsReport):
    pass

    class Meta:
        proxy = True
        verbose_name = verbose_name_plural = '供应商销售账单(分渠道)'
        permissions = (
            ('manage_supplier_bill', '管理供应商账单'),
        )