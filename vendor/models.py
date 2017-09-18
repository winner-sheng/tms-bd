# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, transaction
from django.db.models import Sum
from django.contrib.auth.models import User
from filemgmt.models import BaseImage
from util import renderutil
from ueditor.models import UEditorField
from django.forms.models import model_to_dict
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from tms.config import PROVINCES
from django.utils import timezone
from tms import settings
from util.renderutil import logger, now
from django.utils.functional import cached_property
from datetime import timedelta, datetime
from django.utils.safestring import mark_safe
from config.models import AppSetting


class Contact(models.Model):
    name = models.CharField('联系人', max_length=30, blank=True, null=True, unique=True)
    mobile = models.CharField('手机', max_length=13, blank=True, null=True)
    phone = models.CharField('固定电话', max_length=15, blank=True, null=True)
    qq = models.CharField('QQ', max_length=15, blank=True, null=True)
    wechat = models.CharField('微信', max_length=30, blank=True, null=True)
    email = models.EmailField('Email', max_length=60, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def to_dict(self, detail=False):
        exclude = [] if detail else ['qq', 'wechat', ]
        # exclude = [] if detail else ['phone', 'qq', 'wechat', ]
        return model_to_dict(self, exclude=exclude)

    class Meta:
        ordering = ['name', ]
        verbose_name_plural = verbose_name = '商家 - 联系人'


class BusinessEntity(models.Model):
    """
    商家抽象类（可扩展为产品生产商、供应商、销售商、物流提供商等）
    """
    SETTLEMENT_ONLINE = 0  # 线上结算
    SETTLEMENT_OFFLINE = 1  # 线下结算
    SETTLEMENT_OTHER = 2  # 其他
    SETTLEMENT = (
        (SETTLEMENT_ONLINE, u'线上结算'),
        (SETTLEMENT_OFFLINE, u'线下结算'),
        (SETTLEMENT_OTHER, u'其他')
    )
    settlement = models.PositiveSmallIntegerField(u'结算方式', default=SETTLEMENT_ONLINE, choices=SETTLEMENT)

    code = models.CharField("编码", unique=True, max_length=32, null=False, blank=False,
                            default=renderutil.random_code, help_text=mark_safe('可自动生成，建议统一使用用拼音首字母作为编码'
                                                                                '(注："TWOHOU-"前缀为专用)'))
    name = models.CharField("名称", unique=True, max_length=50, null=False, blank=False)
    intro = UEditorField('简介', max_length=10000, blank=True, null=True, width=900, height=600,)
    logo = models.ForeignKey(BaseImage, related_name='company_logo+', on_delete=models.SET_NULL,
                             blank=True, null=True, limit_choices_to={"usage": BaseImage.USAGE_LOGO})
    homepage = models.URLField('网址(http://)', blank=True, null=True)
    phone = models.CharField('联系电话', max_length='16', blank=True, null=True)
    fax = models.CharField('传真', max_length='16', blank=True, null=True)
    primary_contact = models.ForeignKey(Contact, verbose_name="主联系人", on_delete=models.SET_NULL,
                                        related_name='primary_contact+', blank=True, null=True)
    backup_contact = models.ForeignKey(Contact, verbose_name="备联系人", on_delete=models.SET_NULL,
                                       related_name='backup_contact+', blank=True, null=True)
    province = models.CharField("所在省/直辖市/自治区", choices=PROVINCES, max_length=10, null=True, blank=True)
    city = models.CharField("所在城市", max_length=10, null=True, blank=True)
    address = models.CharField('地址', max_length=100, blank=True, null=True)
    post_code = models.CharField('邮编', max_length=8, blank=True, null=True)
    lng = models.FloatField('经度', default=0, blank=True, null=True)  #
    lat = models.FloatField('纬度', default=0, blank=True, null=True)
    # 经纬度hash编码，用于快速进行周边搜索
    geo_hash = models.CharField(max_length=16, blank=True, null=True, db_index=True, editable=False)
    is_active = models.BooleanField("是否有效", default=True, null=False, blank=False)
    is_verified = models.BooleanField("是否已认证", default=True, null=False, blank=False)
    # 以下字段信息用于排序、筛选及安全审计
    create_time = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True, editable=False)
    create_by = models.IntegerField('创建人', blank=True, null=True, editable=False)
    update_time = models.DateTimeField('更新时间', auto_now=True, blank=True, null=True, editable=False)
    update_by = models.IntegerField('更新人', blank=True, null=True, editable=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # 清除不安全的html代码
        if self.intro and self.intro.find('<') != -1:
            self.intro = renderutil.purify_html(self.intro)

        if self.pk:  # clear keys if updated
            cache_key = "%s-%s" % (self._meta.model_name, self.pk)
            cache.delete_many(["%s-%s" % (cache_key, k) for k in [0, 1, 2]])

        super(BusinessEntity, self).save(force_insert, force_update, using, update_fields)

    def __unicode__(self):
        return self.name

    def get_logo(self):
        return self.logo.thumbnail if self.logo else ''

    def get_phone(self):
        """
        获取联系人的电话列表-mobile
        """
        res = []
        if self.primary_contact_id and self.primary_contact.mobile:
            res.append(self.primary_contact.mobile)
        if self.backup_contact_id and self.backup_contact.mobile:
            res.append(self.backup_contact.mobile)

        return res

    def get_phone_phone(self):
        """
        获取联系人的电话列表-phone
        """
        res = []
        if self.primary_contact_id and self.primary_contact.phone:
            res.append(self.primary_contact.phone)
        if self.backup_contact_id and self.backup_contact.phone:
            res.append(self.backup_contact.phone)

        return res

    def get_email_to(self):
        """
        获取联系人的邮件列表
        """
        res = []
        if self.primary_contact_id and self.primary_contact.email:
            res.append(self.primary_contact.email)
        if self.backup_contact_id and self.backup_contact.email:
            res.append(self.backup_contact.email)

        return res

    def to_dict(self, detail=False):
        cache_key = "%s-%s-%s" % (self._meta.model_name, self.pk, 1 if detail else 2)
        cached_val = cache.get(cache_key)
        if cached_val:
            return cached_val
        else:
            if detail:
                res = model_to_dict(self, exclude=['logo', 'primary_contact', 'backup_contact'])
                res['primary_contact'] = self.primary_contact.to_dict() if self.primary_contact else None
                res['backup_contact'] = self.backup_contact.to_dict() if self.backup_contact else None
            else:
                res = model_to_dict(self, fields=['id', 'code', 'name', 'province', 'city', 'address'])
                res['primary_contact'] = self.primary_contact.name if self.primary_contact else ''

            res['logo'] = self.logo.origin.url if self.logo else ''
            cache.set(cache_key, res)
            return res

    class Meta:
        abstract = True


class Supplier(BusinessEntity):
    @property
    def capital_accounts(self):
        if self.id:
            from profile.models import UserCapitalAccount
            accounts = UserCapitalAccount.objects.filter(uid='SUP-%0*d' % (12, self.id))
            return accounts
        else:
            return []

    def to_dict(self, detail=False):
        res = super(Supplier, self).to_dict(detail)

        cur_time = now(settings.USE_TZ)
        res['notices'] = self.notices.filter(effective_time__lte=cur_time, expire_time__gt=cur_time)\
            .values_list('content', flat=True)
        if detail:
            res['capital_account'] = [model_to_dict(acct) for acct in self.capital_accounts]
            # if self.capital_account_id:
            #     acct = model_to_dict(self.capital_account)
            #     res['capital_account'] = acct

        return res

    def get_email_to(self):
        emails = []
        try:
            emails = super(Supplier, self).get_email_to()
            managers = self.suppliermanager_set.all()
            for mgr in managers:
                if mgr.user.email:
                    emails.append(mgr.user.email)
        except ObjectDoesNotExist:
            pass
        return emails

    def get_binded_uid(self):
        from profile.models import EndUserExt
        managers = self.suppliermanager_set.all()
        usernames = [mgr.user.username for mgr in managers]
        uids = EndUserExt.objects.filter(ex_id_type=EndUserExt.ID_TYPE_INTERNAL,
                                         ex_id__in=usernames).values_list('uid', flat=True)
        # open_ids = EndUserExt.objects.filter(ex_id_type=EndUserExt.ID_TYPE_WECHAT_OPENID,
        #                                      uid__in=uids).values_list('ex_id', flat=True)

        return uids

    class Meta:
        ordering = ['code', ]
        verbose_name_plural = verbose_name = '商家 - 商品供应商'


def _expire_time():
    return renderutil.now(settings.USE_TZ, timedelta(days=7))


class SupplierNotice(models.Model):
    supplier = models.ForeignKey(Supplier, verbose_name='所属供应商', related_name='notices',
                                 null=False, blank=False)
    content = models.CharField('通告内容', max_length=1024, null=False, blank=False,
                               help_text=mark_safe('请填写纯文本内容。<br>'
                                                   '<strong>注意，此处填写的内容，将在用户添加商品到购物车时，'
                                                   '提示给用户</strong>'))
    effective_time = models.DateTimeField('生效时间', default=datetime.now, blank=False, null=False)
    expire_time = models.DateTimeField('失效时间', default=_expire_time, blank=False, null=False,
                                       help_text='默认有效期为7天')

    # 以下字段信息用于排序、筛选及安全审计
    create_time = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True, editable=False)
    create_by = models.CharField(u'创建人', max_length=32, null=True, blank=True,
                                 help_text='对于通过后台管理入口添加者，记录username，通过接口的记录用户uid信息')
    update_time = models.DateTimeField('更新时间', auto_now=True, blank=True, null=True, editable=False)
    update_by = models.CharField(u'更新人', max_length=32, null=True, blank=True,
                                 help_text='对于通过后台管理入口添加者，记录username，通过接口的记录用户uid信息')

    def __unicode__(self):
        return "%s(%s)" % (self.supplier.name, self.pk)

    class Meta:
        ordering = ['effective_time', ]
        verbose_name_plural = verbose_name = '商家 - 商品供应商 - 消息通告'


