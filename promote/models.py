# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import re
import hashlib

from django.db.models import signals
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.forms.models import model_to_dict
from config.models import AppSetting
from tms.config import REWARD_DEFERRED_DAYS

from ueditor.models import UEditorField
from promote.rules import SCENARIO_GLOBAL, APPLY_TO_SCENARIO, RULE_MAP
from tms import settings
from util import renderutil
from util.renderutil import now, day_str, random_letter, logger
from django.utils.safestring import mark_safe
import uuid

ticket_lock = False


class ComputationRule(models.Model):
    name = models.CharField("优惠/计费规则名称", max_length=30, null=False, blank=False)
    apply_to = models.PositiveSmallIntegerField('适用于（应用场合）', default=SCENARIO_GLOBAL, choices=APPLY_TO_SCENARIO,
                                                help_text='如需限制规则适用于特定门店、供应商、商品，'
                                                          '请在配置中分别使用"stores"/"suppliers"/"products"数组参数。'
                                                          '如果规则适用于所有特定对象，如供应商，可将suppliers设置为["all"]。暂不支持组合条件。')
    RULE_TYPES = (
        ('SimpleReductionRule', RULE_MAP['SimpleReductionRule'].description),
        ('PercentReductionRule', RULE_MAP['PercentReductionRule'].description),
        # ('SimpleFreeShipRule', RULE_MAP['SimpleFreeShipRule'].description),
        ('FreeShipPerAmountRule', RULE_MAP['FreeShipPerAmountRule'].description),
        # ('FreeShipPerAmountBySupplierRule', RULE_MAP['FreeShipPerAmountBySupplierRule'].description),
    )
    rule = models.CharField("计算规则", max_length=50, default='SimpleReductionRule',
                            choices=RULE_TYPES, null=False, blank=False)
    setting = models.TextField("配置", max_length=1000, default='{}', null=False, blank=False,
                               help_text='Json格式，形如{"reduction":"10", "comment":"优惠说明"}，'
                                         '包含对应的规则需要使用的配置信息(如reduction, comment等)')
    effective_date = models.DateTimeField('生效时间', blank=True, null=True,
                                          help_text='同等优先级时，生效时间早的先应用')
    expire_date = models.DateTimeField('失效时间', blank=True, null=True)
    allow_overlap = models.BooleanField('可叠加', default=False, blank=False, null=False,
                                        help_text='可叠加规则是指该规则生效后，其它后续计算的规则仍可适用。'
                                                  '如果不可叠加，一个规则生效后后续所有规则都将失效。')
    priority = models.PositiveIntegerField('优先级', default=0, null=False, blank=False, db_index=True,
                                           help_text='优先级高的先应用，同样优先级，生效早的先应用')
    # 以下字段信息用于排序、筛选及安全审计
    create_time = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True, editable=False)
    create_by = models.IntegerField('创建人', blank=True, null=True, editable=False)
    update_time = models.DateTimeField('更新时间', auto_now=True, blank=True, null=True, editable=False)
    update_by = models.IntegerField('更新人', blank=True, null=True, editable=False)

    def __unicode__(self):
        return self.name

    def clean(self):
        rule = RULE_MAP.get(self.rule)
        if not rule:
            raise ValidationError('未设置有效的优惠规则')

        try:
            rule(self)
        except ValueError, e:
            raise ValidationError(e.message or e.args[1])

        super(ComputationRule, self).clean()

    @property
    def is_store_specific(self):
        return 'stores' in self.setting

    @property
    def is_supplier_specific(self):
        return 'suppliers' in self.setting

    @property
    def is_product_specific(self):
        return 'products' in self.setting

    @staticmethod
    def get_effective_rules():
        """
        获取当前有效的优惠规则列表
        :return:
        """
        cache_key = "tms-config-couponrules"
        cached_val = cache.get(cache_key)
        if cached_val:
            return cached_val
        else:
            cur_time = timezone.now() if settings.USE_TZ else datetime.datetime.now()
            q_condition = Q(expire_date__isnull=True) | Q(expire_date__gt=cur_time)
            cs = ComputationRule.objects.filter(q_condition, effective_date__lt=cur_time)
            results = []
            for s in cs:
                if s.rule in RULE_MAP:
                    rule = RULE_MAP[s.rule](s)
                    rule.allow_overlap = s.allow_overlap
                    results.append(rule)
            cache.set(cache_key, results)
            return results

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        cache_key = "tms-config-couponrules"
        cache.delete(cache_key)
        super(ComputationRule, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        ordering = ['-priority', '-effective_date']
        verbose_name_plural = verbose_name = '优惠/计费计算规则'


def _activity_code():
    return "A-%s-%s" % (day_str(), random_letter(3))


class CouponRule(models.Model):
    code = models.CharField(u"活动编码", max_length=12, default=_activity_code, primary_key=True,
                            help_text=u'用于引用')
    name = models.CharField(u"优惠活动名称", max_length=50, blank=False, null=False,
                            help_text=u"比如：满100减10元")
    link_page = models.CharField('活动专题页url', max_length=512, blank=True, null=True,
                                 help_text='仅当存在外部专题页面时使用')
    description = UEditorField(u"规则说明", max_length=5000, blank=False, null=False)
    coupon_image = models.ForeignKey('filemgmt.BaseImage', verbose_name=u'优惠券图片', related_name='coupon_image+',
                                     null=True, blank=True)
    format = models.CharField(u"优惠券编码格式(编码最长18位)", max_length=64, default="",
                              blank=True, null=True,
                              help_text=mark_safe('如"abcd-{digit-3}", 生成类似"abcd-666"的优惠码，可用如下几种变量：<br>'
                                                  '{year}{month}{day}{hour}{minute}{second}{char-X}{digit-X}{letter-X}",<br>'
                                                  '分别表示用年、月、日、时、分、秒、字符（含数字和字母）、数字、字母。<br>'
                                                  'X表示包含几个字母或数字。留空表示由系统自动编码，带校验功能'))
    # 订单金额限制=0 表示没有限制
    threshold = models.PositiveIntegerField(u"购物金额限制(元)", default=0, null=True, blank=True,
                                            help_text=u'订单最小购物金额限制(元)，0表示不限')
    applied_to_suppliers = models.CharField(u'适用供应商列表', default='', max_length=500, null=True, blank=True,
                                            help_text=u'填写供应商编码，多个供应商用英文逗号分隔，留空则不作限制')
    applied_to_products = models.CharField(u'适用商品列表', default='', max_length=500, null=True, blank=True,
                                           help_text=u'填写商品编号，多个商品用英文逗号分隔，留空则不作限制')
    applied_to_stores = models.CharField(u'适用店铺列表', default='', max_length=500, null=True, blank=True,
                                         help_text=u'填写店铺编号，多个店铺用英文逗号分隔，留空则不作限制')
    applied_to_first_order = models.BooleanField(u'仅限用于首单', default=False,
                                                 help_text=u'仅当用户未下过单时使用（不含已取消的订单）')
    discount = models.PositiveIntegerField(u"优惠金额(元)", default=0, null=True, blank=True)
    repeatable = models.BooleanField(u"允许多张", default=False,
                                     help_text=u"同一订单是否允许使用多张优惠券")
    # 是否允许一张订单和其他优惠策略叠加使用
    allow_addon = models.BooleanField(u"允许叠加", default=False,
                                      help_text=u'是否允许与其他购物优惠规则（非优惠券）叠加使用')
    pub_number = models.PositiveIntegerField(u"优惠券发行数量", default=100, null=True, blank=True)
    tickets_onetime = models.PositiveSmallIntegerField(u"每次可领券数量", default=1, null=True, blank=True,
                                                       help_text=u'默认用户每次可以领取同类优惠券的数量，最小为1')
    most_tickets = models.PositiveSmallIntegerField(u"最多可领券数量", default=10, null=True, blank=True,
                                                    help_text=u'默认用户最多可以领取同类优惠券的数量，默认为10')
    start_time = models.DateTimeField(u'有效期开始时间', auto_now=False, blank=True, null=True, editable=True)
    end_time = models.DateTimeField(u'有效期结束时间', auto_now=False, blank=True, null=True, editable=True)
    allow_dynamic = models.BooleanField('允许动态有效期', default=False,
                                        help_text='如果允许，则优惠券的有效期从用户领取时开始算起，'
                                                  '自动顺延指定的有效天数')
    dynamic_days = models.PositiveSmallIntegerField('动态有效期（天）', default=30,
                                                    help_text='自用户领券开始，优惠券在x天内有效，'
                                                              '即便该时间超过有效期结束时间')
    is_active = models.BooleanField(u"是否有效", default=False)
    create_time = models.DateTimeField(u'创建时间', auto_now=True, blank=True, null=True, editable=False)
    create_by = models.CharField(u'创建人', max_length=32, blank=True, null=True, editable=False)
    update_time = models.DateTimeField(u'更新时间', auto_now=True, blank=True, null=True, editable=False)
    update_by = models.CharField(u'更新人', max_length=32, blank=True, null=True, editable=False)

    def get_expiry(self, get_time=None):
        get_time = get_time or now(settings.USE_TZ)
        if self.allow_dynamic:
            expiry_date = get_time + datetime.timedelta(days=self.dynamic_days)
        else:
            expiry_date = self.end_time
        return expiry_date

    def clean(self):
        err = {}
        if self.is_active:
            if not self.start_time:
                err['start_time'] = '请设置生效的开始时间！'
            if not self.end_time:
                err['end_time'] = '请设置生效的结束时间！'
            if self.discount <= 0:
                err['discount'] = '优惠金额必须大于0!'
            if self.pub_number <= 0:
                err['pub_number'] = '优惠券数量必须大于0！'
            # if not self.coupon_image:
            #     err['coupon_image'] = u'必须提供优惠券图片！'

        if self.tickets_onetime > self.most_tickets:
            err['tickets_onetime'] = '每次可领券数量不得超过最多可领取数量！'

        if self.applied_to_products and self.applied_to_suppliers:
            err['applied_to_suppliers'] = u'指定供应商/商品只能二者选其一填写！'

        if self.allow_dynamic and not self.dynamic_days > 0:
            err['dynamic_days'] = '动态有效期（天）必须大于0'

        if len(err) > 0:
            raise ValidationError(err)

    def to_dict(self):
        """
        返回dict格式CouponRule对象，加上可用及已用优惠券数量
        """
        res = model_to_dict(self)
        res['image'] = self.coupon_image.large if self.coupon_image_id else ''
        res['tickets_claimed'] = self.tickets.filter(consumer__isnull=False).count()
        res['tickets_available'] = self.pub_number - res['tickets_claimed']
        return res

    def simple(self):
        res = model_to_dict(self, exclude=['description', 'format', 'coupon_image',])
        res['image'] = self.coupon_image.large if self.coupon_image_id else ''
        return res

    # # TODO: should be in a transaction
    # def fetch_tickets(self, consumer=None, size=1):
    #     tickets = self.generate(size=size, consumer=consumer)
    #     return tickets
        # tickets = self.tickets.filter(consumer__isnull=True)
        # # 数量不足，需要创建新的优惠券
        # if tickets.count() < size:
        #     delta = size - len(tickets)
        #     tickets_cnt = self.tickets.all().count()
        #     if tickets_cnt < self.pub_number:
        #         if tickets_cnt + delta > self.pub_number:
        #             raise ValueError(u'优惠券数量不足，差额%s' % (tickets_cnt + delta - self.pub_number))
        #         else:
        #             from config.models import AppSetting
        #             batch_size = AppSetting.get('app.promote.coupon_batch_size', 100)
        #             max_size = self.pub_number - tickets_cnt  # 按券发行量定上限，预生成后量不能超出发行量
        #             max_size = max_size if max_size < batch_size else batch_size
        #             delta = delta if delta > max_size else max_size  # 哪个大用哪个，预生成多余的券
        #             self.generate(size=delta)
        #             tickets = self.tickets.filter(consumer__isnull=True)
        #
        # tickets = tickets[:size]
        # if consumer is not None:
        #     # 如果提供了领用人，则需先更新领用人再重新查询获取领用的优惠券列表
        #     get_time = now(settings.USE_TZ)
        #     ticket_codes = [t.code for t in tickets]
        #     tickets_qs = self.tickets.filter(code__in=ticket_codes)
        #     expiry_date = self.get_expiry(get_time)
        #     tickets_qs.update(consumer=consumer,
        #                       get_time=get_time,
        #                       expiry_date=expiry_date)
        #     tickets = self.tickets.filter(code__in=ticket_codes)
        # return [t.to_dict() for t in tickets]

    def fetch_coupons(self, consumer, size=0):
        """
        取指定活动相关的指定数量的优惠券
        """
        if not self.is_active:
            raise ValueError(u'活动[%s]已失效' % self.code)
        cur_time = now(settings.USE_TZ)
        if cur_time < self.start_time:
            raise ValueError(u"活动[%s]尚未开始" % self.code)
        elif cur_time > self.end_time:
            raise ValueError(u"活动[%s]已过期" % self.code)
        size = size or self.tickets_onetime
        size = int(size)
        exists = self.tickets.count()
        if exists + size > self.pub_number:
            raise ValueError('您来晚啦，优惠券已被领完')
        # return cr.fetch_tickets(consumer, int(size))
        return self.generate(size=size, consumer=consumer)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.tickets.count() > self.pub_number > 0:
            raise ValueError(u'当前已有%s张优惠券，如需减少请直接删除【未使用】的优惠券！')
        if self.applied_to_products:
            self.applied_to_products = self.applied_to_products.replace('，', ',')
        if self.applied_to_suppliers:
            self.applied_to_suppliers = self.applied_to_suppliers.replace('，', ',')
        if self.applied_to_stores:
            self.applied_to_stores = self.applied_to_stores.replace('，', ',')

        super(CouponRule, self).save(force_insert, force_update, using, update_fields)
        # if self.is_active:
        #     self.tickets.filter(Q(expiry_date__isnull=True) | Q(expiry_date__lt=self.end_time),
        #                         consume_time__isnull=True).update(expiry_date=self.end_time)

    def generate_all(self):
        size = self.tickets.all().count()
        size_to_generate = self.pub_number - size
        if size_to_generate > 0:
            self.generate(size_to_generate)
        return size_to_generate

    def generate(self, size, consumer=None):
        size = size or self.tickets_onetime or 1
        if self.most_tickets > 0 and consumer:
            tickets_owned = CouponTicket.objects.filter(rule_id=self.code, consumer=consumer).count()
            if self.most_tickets <= tickets_owned:
                raise ValueError('[%s]优惠券每人限领%s张' % (self.name, self.most_tickets))
            else:
                size = min(size, self.most_tickets - tickets_owned)
        tickets = []
        prefix = renderutil.get_dts()
        get_time = now(settings.USE_TZ) if consumer else None  # 自动设置默认领用时间
        expiry_date = self.get_expiry(get_time) if get_time else None
        # TODO: 需要调整写法以避免优惠券数量过多时把内存消耗光
        for i in xrange(size):
            s = "%s%s" % (prefix, renderutil.random_code(12))
            c = hashlib.sha1(s + 'shuiyaopojieyouhuiquan').hexdigest()[-1]
            # 使用已有字符串加一段盐做sha1摘要，取最后一位字符作为校验码加到优惠券码中
            tickets.append(CouponTicket(rule=self,
                                        consumer=consumer,
                                        get_time=get_time,
                                        expiry_date=expiry_date,
                                        code="%s%s" % (s, c.upper())))
        CouponTicket.objects.bulk_create(tickets)
        return [t.to_dict() for t in tickets]

    # 批量生成优惠券的函数
    def generate_per_pattern(self, size, consumer=None):
        pattern = re.compile(r"\{(digit-\d+|char-\d+|letter-\d+)\}")
        code_format = self.format
        placeholders = pattern.findall(code_format)
        if not placeholders:
            raise ValueError(u"无效的优惠券编码格式，无法生成多个优惠码")

        codes = []
        cur_time = now(settings.USE_TZ)
        default_values = {"year": cur_time.year % 100,
                          "month": cur_time.month,
                          "day": cur_time.day,
                          "hour": cur_time.hour,
                          "minute": cur_time.minute,
                          "second": cur_time.second}
        for k, v in default_values.items():
            code_format = code_format.replace("{%s}" % k, str(v))

        for i in xrange(0, size):
            code = code_format
            for ph in placeholders:
                kv = ph.split('-')
                if kv[0] == "digit":
                    code = code.replace("{%s}" % ph, renderutil.random_num(int(kv[1])))
                elif kv[0] == "char":
                    code = code.replace("{%s}" % ph, renderutil.random_code(int(kv[1])))
                elif kv[0] == "letter":
                    code = code.replace("{%s}" % ph, renderutil.random_letter(int(kv[1])))
            codes.append(code)

        tickets = []
        get_time = now(settings.USE_TZ) if consumer else None  # 自动设置默认领用时间
        expiry_date = self.get_expiry(get_time) if get_time else None
        for code in codes:
            tickets.append(CouponTicket(rule=self,
                                        consumer=consumer,
                                        get_time=get_time,
                                        expiry_date=expiry_date,
                                        code=code))
        CouponTicket.objects.bulk_create(tickets)
        return [t.to_dict() for t in tickets]

    def __unicode__(self):
        return "[%s]%s" % (self.code, self.name)

    class Meta:
        verbose_name_plural = verbose_name = '优惠活动'


# def prepare_tickets(sender, instance, created, **kwargs):
#     # 如果是数量比设定的少，则批量生成优惠券
#     if instance.is_active:
#         ticket_cnt = instance.tickets.count()
#         if ticket_cnt < instance.pub_number > 0:
#             from config.models import AppSetting
#             size = instance.pub_number - ticket_cnt
#             batch_size = AppSetting.get('app.promote.coupon_batch_size', 100)
#             size = size if size < batch_size else batch_size
#             if not instance.format:
#                 instance.generate(size=size)
#             else:
#                 instance.generate_coupon(size)
#
#
# signals.post_save.connect(receiver=prepare_tickets, sender=CouponRule)


# def create_token(size=32):
#     """
#     生成默认令牌，32位
#     :return:
#     """
#     return renderutil.random_str(size)


class CouponTicket(models.Model):
    # STATE_NOT_CLAIMED = 0
    # STATE_CLAIMED = 1
    # STATE_CONSUMED = 2
    # COUPON_STATES = (
    #     (0, '未领取'),
    #     (1, '已领取'),
    #     (2, '已消费'),
    # )
    rule = models.ForeignKey(CouponRule, verbose_name='优惠活动', null=False, blank=False,
                             related_name='tickets', on_delete=models.PROTECT)
    code = models.CharField("优惠券号码", max_length=18, blank=False, null=False, unique=True)
    get_time = models.DateTimeField('领取时间', auto_now=False, blank=True, null=True, db_index=True)
    dispatcher = models.CharField('分发人UID', max_length=32, blank=True, null=True,
                                  help_text='备用，用于特殊角色，即获取优惠券，提供给他人使用的用户')
    consumer = models.CharField('领用人UID', max_length=32, blank=True, null=True,
                                help_text='即最终该优惠券的使用人')
    consume_time = models.DateTimeField('消费时间', auto_now=False, blank=True, null=True)
    expiry_date = models.DateTimeField(u'过期时间', auto_now=False, blank=True, null=True,
                                       help_text='对于支持动态过期时间的优惠券，过期时间以此为准')
    order_no = models.CharField('消费订单号', max_length=20, blank=True, null=True)
    # status = models.PositiveIntegerField("状态", default=0, choices=COUPON_STATES)
    # 冗余字段，如果为False，还需通过rule的过期时间判断
    is_expired = models.BooleanField('是否过期', default=False)

    def to_dict(self):
        """
        返回dict机构优惠券信息，包含优惠券规则的简要信息
        :return:
        """
        res = model_to_dict(self)
        res['rule'] = self.rule.simple()
        return res

    def is_valid(self):
        """
        检查优惠券是否有效
        :return:
            有效返回True，否则返回无效的文字说明
        """
        if self.is_expired:
            return u"优惠券已过期"
        elif self.order_no:
            return u'优惠券已使用'

        cur_time = now(settings.USE_TZ)
        if self.expiry_date and self.expiry_date < cur_time:
            return u"优惠券已过期"
        elif cur_time < self.rule.start_time:
            return u"优惠券尚未生效"
        elif cur_time > self.rule.end_time and not self.rule.allow_dynamic:
            return u"优惠券已过期"
        elif not self.rule.is_active:
            return u"优惠活动已失效或暂停"
        else:
            return True

    @staticmethod
    def is_valid_coupon(code):
        """
        检查指定编码的优惠券是否有效
        :return:
            有效返回True，否则返回无效的文字说明
        """
        try:
            ticket = CouponTicket.objects.get(code=code)
            return ticket.is_valid()
        except CouponTicket.DoesNotExist:
            return u'无效的优惠券'

    def is_applicable_to_product(self, product=None, pcs=1):
        """
        检查当前优惠券是否适用于指定商品
        :param product:
        :param pcs:
        :return:
            是返回True
            否则返回不适用的原因描述
        """

        if product is None or pcs < 1:
            return u'商品信息(%s * %s)无效！' % (product, pcs)
        if product['is_special']:
            return u'特价商品[%s]不参与其它优惠活动！' % product
        if self.rule.applied_to_products:
            if product['code'] not in self.rule.applied_to_products.split(','):
                return u'不适用于商品[%s]' % product['name']
            # elif self.rule.threshold > 0 and product.retail_price * pcs < self.rule.threshold:
            #     return u'未达到使用最低限额￥%s' % self.rule.threshold
        elif self.rule.applied_to_suppliers:
            if product['supplier']['code'] not in self.rule.applied_to_suppliers.split(','):
                return u'不适用于供应商[%s]' % product['supplier']['name']
            # elif self.rule.threshold > 0 and product.retail_price * pcs < self.rule.threshold:
            #     return u'未达到使用最低限额￥%s' % self.rule.threshold

        shop_amount = product['retail_price'] * pcs
        if self.rule.threshold > 0 and shop_amount < self.rule.threshold:
            return u'未达到优惠最低限额条件￥%s（再凑￥%s就可以啦）' \
                   % (self.rule.threshold, (self.rule.threshold - shop_amount))

        return True

    def is_applicable_to_products(self, shop_data):
        """
        使用订单或商品及数量信息及用户信息进行匹配检查，判断优惠券是否可用
        可用返回True，不可用返回错误消息提示
        - order, 用于验证能否使用优惠券的订单对象，不检查订单状态
        - user， 用于验证能否使用优惠券的订单
        :return:
            是返回True
            否则返回不适用的原因描述
        """
        if not shop_data:
            return "无适用的商品"
        if self.rule.applied_to_products:
            shop_amount = 0
            product_codes = self.rule.applied_to_products.split(',')
            for item in shop_data:
                if not item['product']['is_special'] and item['product']['code'] in product_codes:
                    shop_amount += item['product']['retail_price'] * item['pcs']
            if shop_amount == 0:
                return '无适用的商品'
            else:
                if shop_amount < self.rule.threshold > 0:
                    return u'再凑单￥%s就能使用优惠券啦(注：特价商品不参与活动)' % (self.rule.threshold - shop_amount)

        elif self.rule.applied_to_suppliers:
            shop_amount = 0
            supplier_codes = self.rule.applied_to_suppliers.split(',')
            for item in shop_data:
                if not item['product']['is_special'] and item['product']['supplier']['code'] in supplier_codes:
                    shop_amount += item['product']['retail_price'] * item['pcs']

            if shop_amount == 0:
                return '无适用的商品'
            else:
                if shop_amount < self.rule.threshold > 0:
                    return u'再凑单￥%s就能使用优惠券啦(注：特价商品不参与活动)' % (self.rule.threshold - shop_amount)

        else:
            shop_amount = 0
            for item in shop_data:
                if not item['product']['is_special']:
                    shop_amount += item['product']['retail_price'] * item['pcs']
            if shop_amount == 0:
                return '无适用的商品'
            else:
                if shop_amount < self.rule.threshold > 0:
                    return u'再凑单￥%s就能使用优惠券啦(注：特价商品不参与活动)' % (self.rule.threshold - shop_amount)

        return True

    def is_applicable_to_order(self, order=None):
        """
        使用订单或商品及数量信息及用户信息进行匹配检查，判断优惠券是否可用
        可用返回True，不可用返回错误消息提示
        - order, 用于验证能否使用优惠券的订单，不检查订单状态
        - user， 用于验证能否使用优惠券的订单
        """
        if not order:
            return u'订单无效'

        if not isinstance(order, dict):
            order = order.to_dict()

        return self.is_applicable_to_order_obj(order)

    def is_applicable_to_order_obj(self, order):
        """
        使用订单或商品及数量信息及用户信息进行匹配检查，判断优惠券是否可用
        可用返回True，不可用返回错误消息提示
        - order, 用于验证能否使用优惠券的订单对象，不检查订单状态
        - user， 用于验证能否使用优惠券的订单
        """
        if not order:
            return u'订单无效'

        if not self.rule.repeatable:
            if order['order_no']:
                if CouponTicket.objects.filter(order_no=order['order_no']).exists():
                    return "同一订单只能使用一张优惠券"
            else:
                for disc in order['discounts']:
                    if disc['rel_type'] == 'coupon':
                        return "同一订单只能使用一张优惠券"
        if order['shop_amount_off'] > 0 and not self.rule.allow_addon:
            for disc in order['discounts']:
                if disc['rel_type'] == 'rule':
                    return "该优惠券不能叠加其它优惠共同使用"

        if self.rule.applied_to_products:
            for item in order['items']:
                if self.is_applicable_to_product(item['product'], item['pcs']):
                    return True
            return u"无适用的商品"

        if self.rule.applied_to_suppliers:
            shop_amount = 0
            supplier_codes = self.rule.applied_to_suppliers.split(',')
            for item in order['items']:
                if not item['product']['is_special'] and item['product']['supplier']['code'] in supplier_codes:
                    shop_amount += item['deal_price'] * item['pcs']

            if shop_amount == 0:
                return u'无适用的商品'
            else:
                if shop_amount < self.rule.threshold > 0:
                    return u'再凑单￥%s就能使用优惠券啦(注：特价商品不参与活动)' % (self.rule.threshold - shop_amount)

        if self.rule.threshold > 0:
            shop_amount = 0
            for item in order['items']:
                if not item['product']['is_special']:
                    shop_amount += item['deal_price'] * item['pcs']
            if shop_amount < self.rule.threshold:
                return u"再凑单￥%s就能使用优惠券啦(注：特价商品不参与活动)" % self.rule.threshold - shop_amount

        return True

    def apply_to(self, order):
        """
        应用于指定订单，调用该接口会先检查优惠券是否可用
        :param order:
        :return:
        """
        if not isinstance(order, dict):
            order = order.to_dict()

        is_applicable = self.is_applicable_to_order(order)
        if is_applicable is not True:
            raise ValueError(is_applicable)

        self.order_no = order['order_no']
        self.consume_time = now(settings.USE_TZ)
        # self.status = CouponTicket.STATE_CONSUMED
        self.save()

    def __unicode__(self):
        return self.code

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.consumer is not None:
            # if self.status == CouponTicket.STATE_NOT_CLAIMED:
            #     self.status = CouponTicket.STATE_CLAIMED
            self.get_time = self.get_time or now(settings.USE_TZ)  # 自动设置默认领用时间
        if self.consumer and self.order_no:
            # self.status = CouponTicket.STATE_CONSUMED
            self.consume_time = self.consume_time or now(settings.USE_TZ)  # 自动设置消费时间
        super(CouponTicket, self).save(force_insert=force_insert, force_update=force_update,
                                       using=using, update_fields=update_fields)

    class Meta:
        ordering = ['-get_time']
        verbose_name_plural = verbose_name = '优惠活动 - 优惠券'


def _set_code():
    return "S%s%s" % (day_str(), random_letter(3))


class CouponRuleSet(models.Model):
    code = models.CharField(u"组合编码", max_length=32, primary_key=True, null=False, blank=True,
                            help_text=u'用于引用，如果不填写则由系统自动生成。注意：填写后将不能再修改！')
    name = models.CharField(u"组合名称", max_length=50, blank=False, null=False,
                            help_text=u"比如：满100减10元")
    link_page = models.CharField('组合专题页url', max_length=512, blank=True, null=True,
                                 help_text='仅当存在外部专题页面时使用')
    image = models.ForeignKey('filemgmt.BaseImage', verbose_name=u'套餐图片', related_name='+',
                              null=True, blank=True)
    description = UEditorField(u"组合介绍", max_length=5000, blank=True, null=True)
    start_time = models.DateTimeField(u'有效期开始时间', default=datetime.datetime.now, blank=True, null=True, editable=True)
    end_time = models.DateTimeField(u'有效期结束时间', auto_now=False, blank=True, null=True, editable=True)
    create_time = models.DateTimeField(u'创建时间', auto_now=True, blank=True, null=True, editable=False)
    create_by = models.CharField(u'创建人', max_length=32, blank=True, null=True, editable=False)
    update_time = models.DateTimeField(u'更新时间', auto_now=True, blank=True, null=True, editable=False)
    update_by = models.CharField(u'更新人', max_length=32, blank=True, null=True, editable=False)

    def to_dict(self):
        res = {'code': self.code,
               'name': self.name,
               'link_page': self.link_page,
               'image': self.image.large if self.image else '',
               'description': self.description,
               'start_time': self.start_time,
               'end_time': self.end_time}
        rule_items = self.rules.all()
        rules = []
        for item in rule_items:
            rule = item.rule.to_dict()
            rule['list_order'] = item.list_order
            rule['number'] = item.number
            rules.append(rule)
        res['rules'] = rules
        return res

    def __unicode__(self):
        return "[%s]%s" % (self.code, self.name)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.code = self.code or _set_code()
        self.link_page = self.link_page or ("http://itravelbuy.twohou.com/guest/getcoupons/%s" % self.code)
        super(CouponRuleSet, self).save(force_insert=force_insert, force_update=force_update,
                                        using=using, update_fields=update_fields)

    class Meta:
        ordering = ['-pk']
        verbose_name_plural = verbose_name = '优惠活动组合(领券用)'


class RuleSetMap(models.Model):
    rule_set = models.ForeignKey(CouponRuleSet, verbose_name='组合',  related_name='rules', on_delete=models.CASCADE,
                                 null=False, blank=False)
    rule = models.ForeignKey(CouponRule, verbose_name='优惠活动', related_name='rulesets', on_delete=models.PROTECT,
                             null=False, blank=False)
    number = models.PositiveSmallIntegerField('优惠券数量', default=1, null=False, blank=False)
    list_order = models.PositiveIntegerField('排序标记', default=0, help_text='数值越大，排序越靠前')

    def __unicode__(self):
        return "%s:%s*%s" % (self.rule_set.name, self.rule.name, self.number)

    def clean(self):
        if self.number > self.rule.tickets_onetime:
            raise ValidationError({'number': '活动组合中优惠券可领数量(%s)超过活动限制(%s)' % (self.number, self.rule.tickets_onetime)})

    class Meta:
        ordering = ['-list_order']
        verbose_name_plural = verbose_name = '组合活动关系表'


class RewardRecord(models.Model):
    REWARD_TBD = 0  # 待结算
    REWARD_ACHIEVED = 1  # 已结算
    REWARD_REVOKED = 2  # 已取消，即订单已取消或退款
    REWARD_STATUS = (
        (REWARD_TBD, u'待结算'),
        (REWARD_ACHIEVED, u'已结算'),
        (REWARD_REVOKED, u'已取消')
    )
    TYPE_REWARD = 0
    TYPE_PARTNER_REWARD = 1
    TYPE_REWARD_OVERHEAD = 2
    TYPE_FORWARD_REWARD = 3
    REWARD_TYPES = (
        (0, u'销售回佣'),
        (1, u'伙伴销售奖励'),
        (2, u'企业管理费用'),
        (3, u'转发推广回佣'),
    )
    referrer_id = models.CharField(u'推广用户UID', max_length=32, null=False, blank=False, db_index=True)
    activity_code = models.CharField(u'活动代码', max_length=32, null=True, blank=True,
                                     help_text=u'用于特定场景下产生的订单，比如导游行程中产生的订单（代码为行程单号）')
    order_no = models.CharField(u'推广订单号', max_length=20,
                                blank=False, null=False)
    reward = models.DecimalField(u'预期收益', max_digits=10, decimal_places=2, default=0,
                                 blank=False, null=False,
                                 help_text=u"为订单结算完成前可预期收益")
    reward_type = models.PositiveSmallIntegerField(u'收益类型', default=TYPE_REWARD,
                                                   blank=True, null=True, choices=REWARD_TYPES)
    achieved = models.DecimalField(u'已结算收益', max_digits=10, decimal_places=2, default=0,
                                   blank=False, null=False,
                                   help_text=u"为订单结算完成后实际到账金额")
    achieved_time = models.DateTimeField(u'结算时间', blank=True, null=True)
    account_no = models.CharField(u'流水号', max_length=32, null=True, blank=True,
                                  help_text=u'已结算收益必须有流水号后，才意味着该收益到账')
    memo = models.CharField(u'备注', max_length=32, null=True, blank=True,
                            help_text=u'用于简单说明收益撤销原因')
    status = models.PositiveSmallIntegerField(u'收益状态', default=REWARD_TBD, choices=REWARD_STATUS)
    source_uid = models.CharField(u'收益来源用户UID', max_length=32, null=True, blank=True, db_index=True,
                                  help_text=mark_safe('- 如果是销售回佣，则为买家uid，<br>'
                                                      '- 如果是伙伴销售奖励，则为伙伴uid，<br>'
                                                      '- 如果是企业管理费用，则为下属企业uid'))
    store_code = models.CharField(u'店铺代码', max_length=32, null=True, blank=True, db_index=True,
                                  help_text=u'店铺编码')
    create_time = models.DateTimeField(u'创建时间', blank=True, null=True, default=timezone.now)
    update_time = models.DateTimeField(u'更新时间', blank=True, null=True, auto_now=True)

    @staticmethod
    def summary(referrer_id):
        incomes = RewardRecord.objects.filter(supplier_id=referrer_id).values('status').annotate(
            total_reward=Sum('reward'), total_achieved=Sum('achieved'), reward_cnt=Count('id')
        )
        result = {}
        status_dict = dict(RewardRecord.REWARD_STATUS)
        for i in incomes:
            if i.get('status') == RewardRecord.REWARD_ACHIEVED:
                result[status_dict[i.get('status')]] = {"rewards": i.get('total_achieved'), "cnt": i.get('reward_cnt')}
            else:
                result[status_dict[i.get('status')]] = {"rewards": i.get('total_reward'), "cnt": i.get('reward_cnt')}

        return result

    def revoke(self, memo):
        """
        撤销收益，并说明理由
        :param memo:
        :return:
        """
        if not memo:
            raise ValueError('缺少撤销理由')
        if self.status == RewardRecord.REWARD_REVOKED:
            return False
        self.charge_back()
        self.memo = memo
        self.status = RewardRecord.REWARD_REVOKED
        self.save()
        return True

    def charge_back(self):
        """
        撤销收益对应的流水
        :return:
        """
        from profile.models import UserAccountBook
        if not self.account_no:
            pass
        else:
            account = UserAccountBook.objects.get(account_no=self.account_no)
            account.charge_back()

    def charge(self, frozen_days=7):
        """
        结算收益变成资金流水，默认冻结7天后方可提现
        :param frozen_days:
        :return:
        """
        if self.account_no:
            return False
        elif self.status == RewardRecord.REWARD_ACHIEVED:
            if self.achieved >= 0:
                desc = (u'[%s]伙伴销售奖励' if self.reward_type == self.TYPE_PARTNER_REWARD
                        else u'[%s]订单结算返佣') % self.order_no

                from profile.models import UserAccountBook
                # 收益记录，有一定的冻结时间
                # frozen_days = AppSetting.get('app.reward_deferred_days', 7)
                delta = datetime.timedelta(days=frozen_days)
                book = UserAccountBook.objects.create(
                    uid=self.referrer_id,
                    figure=self.achieved,
                    is_income=True,
                    type='reward',
                    account_desc=desc,
                    extra_type='basedata.Order',
                    extra_data=self.order_no,
                    effective_time=now(settings.USE_TZ) + delta
                )
                self.account_no = book.account_no
                self.save()
                return True
        else:
            raise ValueError(u'当前收益不可入账(id: %s)' % self.pk)

    @staticmethod
    def transfer_reward(uid, rewards):
        from profile.models import EndUser, UserAccountBook
        from basedata.models import Order
        result = {"order_cnt": 0, "reward_cnt": 0, "account_cnt": 0}
        err_msgs = []

        if not EndUser.objects.filter(uid=uid).exists():
            err_msgs.append(u'找不到uid为[%s]的用户' % uid)
        else:
            reward_cnt = account_cnt = order_cnt = 0
            queryset = RewardRecord.objects.filter(pk__in=rewards.split(','))
            for reward in queryset:
                old_uid = reward.referrer_id
                order = account = None
                try:
                    Order.objects.get(order_no=reward.order_no)
                    if reward.account_no:  # 已经入账，也需要转移流水
                        account = UserAccountBook.objects.get(account_no=reward.account_no)
                except Order.DoesNotExist:
                    err_msgs.append(u"找不到订单：%s" % reward.order_no)
                    continue
                except UserAccountBook.DoesNotExist:
                    err_msgs.append(u"找不到资金记录：%s" % reward.account_no)
                    continue

                # memo_msg = reward.memo
                # memo_time = datetime.datetime.now()
                # memo_msg.append(u"时间: %s, 订单收益转移给: %s; " % memo_time.strftime('%Y-%m-%d %H:%M:%S'), uid)
                # reward.memo = memo_msg

                reward.referrer_id = uid
                reward.save()
                logger.warn(u'转移收益[%s]从%s到%s' % (reward.pk, old_uid, uid))
                reward_cnt += 1
                row = Order.objects.filter(order_no=reward.order_no).update(referrer_id=uid)  # 更新订单的推荐信息
                if row == 1:
                    order_cnt += 1
                else:
                    err_msgs.append(u'找不到订单：%s' % reward.order_no)
                logger.warn(u'订单[%s]推广人从%s变成%s' % (reward.order_no, old_uid, uid))
                if account:
                    account.uid = uid
                    account.save()
                    account_cnt += 1
                    logger.warn(u'转移资金流水[%s]从%s到%s' % (account.pk, old_uid, uid))

            result['reward_cnt'] = reward_cnt
            result['account_cnt'] = account_cnt
            result['order_cnt'] = order_cnt
        result['errors'] = err_msgs
        return result

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.achieved > 0 and not self.achieved_time:
            self.achieved_time = renderutil.now(settings.USE_TZ)
        # if self.status == RewardRecord.REWARD_ACHIEVED and not self.account_no:
        #     raise ValueError(u'已结算订单[%s]收益应提供流水号' % self.order_no)
        super(RewardRecord, self).save(force_insert, force_update, using, update_fields)

        if self.status == RewardRecord.REWARD_REVOKED and self.account_no:
            self.charge_back()

    def __unicode__(self):
        return u"[%s]预期收益(%s)/实际到账(%s)" % (self.order_no, self.reward, self.achieved)

    class Meta:
        unique_together = ['order_no', 'referrer_id', 'activity_code', ]
        ordering = ['-create_time']
        verbose_name_plural = verbose_name = u'用户推广收益记录'
