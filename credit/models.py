# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import timedelta

from django.db import models, transaction, IntegrityError
from django.forms.models import model_to_dict
from django.db.models import Sum

from tms import settings
from util.renderutil import now, logger
from django.core.cache import cache


class CreditBook(models.Model):
    """
    用户积分流水
    """
    uid = models.CharField(u'用户UID', max_length=32, null=False, blank=False, db_index=True,
                           help_text='对于普通用户是用户的UID，对于供应商，则是"SUP-"前缀 + 供应商编码，如"SUP-TWOHOU"')
    figure = models.PositiveIntegerField(u'入账积分', default=0,
                                         help_text=u"出/入账均计入此栏，正值表示收入，负值表示支出")
    is_income = models.BooleanField(u'是否收入', default=True, help_text=u'如果是支出，应设为False')
    source = models.CharField(u'积分来源', max_length=200, null=False, blank=False,
                              help_text='说明积分的来源信息，比如某个任务奖励')
    extra_type = models.CharField(u'关联对象类型', max_length=30, null=True, blank=True)
    extra_data = models.CharField(u'补充信息', max_length=500, null=True, blank=True,
                                  help_text=u'用于保存额外的关联数据，比如订单号等')
    scenario = models.CharField('场景', max_length=50, null=True, blank=True,
                                help_text='用于区分获取积分的不同场景和应用，预留')
    create_time = models.DateTimeField(u'创建时间', blank=True, null=True, auto_now_add=True)
    expire_time = models.DateTimeField(u'失效时间', blank=True, null=True)
    create_by = models.CharField(u'创建人', max_length=32, null=True, blank=True,
                                 help_text='对于通过后台管理入口添加者，记录用户信息')

    def __unicode__(self):
        return "%s:%s%s" % (self.source, '+' if self.is_income else '-', self.figure)

    @staticmethod
    def get_user_title(uid, credit):
        """
        根据用户的积分获取其对应的称号
        :param uid:
        :param credit:
        :return:
        """
        result = {'rank_title': '隐形人', 'next_level': 0}
        try:
            with transaction.atomic():
                user_title = UserTitle.objects.filter(uid=uid).last()  # TODO: 忽略重复数据（原因待查）
                if not user_title:
                    rank_series = RankSeries.objects.first()
                    if not rank_series:
                        return result
                    series_id = rank_series.pk
                    UserTitle.objects.create(uid=uid, series_id=series_id)
                else:
                    series_id = user_title.series_id
        except IntegrityError, e:
            logger.error(e)

        try:
            rank_title = RankTitle.objects.get(series_id=series_id,
                                               left_value__lte=credit,
                                               right_value__gte=credit)
            result['rank_title'] = rank_title.name
            result['next_level'] = rank_title.right_value
        except RankTitle.DoesNotExist:
            logger.error('没有找到匹配（积分：%s）的称号' % credit)

        return result

    @staticmethod
    def get_credit_summary(uid):
        """
        获取指定用户的积分统计信息
        :param uid:
        :return:
            成功返回收益记录列表，如：
            {
                total: "569.00",   (账户总额，含已申请提现但尚未到账的部分)
                income: "1169.00", （收入）
                deduct: "0",        (已收入，因故又被扣除的部分)
                expense: 600       （支出）
                withdraw_tbd: "400.00",  （尚未处理的申请提现金额，即冻结部分）
                reward_frozen: "100.00",  (收益已入账，但暂时不可使用部分）
                available: "69.00"       （账户中可使用金额，及总余额扣除冻结和已入账暂不可使用部分）
                uid: "7ad5b2c101cb4944ae053b6b275e91a6",
            }
            失败返回错误消息{"error": msg}
        """
        summary = CreditBook.objects.filter(uid=uid).values('is_income')\
            .order_by('is_income').annotate(total=Sum('figure'))

        result = {"uid": uid, "total": 0, "income": 0, "expense": 0}
        for item in summary:
            if item['is_income']:
                result['income'] += item['total']
            else:
                result['expense'] += item['total']

        result['total'] = result['income'] - result['expense']
        return result

    def to_dict(self):
        res = model_to_dict(self)
        res['create_time'] = self.create_time
        return res

    # def charge_back(self):
    #     """
    #     对于当前的流水记录进行相反操作，出账的新增一笔入账记录，入账的则新增一笔扣除操作，不重复处理
    #     :return:
    #     """
    #     acct_type = 'deduct' if self.is_income else 'return'
    #     try:
    #         CreditBook.objects.get(extra_type='profile.UserAccountBook',
    #                                     extra_data=self.account_no,
    #                                     type=acct_type)
    #         pass  # do nothing if ever exists
    #     except CreditBook.DoesNotExist:
    #         account_desc = u'撤销[%s]' % self.account_desc
    #         CreditBook.objects.create(extra_type='profile.UserAccountBook',
    #                                        extra_data=self.account_no,
    #                                        uid=self.uid,
    #                                        figure=self.figure,
    #                                        is_income=not self.is_income,
    #                                        type=acct_type,
    #                                        account_desc=account_desc)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.expire_time = self.expire_time or now(settings.USE_TZ) + timedelta(days=10 * 365)
        super(CreditBook, self).save(force_insert=force_insert,
                                     force_update=force_update,
                                     using=using,
                                     update_fields=update_fields)
        cache_key = "%s:%s" % (CreditBook._meta.model_name, self.uid)
        if cache_key in cache:
            cache.delete(cache_key)

    class Meta:
        ordering = ['-pk']
        verbose_name_plural = verbose_name = u'积分流水'