class Hotel(BusinessEntity):
    tags = models.CharField('标签', max_length=255, null=True, blank=True,
                            help_text='多个标签用英文逗号分隔，如“超值,免费wifi,交通方便”')
    link_to_book1 = models.CharField('订房链接', max_length=255, null=True, blank=True)
    link_to_book2 = models.CharField('订房链接', max_length=255, null=True, blank=True)

    @cached_property
    def images(self):
        images = self.hotel_images.all()
        res = [img.large for img in images]
        return res

    def to_dict(self, detail=False):
        res = super(Hotel, self).to_dict(detail)
        res['tags'] = self.tags
        hotel_imgs = self.images
        if detail:
            res.update({
                'images': hotel_imgs,
                'link_to_book1': self.link_to_book1,
                'link_to_book2': self.link_to_book2,
            })
        else:
            res['image'] = hotel_imgs[0] if hotel_imgs else None

        return res

    class Meta:
        ordering = ['name', ]
        verbose_name_plural = verbose_name = '商家 - 酒店/民宿'


class HotelImage(BaseImage):
    # 如果外键记录被删除，则自动删除相应的本地记录
    hotel = models.ForeignKey(Hotel, verbose_name='酒店', related_name="hotel_images",
                              on_delete=models.CASCADE, null=False, blank=False)
    # image = models.ForeignKey(BaseImage, verbose_name='图片', on_delete=models.CASCADE)
    list_order = models.PositiveIntegerField('排序标记', default=0, help_text='数值越大，排序越靠前')

    def __unicode__(self):
        return self.origin.url

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.image_desc = self.image_desc or self.hotel.name
        super(HotelImage, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        ordering = ('-list_order',)
        verbose_name_plural = verbose_name = '酒店图片'


class SalesAgent(BusinessEntity):
    """
    销售商，商品发布平台，用户下订单入口：如
        RJ -> 如家,
        HT -> 汉庭,
        BD -> 布丁,
    """

    class Meta:
        ordering = ['code', ]
        verbose_name_plural = verbose_name = '销售渠道'


class Manufacturer(BusinessEntity):
    pass

    class Meta:
        ordering = ['code', ]
        verbose_name_plural = verbose_name = '商家 - 生产厂家'


class LogisticsVendor(BusinessEntity):

    class Meta:
        ordering = ['-is_active', 'code', ]
        verbose_name_plural = verbose_name = '商家 - 物流服务商'


class Store(BusinessEntity):
    # 二维码入口地址形如：
    #   http://商城地址?sc=门店编码
    # coupon = models.CharField('优惠码', max_length=16, null=True, blank=True, db_index=True,
    #                           help_text='优惠码仅用于判别门店，如需设定特定门店的优惠规则，请到优惠规则管理界面')
    # rule = models.ForeignKey('config.CouponSetting', null=True, blank=True,
    #                          help_text='默认规则为优惠规则设置中应用于“门店优惠码”的规则，如有指定(优先级需比前者高)，则使用指定的规则')
    # manager = models.ForeignKey(Contact, verbose_name="店长", related_name='manager+', blank=True, null=True)
    owner_uid = models.CharField(u'店主UID', max_length=32, null=True, blank=True, db_index=True)
    capital_account = models.ForeignKey('profile.UserCapitalAccount', verbose_name=u"资金账号",
                                        related_name='+', blank=True, null=True,
                                        help_text=u'用于给店铺账号打款')

    class Meta:
        ordering = ['code', ]
        verbose_name_plural = verbose_name = '商家 - 门店'


class StoreAgent(models.Model):
    store = models.ForeignKey(Store, verbose_name="门店", null=False, blank=False)
    user = models.OneToOneField(User, verbose_name="前台用户", null=False, blank=False)

    def __unicode__(self):
        return "[%s]%s" % (self.store.name, self.user.get_full_name())

    class Meta:
        verbose_name_plural = verbose_name = '门店 - 前台用户'


class SupplierManager(models.Model):
    supplier = models.ForeignKey(Supplier, verbose_name="供应商", null=False, blank=False)
    user = models.ForeignKey(User, verbose_name="供应商管理员账号", null=False, blank=False)

    def __unicode__(self):
        return "[%s]%s" % (self.supplier.name, self.user.get_full_name())

    class Meta:
        verbose_name_plural = verbose_name = '商家 - 商品供应商 - 管理员账号'


class SupplierSalesIncome(models.Model):
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
    supplier = models.ForeignKey(Supplier, verbose_name="供应商", null=False, blank=False)
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
    def summary(supplier_id):
        """
        按指定供应商汇总统计收入情况
        :param supplier_id:
        :return:
        """
        incomes = SupplierSalesIncome.objects.filter(supplier_id=supplier_id).values('status').annotate(
            total_income=(Sum('product_cost') + Sum('ship_fee') + Sum('adjust_fee'))
        )
        result = {}
        status_dict = dict(SupplierSalesIncome.INCOME_STATUS)
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
            self.status = SupplierSalesIncome.INCOME_REVOKED
            self.revoked_time = renderutil.now(settings.USE_TZ)
            self.save()

    def charge(self):
        if self.account_no:
            return False
        elif self.status == SupplierSalesIncome.INCOME_TO_BE_SETTLED:
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
                uid="SUP-%s" % str(self.supplier_id).zfill(12),
                figure=figure,
                is_income=True,
                type='sales',
                account_desc=desc,
                extra_type='basedata.Order',
                extra_data=self.order_no,
                effective_time=now(settings.USE_TZ) + delta
            )
            self.status = SupplierSalesIncome.INCOME_SETTLED
            self.account_no = book.account_no
            self.settled_time = renderutil.now(settings.USE_TZ)
            self.save()
            # SupplierSalesIncome.objects.filter(account_no=book.account_no).update(status=SupplierSalesIncome.INCOME_SETTLED)
            return True
        else:
            raise ValueError(u'当前收入暂不可入账(id: %s)' % self.pk)

    def charge_now(self):
        if self.account_no:
            return False
        elif self.status == SupplierSalesIncome.INCOME_TO_BE_SETTLED:
            if self.has_doubt:
                raise ValueError('订单[%s]收入有疑问，暂不可结算' % self.order_no)

            desc = '[%s]订单销售收入' % self.order_no

            from profile.models import UserAccountBook
            figure = self.product_cost or 0
            figure += (self.ship_fee or 0)
            figure += (self.adjust_fee or 0)
            book = UserAccountBook.objects.create(
                uid="SUP-%s" % str(self.supplier_id).zfill(12),
                figure=figure,
                is_income=True,
                type='sales',
                account_desc=desc,
                extra_type='basedata.Order',
                extra_data=self.order_no,
                effective_time=now(settings.USE_TZ)
            )
            self.status = SupplierSalesIncome.INCOME_SETTLED
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

        super(SupplierSalesIncome, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name_plural = verbose_name = '供应商销售收入'


class Brand(models.Model):
    name = models.CharField("品牌名称", max_length=20, null=False, blank=False, unique=True)
    supplier = models.ForeignKey('vendor.Supplier', verbose_name='供应商', null=True, blank=True)
    list_order = models.PositiveIntegerField('排序标记', default=0, help_text='数值越大，排序越靠前')

    @staticmethod
    def initialize():
        from basedata.models import Product
        brands = Product.objects.values_list('brand_id', 'supplier_id').distinct().order_by('brand_id')
        brands_saved = Brand.objects.values_list('name', 'supplier_id').distinct().order_by('name')
        difference = set(brands) - set(brands_saved)
        for name, sup_id in difference:
            if name:
                try:
                    Brand.objects.create(name=name, supplier_id=sup_id)
                except:
                    pass
        logger.debug("total %s brands initialized" % len(difference))

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('-list_order', 'name')
        verbose_name_plural = verbose_name = '品牌'


