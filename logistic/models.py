# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from copy import deepcopy
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import signals
from django.db.models.fields import NOT_PROVIDED

from filemgmt.models import BaseImage
from tms.config import SHIP_STATUS_UNKNOWN, SHIP_STATUS_MAP, SHIP_STATUS_SIGNOFF, PROVINCES

from util.webtool import fetch_json
from util.jsonall import json_encode
from util.renderutil import random_str, logger
from tms.config import SHIP_QUERY_URL, SHIP_QUERY_CALLBACK, SHIP_QUERY_KEY, SHIP_SUBSCRIBE_CODE_MAP, SELF_SHIP_VENDORS
import hashlib
__author__ = 'Winsom'


class Invoice(models.Model):
    INVOICE_TYPES = (
        ('N', '普通发票'),
        ('VAT', '增值税发票'),
    )
    INVOICE_MODES = (
        ('N', '普通发票'),
        ('E', '电子发票'),
    )
    order = models.OneToOneField('basedata.Order', verbose_name="订单",
                                 null=False, blank=False)
    type = models.CharField('发票类型', max_length=3, default='N', null=True, blank=True, choices=INVOICE_TYPES)
    mode = models.CharField('开票方式', max_length=3, default='N', null=True, blank=True, choices=INVOICE_MODES)
    invoice_no = models.CharField('发票代码', max_length=12, default='', null=True, blank=True)
    title = models.CharField("发票抬头", max_length=50, null=True, blank=True,
                             help_text='留空表示个人，否则应填写公司名称')
    amount = models.DecimalField('发票金额', max_digits=10, decimal_places=2, null=False, blank=False)
    require_detail = models.BooleanField('是否需要详情', default=False, help_text='如果需要详情，则按订单内容生成')
    content = models.CharField("发票内容", max_length=30, null=True, blank=True,
                               help_text='如食品，工艺品，日用品等，如果需要详情，则忽略该项')
    made_date = models.DateTimeField('开票时间', null=True, blank=True, help_text='未开票时，该项留空')

    @property
    def is_invoice_made(self):
        return self.made_date is None

    def __unicode__(self):
        return '%s %s: ￥%s' % (self.title or '个人', self.get_type_display(), self.amount)

    class Meta:
        verbose_name_plural = verbose_name = '发票'


class PrintTemplate(models.Model):
    """
    打印模板
    """
    name = models.CharField("模板名称", db_index=True, max_length=30, null=False, blank=False)
    # vendor = models.ForeignKey(Supplier, verbose_name="供应商", null=True, blank=True)
    # version = models.CharField("版本", default='1.0', max_length=10, null=True, blank=True)
    template = models.TextField("模板", max_length=5000, null=True, blank=True)
    TYPE_PRIVATE = 0
    TYPE_PUBLIC = 1
    TYPES = (
        (TYPE_PRIVATE, '私有'),
        (TYPE_PUBLIC, '共享'),
    )
    type = models.SmallIntegerField("类型", default=0, null=True, blank=True, choices=TYPES)
    supplier = models.ForeignKey('vendor.Supplier', verbose_name="供应商", null=True, blank=True)
    # 以下字段信息用于排序、筛选及安全审计
    create_time = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True, editable=False)
    create_by = models.IntegerField('创建人', blank=True, null=True, editable=False)
    update_time = models.DateTimeField('更新时间', auto_now=True, blank=True, null=True, editable=False)
    update_by = models.IntegerField('更新人', blank=True, null=True, editable=False)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True
        unique_together = ['name', 'create_by']
        ordering = ['name', '-update_time']
        verbose_name_plural = verbose_name = '打印单模板'


class InvoiceTemplate(PrintTemplate):
    """
    发货单模板
    """
    class Meta:
        ordering = ['name', '-update_time']
        verbose_name_plural = verbose_name = '模板-发货单'


