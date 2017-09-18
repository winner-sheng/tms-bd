# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.forms.models import model_to_dict
from profile.models import _uuid
from util import renderutil
from tms import settings
from util.renderutil import logger, random_str, random_code, now
from django.db.models import Sum
from django.utils import timezone
from basedata.models import Product
from django.core.exceptions import ObjectDoesNotExist


def _default_shop_code():
    return "S%s" % (renderutil.random_num(7))


class ShopkeeperInfo(models.Model):
    """
    店主信息表
    """
    # 0:待审核，1：审核通过, 2:审核不通过
    STATUS_AUDITING_WAITTING = 0
    STATUS_AUDITING_APPLYED = 1
    STATUS_AUDITING_REJECTED = 2
    STATUS_AUDITING_TYPES = (
        (STATUS_AUDITING_WAITTING, '待审核'),
        (STATUS_AUDITING_APPLYED, '审核通过'),
        (STATUS_AUDITING_REJECTED, '审核不通过'),
    )
    # uid = models.CharField(u'用户UID', max_length=32, default=_uuid, null=False, blank=False, primary_key=True)
    uid = models.CharField(u'用户UID', max_length=32, null=False, blank=False, db_index=True,
                           help_text=u'布丁帐号系统的用户UID')
    wx_openid = models.CharField(u'微信公众号ID', max_length=64, null=False, blank=False, db_index=True,
                                 help_text=u'微信公众号ID')
    truename = models.CharField(u'姓名/名称', max_length=64, null=False, blank=False, db_index=True,
                                help_text=u'个人真实名称')
    mobile = models.CharField(u'手机号码', max_length=15, null=True, blank=True, help_text=u'手机号码')
    city = models.CharField(u'所在城市', max_length=30, null=True, blank=True, help_text=u'所在城市拼音')
    id_card = models.CharField(u'身份证号码', max_length=32, null=False, blank=False, help_text=u'身份证号码')
    photo = models.CharField(u'身份证正面', max_length=255, null=False, blank=False, help_text=u'身份证正面')
    photoReverse = models.CharField(u'身份证反面', max_length=255, null=False, blank=False, help_text=u'身份证反面')
    rejectmessage = models.CharField(u'拒绝信息', max_length=45, null=True, blank=True, help_text=u'拒绝信息')
    state = models.PositiveSmallIntegerField(u'业主审核状态', default=STATUS_AUDITING_WAITTING,
                                             choices=STATUS_AUDITING_TYPES, db_index=True,
                                             help_text=u'业主审核状态')

    create_time = models.DateTimeField(u'创建时间', blank=True, null=True, auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间', blank=True, null=True)
    create_by = models.CharField(u'创建人', max_length=32, null=True, blank=True,
                                 help_text=u'对于通过后台管理入口添加者，记录用户信息')

    def to_dict(self):
        return model_to_dict(self)

    def audited(self):
        """
        （管理员）审核通过店主信息
        """
        if self.state != self.STATUS_AUDITING_WAITTING:
            raise ValueError(u'不是待审核状态待的申请不可审核确认通过！')

        self.state = self.STATUS_AUDITING_APPLYED
        self.update_time = now(settings.USE_TZ)
        self.save()

        # TODO: may do sth. if failed
        return 0

    def rejectd(self):
        """
        （管理员）审核拒绝店主信息
        """
        if self.state != self.STATUS_AUDITING_WAITTING:
            raise ValueError(u'不是待审核状态待的申请不可审核确认通过！')

        self.state = self.STATUS_AUDITING_REJECTED
        self.update_time = now(settings.USE_TZ)
        self.save()

        # TODO: may do sth. if failed
        return 0

    class Meta:
        ordering = ['-pk']
        verbose_name_plural = verbose_name = u'店主信息表'


class SaleShop(models.Model):
    """
    店铺信息表
    """
    #     status: { //状态:0:审核中, 1:开张中,2:休息中
    STATUS_SHOPSTORE_WATTING_FOR_APPLY = 0
    STATUS_SHOPSTORE_IS_OPEN = 1
    STATUS_SHOPSTORE_IS_CLOSED = 2
    STATUS_SHOPSTORE_TYPES = (
        (STATUS_SHOPSTORE_WATTING_FOR_APPLY, '审核中'),
        (STATUS_SHOPSTORE_IS_OPEN, '开业中'),
        (STATUS_SHOPSTORE_IS_CLOSED, '休息中'),
    )

    SHOPTYPE_ZHIYINGDIAN = 0
    SHOPTYPE_JIAMENGDIAN = 1
    TYPES_OF_SHOP = (
        (SHOPTYPE_ZHIYINGDIAN, '直营店'),
        (SHOPTYPE_JIAMENGDIAN, '加盟店'),
    )

    code = models.CharField(u'店铺代码', max_length=16, null=False, blank=False, primary_key=True,
                            default=_default_shop_code, help_text=u'店铺代码')
    # code = models.CharField(u'店铺代码', max_length=32, null=False, blank=False, db_index=True,
    #                         help_text=u'店铺代码')
    name = models.CharField(u'店铺名称', max_length=32, null=False, blank=False, db_index=True,
                            help_text=u'店铺名称')
    qrcode = models.CharField(u'店铺二维码', max_length=255, null=True, blank=True,
                              help_text=u'店铺名称')
    keeperqrcode = models.CharField(u'店主邀请二维码', max_length=255, null=True, blank=True,
                                    help_text=u'店主邀请二维码')
    shopicon = models.CharField(u'店铺头像', max_length=255, null=True, blank=True,
                                help_text=u'店铺头像')
    cover = models.CharField(u'封面', max_length=255, null=True, blank=True,
                             help_text=u'封面')
    watchcount = models.PositiveIntegerField(u'关注人数', null=False, blank=False, default=0,
                                             help_text=u'微信关注人数')
    state = models.PositiveSmallIntegerField(u'店铺状态', default=STATUS_SHOPSTORE_WATTING_FOR_APPLY,
                                             choices=STATUS_SHOPSTORE_TYPES, db_index=True,
                                             help_text=u'店铺状态')
    shop_type = models.PositiveSmallIntegerField(u'店铺类型', default=SHOPTYPE_ZHIYINGDIAN,
                                                 choices=TYPES_OF_SHOP, db_index=True,
                                                 help_text=u'店铺类型')
    uid = models.CharField(u'店主UID', max_length=32, null=True, blank=True, db_index=True,
                           help_text=u'店主UID')
    # province:Sequelize.STRING(32), // 省
    # city:Sequelize.STRING(32), // 市
    # district:Sequelize.STRING(32), // 区
    # address:Sequelize.STRING(512), // 详细地址
    province = models.CharField(u'省', max_length=32, null=True, blank=True,
                                help_text=u'所在省份')
    city = models.CharField(u'市', max_length=32, null=True, blank=True,
                            help_text=u'所在城市')
    district = models.CharField(u'区', max_length=32, null=True, blank=True,
                                help_text=u'所在区')
    address = models.CharField(u'地址', max_length=512, null=True, blank=True,
                               help_text=u'详细地址')
    create_time = models.DateTimeField(u'创建时间', blank=True, null=True, auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间', blank=True, null=True)
    create_by = models.CharField(u'创建人', max_length=32, null=True, blank=True,
                                 help_text=u'对于通过后台管理入口添加者，记录用户信息')

    def applied(self):
        """
        （管理员）审核通过店主信息
        """
        if self.state != self.STATUS_SHOPSTORE_WATTING_FOR_APPLY:
            raise ValueError(u'不是待审核状态待的申请不可审核确认通过！')

        self.state = self.STATUS_SHOPSTORE_IS_OPEN
        self.update_time = now(settings.USE_TZ)
        self.save()

        # TODO: may do sth. if failed
        return 0

    def closed(self):
        """
        （管理员）审核拒绝店主信息
        """
        if self.state != self.STATUS_AUDITING_WAITTING:
            raise ValueError(u'不是待审核状态待的申请不可审核确认通过！')

        self.state = self.STATUS_SHOPSTORE_IS_CLOSED
        self.update_time = now(settings.USE_TZ)
        self.save()

    def __str__(self):
        """
        Return the representation field or fields.
        """
        return '%s-%s-%s-%s' % (self.code, self.province, self.city, self.name)

        # TODO: may do sth. if failed
        return 0

    def to_dict(self):
        return model_to_dict(self, exclude=['create_time', 'update_time', 'create_by'])

    class Meta:
        # ordering = ['-pk']
        verbose_name_plural = verbose_name = u'店铺信息表'


class SaleShopProduct(models.Model):
    """
    店铺商品表
    """
    # STATUS_PRESHELF = 0
    # STATUS_ONSHELF = 1
    # STATUS_OFFSHELF = 2
    # STATUS_ONSHELF_FOR_REVIEW = 3  # 用于供应商上架的商品审核
    # # STATUS_NOT_REVIEWED = 99
    # RECORD_STATUS = (
    #     (STATUS_PRESHELF, '待上架'),
    #     (STATUS_ONSHELF_FOR_REVIEW, '上架(待审核)'),
    #     (STATUS_ONSHELF, '上架'),
    #     (STATUS_OFFSHELF, '已下架'),
    #     # (STATUS_RESHELF, '重新上架'),
    # )
    STATUS_PRESHELF = 0
    STATUS_ONSHELF = 1
    STATUS_OFFSHELF = 2
    RECORD_STATUS = (
        (STATUS_PRESHELF, '待上架'),
        (STATUS_ONSHELF, '上架'),
        (STATUS_OFFSHELF, '已下架'),
    )
    shopcode = models.CharField(u'店铺代码', max_length=16, null=False, blank=False, db_index=True,
                                help_text=u'店铺代码')
    productid = models.CharField(u'商品代码', max_length=32, null=False, blank=False, db_index=True,
                                 help_text=u'商品代码')
    status = models.PositiveSmallIntegerField('商品状态', default=0, choices=RECORD_STATUS, db_index=True,
                                              help_text=u"只有上架商品才能在商城展示，上架需要确保相关价格信息填写完整")
    retail_price = models.DecimalField(u'零售价￥', max_digits=10, decimal_places=2, null=True, blank=True,
                                       help_text=u'零售价格')
    settle_price = models.DecimalField(u'结算价￥', max_digits=10, decimal_places=2, null=True, blank=True,
                                       help_text=u'结算价格')
    tags = models.CharField(u'商品标签', max_length=128, db_index=True, null=True, blank=True,
                            help_text=u'用于商品搜索，每个标签之间应使用英文逗号","分隔，标签为精确匹配')
    list_order = models.PositiveIntegerField(u'排序标记', default=0, help_text='数值越大，排序越靠前')
    create_time = models.DateTimeField(u'创建时间', blank=True, null=True, auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间', blank=True, null=True)
    create_by = models.CharField(u'创建人', max_length=32, null=True, blank=True,
                                 help_text=u'对于通过后台管理入口添加者，记录用户信息')

    def to_dict(self):
        return model_to_dict(self, exclude=['create_time', 'update_time', 'create_by'])

    def put_offshelf(self):
        """
        下架商品
        """
        self.status = SaleShopProduct.STATUS_OFFSHELF
        self.update_time = now(settings.USE_TZ)
        self.save()
        # tms_signals.product_offshelf.send(Product, obj=self)

    def put_onshelf(self):
        """
        上架商品
        """
        self.status = SaleShopProduct.STATUS_ONSHELF
        self.update_time = now(settings.USE_TZ)
        # self.clean()
        self.save()
        # tms_signals.product_onshelf.send(Product, obj=self)

    class Meta:
        # ordering = ['-pk']
        verbose_name_plural = verbose_name = u'店铺商品表'


class ShopManagerInfo(models.Model):
    """
    店长、店员信息表
    """
    ROLE_SHOPSTORE_STAFF = 0
    ROLE_SHOPSTORE_MANAGER = 1
    ROLE_SHOPSTORE_OWNER = 2
    ROLE_SHOPSTORE_TYPES = (
        (ROLE_SHOPSTORE_STAFF, '员工'),
        (ROLE_SHOPSTORE_MANAGER, '经理'),
        (ROLE_SHOPSTORE_OWNER, '店主'),
    )
    uid = models.CharField(u'用户UID', max_length=32, null=False, blank=False, db_index=True,
                           help_text=u'布丁帐号系统的用户UID')
    wx_openid = models.CharField(u'微信公众号ID', max_length=64, null=False, blank=False, db_index=True,
                                 help_text=u'微信公众号ID')
    truename = models.CharField(u'姓名/名称', max_length=64, null=False, blank=False, db_index=True,
                                help_text=u'个人真实名称')
    mobile = models.CharField(u'手机号码', max_length=15, null=True, blank=True, help_text=u'手机号码')
    shopcode = models.CharField(u'店铺代码', max_length=16, null=False, blank=False, db_index=True,
                                default='',
                                help_text=u'店铺代码')
    role = models.PositiveSmallIntegerField(u'职位', default=ROLE_SHOPSTORE_STAFF,
                                            choices=ROLE_SHOPSTORE_TYPES, db_index=True,
                                            help_text=u'职位')
    # pid = models.PositiveIntegerField('pid', null=False, blank=False, default=0)
    pid = models.CharField(u'推荐人UID', max_length=32, null=True, blank=True, db_index=True,
                           help_text=u'推荐人的UID')
    is_active = models.BooleanField(u'是否有效', default=True, blank=False, null=False,
                                    help_text='是否有效，推荐人关系删除的话，将置为False')
    reward_percent = models.PositiveSmallIntegerField(u'分佣百分比', default=75, blank=False, null=False,
                                                      help_text=u'分佣百分比，75表示个人得75%，25%给店长')
    create_time = models.DateTimeField(u'创建时间', blank=True, null=True, auto_now_add=True)
    update_time = models.DateTimeField(u'更新时间', blank=True, null=True)
    create_by = models.CharField(u'创建人', max_length=32, null=True, blank=True,
                                 help_text=u'对于通过后台管理入口添加者，记录用户信息')

    class Meta:
        # ordering = ['-pk']
        verbose_name_plural = verbose_name = u'店长及店员信息表'


class SaleShopIncome(models.Model):
    INCOME_PENDING = 0  # 待确认，用户尚未签收
    INCOME_TO_BE_SETTLED = 1  # 待结算
    INCOME_SETTLED = 2  # 已结算
    INCOME_REVOKED = 3  # 已取消，即订单已取消或退款
    INCOME_STATUS = (
        (INCOME_PENDING, '待确认'),
        (INCOME_TO_BE_SETTLED, '待结算'),
        (INCOME_SETTLED, '已结算'),
        (INCOME_REVOKED, '已取消'),
    )
    code = models.ForeignKey(SaleShop, verbose_name="店铺", null=False, blank=False)
    order_no = models.CharField("订单编号", max_length=20, blank=False, null=False, db_index=True)
    activity_code = models.CharField('活动代码', max_length=32, null=True, blank=True,
                                     help_text='用于特定场景下产生的订单，比如某个营销活动')
    product_cost = models.DecimalField('商品销售收入', max_digits=10, decimal_places=2, default=0,
                                       blank=True, null=True,
                                       help_text="即订单中该供应商销售的商品成本*商品数量")
    ship_fee = models.DecimalField('邮费收入', max_digits=10, decimal_places=2, default=0,
                                   blank=True, null=True, help_text="邮费收入应扣除邮费优惠部分")
    adjust_fee = models.DecimalField('手工调节的费用', max_digits=10, decimal_places=2, default=0,
                                     blank=True, null=True, help_text="根据需要手工调节")
    has_doubt = models.BooleanField('是否有疑问', default=False,
                                    help_text='收入如果标注为有疑问，则暂时不可结算，已结算的也将撤销')
    memo = models.CharField('备注', max_length=32, null=True, blank=True)
    status = models.PositiveSmallIntegerField(u'收入状态', default=INCOME_PENDING, choices=INCOME_STATUS)
    settled_time = models.DateTimeField('结算时间', blank=True, null=True,
                                        help_text='结算为手工结算，未手工结算的，'
                                                  '则在订单签收后指定结算周期内自动结算进入供应商流水')
    revoked_time = models.DateTimeField('撤销时间', blank=True, null=True,
                                        help_text='当订单被退款时立即撤销')
    account_no = models.CharField('流水号', max_length=32, null=True, blank=True,
                                  help_text='已结算收益必须有流水号后，才意味着该收益到账')
    create_time = models.DateTimeField('创建时间', blank=True, null=True, default=timezone.now)
    update_time = models.DateTimeField('更新时间', blank=True, null=True, auto_now=True)

    @property
    def order_state(self):
        try:
            from basedata.models import Order
            return Order.objects.get(order_no=self.order_no).get_order_state_display()
        except:
            return 'N/A'

    def __unicode__(self):
        return "%s:%s(%s)" % (self.supplier.name, self.order_no, self.get_status_display())

    @staticmethod
    def summary(code):
        """
        按指定店铺code汇总统计收入情况
        :param code:
        :return:
        """
        incomes = SaleShopIncome.objects.filter(code=code).values('status').annotate(
            total_income=(Sum('product_cost') + Sum('ship_fee') + Sum('adjust_fee'))
        )
        result = {}
        status_dict = dict(SaleShopIncome.INCOME_STATUS)
        for i in incomes:
            result[status_dict[i.get('status')]] = i
        return result

    def charge_back(self):
        from profile.models import UserAccountBook
        if not self.account_no:
            pass
        else:
            account = UserAccountBook.objects.get(account_no=self.account_no)
            account.charge_back()
            self.account_no = None
            self.status = SaleShopIncome.INCOME_REVOKED
            self.revoked_time = renderutil.now(settings.USE_TZ)
            self.save()

    def charge(self):
        if self.account_no:
            return False
        elif self.status == SaleShopIncome.INCOME_TO_BE_SETTLED:
            if self.has_doubt:
                raise ValueError('订单[%s]收入有疑问，暂不可结算' % self.order_no)

            desc = '[%s]订单销售收入' % self.order_no

            from profile.models import UserAccountBook
            figure = self.product_cost or 0
            figure += (self.ship_fee or 0)
            figure += (self.adjust_fee or 0)
            frozen_days = AppSetting.get('app.supplier_income_deferred_days', 7)
            delta = timedelta(days=frozen_days)
            book = UserAccountBook.objects.create(
                uid=self.code,
                figure=figure,
                is_income=True,
                type='sales',
                account_desc=desc,
                extra_type='basedata.Order',
                extra_data=self.order_no,
                effective_time=now(settings.USE_TZ) + delta
            )
            self.status = SaleShopIncome.INCOME_SETTLED
            self.account_no = book.account_no
            self.settled_time = renderutil.now(settings.USE_TZ)
            self.save()
            # SaleShopIncome.objects.filter(account_no=book.account_no).update(status=SaleShopIncome.INCOME_SETTLED)
            return True
        else:
            raise ValueError(u'当前收入暂不可入账(id: %s)' % self.pk)

    def charge_now(self):
        if self.account_no:
            return False
        elif self.status == SaleShopIncome.INCOME_TO_BE_SETTLED:
            if self.has_doubt:
                raise ValueError('订单[%s]收入有疑问，暂不可结算' % self.order_no)

            desc = '[%s]订单销售收入' % self.order_no

            from profile.models import UserAccountBook
            figure = self.product_cost or 0
            figure += (self.ship_fee or 0)
            figure += (self.adjust_fee or 0)
            book = UserAccountBook.objects.create(
                uid=self.code,
                figure=figure,
                is_income=True,
                type='sales',
                account_desc=desc,
                extra_type='basedata.Order',
                extra_data=self.order_no,
                effective_time=now(settings.USE_TZ)
            )
            self.status = SaleShopIncome.INCOME_SETTLED
            self.account_no = book.account_no
            self.settled_time = renderutil.now(settings.USE_TZ)
            self.save()
            # ModelName.objects.filter(id=1).update(name='aaa')
            # SupplierSalesIncome.objects.filter(account_no=book.account_no).update(status=SupplierSalesIncome.INCOME_SETTLED)
            return True
        else:
            raise ValueError(u'当前收入暂不可入账(id: %s)' % self.pk)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.status == self.INCOME_SETTLED and not self.settled_time:
            self.settled_time = renderutil.now(settings.USE_TZ)
        if self.status == self.INCOME_REVOKED and not self.revoked_time:
            self.revoked_time = renderutil.now(settings.USE_TZ)

        super(SaleShopIncome, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name_plural = verbose_name = u'店铺销售收入'


def bd_sync_products():
    p = 0
    s = 0
    # scodes = []  # 所有店铺代码
    # shops = SaleShop.objects.all()  # 所有店铺
    # for shop in shops:
    #     scodes.append(shop.code)

    pcodes = []  # 信息有更新的商品代码

    # prds = Product.objects.filter(status=SaleShopProduct.STATUS_OFFSHELF)  # 所有下架商品
    # for prd in prds:
    #     pcodes.append(prd.code)
    # des_prds = SaleShopProduct.objects.filter(status=SaleShopProduct.STATUS_ONSHELF,
    #                                           productid__in=pcodes)
    # if des_prds:
    #     des_prds.status = SaleShopProduct.STATUS_OFFSHELF
    #     des_prds.update()
    #
    # prds = Product.objects.filter(status=SaleShopProduct.STATUS_ONSHELF)  # 所有上架商品
    # for prd in prds:
    #     pcodes.append(prd.code)
    # des_prds = SaleShopProduct.objects.filter(status=SaleShopProduct.STATUS_OFFSHELF,
    #                                           productid__in=pcodes)
    # if des_prds:
    #     des_prds.status = SaleShopProduct.STATUS_ONSHELF
    #     des_prds.update()

    prds = Product.objects.all()  # 所有商品
    shops = SaleShop.objects.all()  # 在所有店铺新建商品
    for prd in prds:
        try:
            SaleShopProduct.objects.filter(productid=prd.code).update(retail_price=prd.retail_price,
                                                                      settle_price=prd.settle_price,
                                                                      status=prd.status,
                                                                      update_time=renderutil.now(settings.USE_TZ))
        except:
            for shop in shops:
                SaleShopProduct.objects.get_or_create(shopcode=shop.code,
                                                      status=prd.status,
                                                      productid=prd.code,
                                                      # tags=prd.tags,
                                                      # list_order=prd.list_order,
                                                      retail_price=prd.retail_price,
                                                      settle_price=prd.settle_price,
                                                      update_time=renderutil.now(settings.USE_TZ))

# prds = Product.objects.all()  # 所有商品
    # for prd in prds:
    #     p += 1
    #     # shops = SaleShop.objects.all()  # 所有店铺
    #     for shopcode in scodes:
    #         try:
    #             ssp = SaleShopProduct.objects.get(shopcode=shopcode, productid=prd.code)
    #             if ssp.status != prd.status or ssp.retail_price != prd.retail_price \
    #                     or ssp.settle_price != prd.settle_price:
    #                     # or ssp.tags != prd.tags \
    #                     # or ssp.list_order != prd.list_order:
    #                 if ssp.status != SaleShopProduct.STATUS_ONSHELF:
    #                     ssp.status = prd.status
    #                 ssp.retail_price = prd.retail_price
    #                 ssp.settle_price = prd.settle_price
    #                 # ssp.tags = prd.tags
    #                 # ssp.list_order = prd.list_order
    #                 ssp.update_time = renderutil.now(settings.USE_TZ)
    #                 ssp.save()
    #                 s += 1
    #                 pcodes.append(prd.code)
    #         except:
    #             SaleShopProduct.objects.get_or_create(shopcode=shopcode,
    #                                                   status=prd.status,
    #                                                   productid=prd.code,
    #                                                   # tags=prd.tags,
    #                                                   # list_order=prd.list_order,
    #                                                   retail_price=prd.retail_price,
    #                                                   settle_price=prd.settle_price
    #                                                   )
    #             s += 1
    #             pcodes.append(prd.code)

    ids = []
    for s in SaleShopProduct.objects.raw('SELECT * FROM buding_saleshopproduct where productid not in (select code from basedata_product)'):
        ids.append(s.productid)
    SaleShopProduct.objects.filter(productid__in=ids).delete()
    return s


def bd_get_user_by_uid(uid, shopcode):
    try:
        users = ShopManagerInfo.objects.filter(uid=uid, shopcode=shopcode)
    except ObjectDoesNotExist:
        return False
    return True