class RankSeries(models.Model):
    name = models.CharField('系列名称', max_length=20, null=False, blank=False)
    create_time = models.DateTimeField(u'创建时间', blank=True, null=True, auto_now_add=True)
    create_by = models.CharField(u'创建人', max_length=32, null=True, blank=True,
                                 help_text='对于通过后台管理入口添加者，记录用户信息')
    update_time = models.DateTimeField(u'更新时间', blank=True, null=True, auto_now=True)
    update_by = models.CharField(u'更新人', max_length=32, null=True, blank=True,
                                 help_text='对于通过后台管理入口添加者，记录用户信息')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = verbose_name = u'等级系列'


class RankTitle(models.Model):
    name = models.CharField('等级名称', max_length=20, null=False, blank=False)
    series = models.ForeignKey(RankSeries, blank=False, null=False,
                               help_text='所属等级系列')
    left_value = models.PositiveIntegerField('指标下限', default=0, null=False, blank=False,
                                             help_text='即该等级对应的指标下限，大于该指标则为该指定称号')
    right_value = models.PositiveIntegerField('指标上限（包含）', default=0, null=False, blank=False,
                                              help_text='即该等级对应的指标上限，大于该指标则为上一级指定称号')
    image = models.ForeignKey('filemgmt.BaseImage', verbose_name='等级图片', null=True, blank=True,
                              related_name='+', help_text='等级对应的图片，可以没有')
    create_time = models.DateTimeField(u'创建时间', blank=True, null=True, auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间', blank=True, null=True, auto_now=True)

    def __unicode__(self):
        return "%s:%s" % (self.series.name, self.name)

    class Meta:
        verbose_name_plural = verbose_name = u'等级名称'


class MedalCatalog(models.Model):
    """
    勋章目录
    """
    code = models.CharField('编码', max_length=20, null=False, blank=False, unique=True,
                            help_text='勋章编码，用于前端引用，需要保持唯一，比如用名称拼音首字母')
    name = models.CharField('名称', max_length=20, null=False, blank=False)
    threshold = models.PositiveIntegerField('获取条件阈值', default=1, null=False, blank=False,
                                            help_text='比如订单结算达到10000元，回答问答数量达到50次等')
    remark = models.CharField('说明', max_length=512, null=False, blank=False)
    image = models.ForeignKey('filemgmt.BaseImage', verbose_name='勋章图片', null=False, blank=False,
                              related_name='+', help_text='勋章对应的图片')
    image2 = models.ForeignKey('filemgmt.BaseImage', verbose_name='未激活勋章图片', null=True, blank=True,
                               related_name='+', help_text='勋章未激活时对应的图片')
    list_order = models.PositiveIntegerField('排序标记', default=0, help_text='数值越大，排序越靠前')
    create_time = models.DateTimeField(u'创建时间', blank=True, null=True, auto_now_add=True)
    create_by = models.CharField(u'创建人', max_length=32, null=True, blank=True,
                                 help_text='对于通过后台管理入口添加者，记录用户信息')
    update_time = models.DateTimeField(u'更新时间', blank=True, null=True, auto_now=True)
    update_by = models.CharField(u'更新人', max_length=32, null=True, blank=True,
                                 help_text='对于通过后台管理入口添加者，记录用户信息')

    def __unicode__(self):
        return self.name

    def to_dict(self):
        res = {
            "code": self.code,
            "name": self.name,
            "threshold": self.threshold,
            "remark": self.remark,
            "image": self.image.large,
            "image2": self.image2.large if self.image2_id else '',
            "list_order": self.list_order
        }
        return res

    class Meta:
        ordering = ['-list_order', 'id']
        verbose_name = verbose_name_plural = '勋章目录'


class UserTitle(models.Model):
    """
    用户使用某个等级系列中的称号
    """
    uid = models.CharField(u'用户UID', max_length=32, null=False, blank=False, unique=True,
                           help_text='对于普通用户是用户的UID，对于供应商，则是"SUP-"前缀 + 供应商编码，如"SUP-TWOHOU"')
    series = models.ForeignKey(RankSeries, blank=False, null=False,
                               help_text='所属等级系列')
    update_time = models.DateTimeField(u'更新时间', blank=True, null=True, auto_now=True)

    def __unicode__(self):
        return self.uid

    class Meta:
        verbose_name = verbose_name_plural = '用户称号'


class UserMedal(models.Model):
    uid = models.CharField(u'用户UID', max_length=32, null=False, blank=False, db_index=True,
                           help_text='对于普通用户是用户的UID，对于供应商，则是"SUP-"前缀 + 供应商编码，如"SUP-TWOHOU"')
    medal = models.ForeignKey(MedalCatalog, blank=False, null=False,
                              help_text='用户获得的勋章')
    grant_time = models.DateTimeField(u'授予时间', blank=True, null=True, auto_now=True)

    def __unicode__(self):
        return self.uid

    class Meta:
        unique_together = ['uid', 'medal']
        verbose_name = verbose_name_plural = '用户勋章'