class ShapeImage(BaseImage):
    """
    快递单模板图片
    """
    pass

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.usage = self.USAGE_EXPRESS_TEMPLATE
        if not self.image_desc:
            self.image_desc = self.origin.name
        super(ShapeImage, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        proxy = True
        verbose_name_plural = verbose_name = '模板 - 快递单图片'


class ExpressTemplate(PrintTemplate):
    """
    快递单模板
    """
    shape_image = models.ForeignKey(ShapeImage, verbose_name="底板图片模板", null=True, blank=True,
                                    limit_choices_to={'usage': ShapeImage.USAGE_EXPRESS_TEMPLATE})

    class Meta:
        ordering = ['name', '-update_time']
        verbose_name_plural = verbose_name = '模板 - 快递单'


class ExpressSender(models.Model):
    """
    寄件人信息
    """
    name = models.CharField('寄件人', max_length=30, blank=False, null=False)
    mobile = models.CharField('手机', max_length=13, blank=True, null=True)
    phone = models.CharField('固定电话', max_length=20, blank=True, null=True)
    province = models.CharField("所在省/直辖市/自治区", choices=PROVINCES, max_length=10, null=False, blank=False)
    city = models.CharField("所在城市", max_length=10, null=True, blank=True)
    address = models.CharField('地址', max_length=100, blank=False, null=False)
    post_code = models.CharField('邮编', max_length=8, blank=True, null=True)
    supplier = models.ForeignKey('vendor.Supplier', verbose_name="供应商", null=False, blank=False)
    # 以下字段信息用于排序、筛选及安全审计
    create_time = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True, editable=False)
    create_by = models.IntegerField('创建人', blank=True, null=True, editable=False)
    update_time = models.DateTimeField('更新时间', auto_now=True, blank=True, null=True, editable=False)
    update_by = models.IntegerField('更新人', blank=True, null=True, editable=False)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = verbose_name = '快递单发件人'


class ShipPackage(models.Model):
    package_no = models.CharField("包裹编号", max_length=20, blank=False, null=False, primary_key=True,
                                  help_text='默认与订单号相同，除非特殊拆单情形使用订单号为前缀')
    order_no = models.CharField("订单编号", max_length=20, blank=False, null=False, db_index=True,
                                help_text='保留')
    receiver = models.CharField("收件人", max_length=30, null=True, blank=True)
    receiver_mobile = models.CharField("收件人电话", max_length=20, null=True, blank=True)
    ship_province = models.CharField("收件省份", choices=PROVINCES, max_length=3, null=True, blank=True)
    ship_address = models.CharField("收件地址", max_length=50, null=True, blank=True)
    ship_vendor = models.ForeignKey('vendor.LogisticsVendor', verbose_name="物流公司", null=True, blank=True,
                                    limit_choices_to={'is_active': True},
                                    on_delete=models.SET_NULL)
    ship_code = models.CharField("物流单号", max_length=20, null=True, blank=True, db_index=True)

    def __unicode__(self):
        return self.package_no

    class Meta:
        verbose_name_plural = verbose_name = '物流包裹'


class ShipItem(models.Model):
    # sid = models.PositiveIntegerField("编码", null=False, default=1)
    # sid = models.PositiveIntegerField('SID', default=0, null=False, blank=False)
    code = models.CharField('编码', null=False, max_length=36, primary_key=True)
    package_no = models.CharField("包裹编号", max_length=20, blank=False, null=False, db_index=True)
    prd_code = models.CharField("商品编码", max_length=16, null=False, blank=False)
    prd_name = models.CharField("商品名称", max_length=40, db_index=True, null=False, blank=False)
    prd_pcs = models.PositiveIntegerField("数量", default=1, null=False, blank=False)

    def __unicode__(self):
        return "%s x %s" % (self.prd_name, self.prd_pcs)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.code:
            self.code = "%s:%s" % (self.package_no, self.prd_code)
        super(ShipItem, self).save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta:
        # unique_together = ['package_no', 'prd_code']
        verbose_name_plural = verbose_name = '物流包裹商品项'


class ShipReport(models.Model):
    # order = models.ForeignKey(Order, verbose_name="订单", null=False, blank=False,
    #                           on_delete=models.CASCADE)
    # order_no = models.CharField("订单编号", max_length=20, blank=True, null=True, unique=True)
    package_no = models.CharField("包裹编号", max_length=20, blank=False, null=False, primary_key=True)
    vendor_code = models.CharField("物流公司编码", max_length=16, null=False, blank=False, db_index=True)
    ship_code = models.CharField("物流单号", max_length=20, null=True, blank=True, db_index=True)
    report = models.CharField("物流状态报告", max_length=4000, null=True, blank=True)
    state = models.PositiveSmallIntegerField("当前状态", default=SHIP_STATUS_UNKNOWN, choices=SHIP_STATUS_MAP)
    latest_status = models.CharField("最新进展", max_length=50, null=True, blank=True)
    update_time = models.DateTimeField('更新时间', auto_now=True, blank=True, null=True, editable=False)

    def __unicode__(self):
        return "%s | %s | %s" % (self.vendor_code, self.ship_code, self.latest_status)

    def refresh(self):
        if self.state == SHIP_STATUS_UNKNOWN:
            return ShipReport.subscribe(self.package_no, self.vendor_code, self.ship_code, '')
        else:
            update_order_ship_state(sender=ShipReport, instance=self, created=False)
            return True

    @staticmethod
    def subscribe(package_no, vendor_code, ship_code, address):
        """
        通过快递100订阅快递信息
        :param vendor_code:
        :param ship_code:
        :param address:
        :return:
        """
        if vendor_code in SELF_SHIP_VENDORS:
            return  # ignore self shipped items
        if not vendor_code or not ship_code:
            raise ValueError('请提供物流服务商(%s)及快递单号(%s)' % (vendor_code, ship_code))
        ship_code = ship_code.strip()
        ship_report, created = ShipReport.objects.update_or_create(package_no=package_no,
                                                                   defaults={
                                                                       "vendor_code": vendor_code,
                                                                       "ship_code": ship_code
                                                                   })
        if created or ship_report.state == SHIP_STATUS_UNKNOWN:
            url = SHIP_QUERY_URL
            param = {
                "schema": "json",
                "param": json_encode({
                     "company": vendor_code,
                     "number": ship_code,
                     "key": SHIP_QUERY_KEY,
                     "parameters": {
                         "callbackurl": SHIP_QUERY_CALLBACK,
                         "salt": hashlib.md5("%s:%s@%s" % (SHIP_QUERY_KEY, ship_code, vendor_code)).hexdigest()[:8]
                     },
                     "from": "",
                     "to": address
                })
            }
            report = fetch_json(url, params=param, method="POST")
            if not report or report.get('returnCode') != '200':
                logger.error(param)
                logger.error(report)
                if report.get('returnCode') != '501':
                    return {'error': '[%s]订阅快递信息失败: %s' % (package_no, SHIP_SUBSCRIBE_CODE_MAP[report.get('returnCode')])}
        else:
            logger.debug(ship_report)
        return True

    class Meta:
        # unique_together = ['vendor_code', 'ship_code']
        ordering = ['-update_time', ]
        verbose_name_plural = verbose_name = '物流状态报告'


def update_order_ship_state(sender, instance, created, **kwargs):
    """
    更新订单状态，当物流状态报告更新触发执行
    :param sender:
    :param instance:
    :param created:
    :param kwargs:
    :return:
    """
    if created:
        return   # ignore while creation
    from basedata.models import Order
    from vendor.models import LogisticsVendor
    try:
        ship_vendor = LogisticsVendor.objects.get(code=instance.vendor_code)
        orders = Order.objects.filter(ship_vendor_id=ship_vendor.id, ship_code=instance.ship_code)
        for order in orders:
            to_update = False
            if instance.state == SHIP_STATUS_SIGNOFF:
                if order.order_state in [Order.STATE_SHIPPED,
                                         Order.STATE_TO_SHIP,
                                         Order.STATE_SHIPPED,
                                         Order.STATE_RECEIVED_BYSELF,
                                         Order.STATE_TO_CLAIM,
                                         Order.STATE_CUSTOMER_SERVICE]:
                    order.ship_signoff()
            logger.debug('%s: %s|%s' % (order.order_no, order.ship_status, instance.get_state_display()))
            if order.ship_status != instance.get_state_display():
                order.ship_status = instance.get_state_display()
                to_update = True
            to_update and order.save()
    except LogisticsVendor.DoesNotExist:
        logger.error('LogisticsVendor NOT found: %s' % instance.vendor_code)
    except Order.DoesNotExist:
        logger.error('Order NOT found with ship codes: %s(%s)' % (instance.ship_code, instance.vendor_code))
    except Exception, e:
        logger.error('Unexpected error in ship update: %s' % e.message)
        logger.exception(e)

signals.post_save.connect(receiver=update_order_ship_state, sender=ShipReport)
