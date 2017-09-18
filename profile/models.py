# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import cgi
import uuid
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.db.models import Sum

from tms import settings
from tms.config import PROVINCES, REWARD_DEFERRED_DAYS
from util.renderutil import day_str, random_letter, now
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from config.models import AppSetting


class UserFavorite(models.Model):
    uid = models.CharField(u'用户UID', max_length=32, null=False, blank=False, db_index=True)
    ENTITY_TYPES = (
        ('P', u'商品'),
    )
    FAVOR_TYPES = (
        (0, u'收藏'),
    )
    favor_type = models.PositiveIntegerField(u'关注类型', default=0, choices=FAVOR_TYPES)
    # 关注对象类型
    entity_type = models.CharField(u'关注对象类型', max_length=2, choices=ENTITY_TYPES)
    entity_id = models.IntegerField(u'关注对象ID')  # 关联实体模型对应的id
    create_time = models.DateTimeField(u'关注时间', auto_now_add=True)

    def __unicode__(self):
        return u"关注对象：%s-%s" % (self.entity_type, self.entity_id)

    class Meta:
        ordering = ('-create_time',)
        verbose_name_plural = verbose_name = u'用户关注列表'


class UserHistory(models.Model):
    # 0 指匿名用户
    uid = models.CharField(u'用户UID', max_length=32, null=False, blank=False, db_index=True)
    ENTITY_TYPES = (
        ('P', u'商品'),
        ('KW', u'搜索'),
        ('A', u'文章'),
    )
    entity_type = models.CharField(u'访问对象类型', max_length=2, choices=ENTITY_TYPES)
    entity_id = models.IntegerField(u'访问对象ID', default=0, null=True, blank=True)  # 关联实体模型对应的id
    entity_value = models.CharField(u'访问对象值', max_length=20, null=True, blank=True,
                                    help_text=u'主要用于保存用户搜索的关键词历史')
    update_time = models.DateTimeField(u'访问时间', auto_now_add=True)

    def __unicode__(self):
        return u"访问历史(%s-%s-%s)" % (self.id, self.entity_type,
                                        self.entity_value if 'KW' == self.entity_type else self.entity_id)

    @staticmethod
    def log(uid, entity_type='KW', entity_value=None):
        cur_time = now(settings.USE_TZ)
        UserHistory.objects.update_or_create(uid=uid,
                                             entity_type=entity_type,
                                             entity_value=cgi.escape(entity_value),
                                             defaults={'update_time': cur_time})

    class Meta:
        ordering = ('-update_time',)
        verbose_name_plural = verbose_name = u'用户访问历史'


def _uuid():
    return uuid.uuid4().hex


class EndUser(models.Model):
    GENDER_TYPES = (
        ('M', u'男'),
        ('F', u'女'),
        ('X', u'不告诉你'),
    )
    STATUS_ACTIVE = 0
    STATUS_INACTIVE = 1
    STATUS_BANNED = 99
    USER_STATUS = (
        (STATUS_ACTIVE, u'有效'),
        (STATUS_INACTIVE, u'无效'),
        (STATUS_BANNED, u'黑名单'),
    )
    USER_PERSON = 'P'   # 个人
    USER_ENTERPRISE = 'E'   # 企业
    USER_GROUP = 'G'    # 集团企业
    USER_TYPES = (
        (USER_PERSON, '普通用户'),
        (USER_ENTERPRISE, '企业用户'),
        (USER_GROUP, '集团企业'),
    )
    uid = models.CharField(u'用户ID', max_length=32, default=_uuid, null=False, blank=False, primary_key=True)
    mobile = models.CharField(u'手机', max_length=15, null=True, blank=True)
    nick_name = models.CharField(u'昵称', max_length=30, null=True, blank=True,
                                 help_text=u'用户自定义昵称，优先于第三方昵称设置')
    avatar = models.URLField(u'头像', null=True, blank=True, max_length=255,
                             help_text=u'用户自定义头像，优先于第三方头像设置，对于企业而言就是企业的Logo')
    ex_nick_name = models.CharField(u'昵称（第三方）', max_length=30, null=True, blank=True)
    ex_avatar = models.URLField(u'头像（第三方）', null=True, blank=True, max_length=255,
                                help_text=u'第三方账号的头像，随时根据用户登录时的信息更新')
    password = models.CharField(u'密码', max_length=128, null=True, blank=True, editable=False)  # 暂时保留
    real_name = models.CharField(u'姓名/名称', max_length=30, null=True, blank=True, db_index=True,
                                 help_text=u'备用，网安实名制要求，对于企业账号就是企业名称')
    id_card = models.CharField(u'身份证号', max_length=18, null=True, blank=True,
                               help_text=u'备用，网安实名制要求')
    gender = models.CharField(u'性别', max_length=1, null=False, blank=False, choices=GENDER_TYPES, default='X')
    status = models.SmallIntegerField(u'状态', default=STATUS_ACTIVE, choices=USER_STATUS, null=True, blank=True)
    user_type = models.CharField('用户类型', max_length=10, choices=USER_TYPES,
                                 default=USER_PERSON, null=False, blank=False)
    intro = models.CharField('简介', max_length=1024, null=True, blank=True)
    # TODO: the register_time may be not the real time it registered, but the first time a sms code sent
    register_time = models.DateTimeField(u'注册时间', null=False, blank=True, auto_now_add=True, editable=False)
    update_time = models.DateTimeField(u'更新时间', null=True, blank=True, auto_now=True, editable=False)
    register_ip = models.GenericIPAddressField(u'注册时IP', null=True, blank=True, editable=False)
    last_login = models.DateTimeField(u'上次登录时间', null=True, blank=True)
    entry_uid = models.CharField(u'入口UID', max_length=36, null=True, blank=True, db_index=True,
                                 help_text='即用户首次扫码进入，成为新用户时入口用户的uid')
    referrer = models.CharField(u'推荐人', max_length=36, null=True, blank=True, db_index=True,
                                help_text='用户被推荐成为导游时推荐人的uid')
    org_uid = models.CharField('归属组织UID', max_length=36, null=True, blank=True, db_index=True)
    is_org_staff = models.BooleanField('是否组织管理者', default=False, null=False,
                                       help_text='该设置仅对普通类型用户有效，当设置为是时，需检查用户与组织的关系')

    def to_dict(self):
        return model_to_dict(self, exclude=('password', 'id_card', ))

    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    @property
    def is_banned(self):
        return self.status == self.STATUS_BANNED

    def get_org(self):
        """
        获取所属组织对象
        """
        if not self.org_uid:
            return None
        try:
            org = EndUserEnterprise.objects.get(uid=self.org_uid)
            return org
        except EndUserEnterprise.DoesNotExist:
            return None

    def get_org_per_time(self, before_time=None):
        """
        获取指定时间之前当前用户的归属组织
        """
        if not before_time:
            org = self.get_org()
            return org.to_dict() if org else None
        else:
            try:
                snapshot = UserOrgSnapShot.objects.filter(uid=self.uid, create_time__lte=before_time)\
                    .values_list('org_uid', 'overhead_rate').latest('create_time')
                try:
                    org = EndUserEnterprise.objects.get(uid=snapshot[0])
                    org = org.to_dict()
                    org['overhead_rate'] = snapshot[1]
                    return org
                except EndUserEnterprise.DoesNotExist:
                    return None
            except UserOrgSnapShot.DoesNotExist:
                org = self.get_org()
                return org.to_dict() if org else None

    def __unicode__(self):
        return "%s[%s]: %s" % (self.get_user_type_display(), self.uid, self.nick_name)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.nick_name = self.nick_name or self.ex_nick_name
        super(EndUser, self).save(force_insert=force_insert,
                                  force_update=force_update,
                                  using=using,
                                  update_fields=update_fields)

    class Meta:
        verbose_name_plural = verbose_name = u'终端用户'


class EndUserExt(models.Model):
    ID_TYPE_WECHAT_OPENID = 0
    ID_TYPE_WECHAT_UNIONID = 1
    ID_TYPE_QQ_OPENID = 2
    ID_TYPE_ALIPAY_OPENID = 3
    ID_TYPE_WEIBO_OPENID = 4
    ID_TYPE_BROWSER = 5
    ID_TYPE_INTERNAL = 99

    ID_TYPES = (
        (ID_TYPE_WECHAT_OPENID, u'微信openID'),
        (ID_TYPE_WECHAT_UNIONID, u'微信unionID'),
        (ID_TYPE_QQ_OPENID, u'QQ开放账号ID'),
        (ID_TYPE_ALIPAY_OPENID, u'支付宝开放账号ID'),
        (ID_TYPE_WEIBO_OPENID, u'微博开放账号ID'),
        (ID_TYPE_BROWSER, u'普通浏览器uuid（匿名用户）'),
        (ID_TYPE_INTERNAL, u'交易平台管理账号')
    )
    uid = models.CharField(u'用户UID', max_length=32, null=False, blank=False, db_index=True)
    ex_id_type = models.PositiveSmallIntegerField(u'第三方账号类型', null=False, blank=False,
                                                  choices=ID_TYPES, default=ID_TYPE_WECHAT_OPENID)
    ex_id = models.CharField(u'第三方账号', max_length=32, null=True, blank=True, db_index=True)
    reg_time = models.DateTimeField(u'注册时间', null=False, blank=True, auto_now_add=True, editable=False)

    def __unicode__(self):
        return "%s:%s" % (self.get_ex_id_type_display(), self.ex_id)

    class Meta:
        verbose_name_plural = verbose_name = u'终端用户 - 第三方账号'


class EndUserEnterprise(EndUser):
    """
    企业账号
    """
    REVIEW_PENDING = 'pending'
    REVIEW_PASSED = 'passed'
    REVIEW_REJECTED = 'rejected'
    REVIEW_HOLD = 'hold'
    REVIEW_STATUSES = (
        (REVIEW_PENDING, '待审核'),
        (REVIEW_PASSED, '已通过'),
        (REVIEW_REJECTED, '已拒绝'),
        (REVIEW_HOLD, '暂时搁置'),
    )
    ENTERPRISE_TYPES = (
        (0, '旅行社'),
        (1, '酒店'),
        (2, '民宿'),
        (3, '景区'),
        (999, '其它'),
    )
    ent_type = models.PositiveSmallIntegerField('企业类型', default=0, null=False, blank=False)
    license_image = models.URLField('执照/资质证照', null=True, blank=True, max_length=255,
                                    help_text=u'私密图片，用于企业资质审核')
    id_card_image = models.URLField('责任人身份证照', null=True, blank=True, max_length=255,
                                    help_text=u'私密图片，用于企业负责人身份认证')
    overhead_rate = models.PositiveSmallIntegerField('抽成比例(0-80%)', null=True, blank=True,
                                                     validators=[MaxValueValidator(80), MinValueValidator(0)])
    contact_name = models.CharField('联系人', max_length=30, blank=True, null=True)
    contact_mobile = models.CharField('联系人手机', max_length=13, blank=True, null=True)
    contact_phone = models.CharField('固定电话', max_length=15, blank=True, null=True)
    contact_email = models.EmailField('Email', max_length=60, blank=True, null=True)
    province = models.CharField("所在省/直辖市/自治区", choices=PROVINCES, max_length=10, null=True, blank=True)
    city = models.CharField("所在城市", max_length=10, null=True, blank=True)
    address = models.CharField('地址', max_length=100, blank=True, null=True)
    post_code = models.CharField('邮编', max_length=8, blank=True, null=True)
    lng = models.FloatField('经度', default=0, blank=True, null=True)  #
    lat = models.FloatField('纬度', default=0, blank=True, null=True)
    # 经纬度hash编码，用于快速进行周边搜索
    geo_hash = models.CharField(max_length=16, blank=True, null=True, db_index=True, editable=False)
    review_status = models.CharField('审核状态', max_length=8, choices=REVIEW_STATUSES,
                                     default=REVIEW_PENDING, blank=False, null=False)
    review_note = models.CharField('审核意见', max_length=255, blank=True, null=True)
    reviewed_time = models.DateTimeField('审核时间', null=True, blank=True, editable=False)
    created_by = models.CharField(u'申请人UID', max_length=32, null=True, blank=True)

    unused_fields = ('ex_nick_name', 'ex_avatar', 'password', 'gender', 'id_card', 'nick_name',
                     'entry_uid', 'mobile', )

    def __unicode__(self):
        return "%s[%s]" % (self.get_user_type_display(), self.real_name)

    def clean(self):
        if not self.real_name:
            raise ValidationError({"real_name": '缺少企业名称'})

    def to_dict(self):
        exclude = ['is_org_staff']
        exclude.extend(self.unused_fields)
        result = model_to_dict(self, exclude=exclude)
        result['register_time'] = self.register_time
        result['reviewed_time'] = self.reviewed_time
        return result

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.user_type == EndUserEnterprise.USER_PERSON:  # 默认为普通企业
            self.user_type = EndUserEnterprise.USER_ENTERPRISE
        if self.review_status != EndUserEnterprise.REVIEW_PENDING and self.reviewed_time is None:
            self.reviewed_time = now(settings.USE_TZ)
        if self.overhead_rate is None:
            self.overhead_rate = AppSetting.get('app.group_reward_overhead'
                                                if self.user_type == EndUserEnterprise.USER_GROUP
                                                else 'app.enterprise_reward_overhead')
        super(EndUserEnterprise, self).save(force_insert=force_insert, force_update=force_update,
                                            using=using, update_fields=update_fields)

    class Meta:
        verbose_name_plural = verbose_name = u'企业账号'


class UserOrgSnapShot(models.Model):
    uid = models.CharField(u'用户/组织用户UID', max_length=32, null=False, blank=False, db_index=True)
    org_uid = models.CharField(u'所属组织用户UID', max_length=32, null=False, blank=True, db_index=True)
    overhead_rate = models.PositiveSmallIntegerField('抽成比例(0-100)', null=True, blank=True,
                                                     validators=[MaxValueValidator(80), MinValueValidator(0)])
    create_time = models.DateTimeField(u'创建时间', null=False, blank=True, auto_now_add=True, db_index=True, editable=False)

    def __unicode__(self):
        return "%s@%s" % (self.uid, self.org_uid)

    class Meta:
        verbose_name_plural = verbose_name = u'用户组织关系快照'


class EndUserLink(models.Model):
    LINK_WEIBO = 'weibo'
    LINK_WECHAT = 'wechat'
    LINK_WEBSITE = 'website'
    LINK_TYPES = (
        (LINK_WEIBO, '微博'),
        (LINK_WECHAT, '微信公众号'),
        (LINK_WEBSITE, '网站地址'),
    )

    uid = models.CharField(u'用户UID', max_length=32, null=False, blank=False, db_index=True)
    link = models.CharField('链接地址', max_length=200, blank=True, null=True)
    link_type = models.CharField('链接类型', max_length=10, null=False, blank=False,
                                 choices=LINK_TYPES, default=LINK_WEBSITE,)

    def __unicode__(self):
        return "%s: %s" % (self.get_link_type_display(), self.link)

    class Meta:
        verbose_name_plural = verbose_name = u'用户关联地址'


class EndUserRole(models.Model):
    ROLE_SP = 'sp'
    ROLE_ADMIN = 'admin'
    ROLE_STAFF = 'staff'
    ROLES = (
        (ROLE_SP, '超级管理员'),
        (ROLE_ADMIN, '管理员'),
        (ROLE_STAFF, '职员'),
    )
    user_uid = models.CharField(u'用户UID', max_length=32, null=False, blank=False, db_index=True)
    org_uid = models.CharField(u'企业用户UID', max_length=32, null=False, blank=False, db_index=True)
    role = models.CharField('用户角色', max_length=10, null=False, blank=False,
                            choices=ROLES, default=ROLE_STAFF)

    def __unicode__(self):
        return "%s[%s]" % (self.user_uid, self.get_role_display())

    class Meta:
        verbose_name_plural = verbose_name = u'用户角色'


class TmsUser(models.Model):
    user = models.OneToOneField(User, verbose_name=u'用户', null=False, blank=False, help_text=u'后台管理用户')
    uid = models.CharField(u'用户UID', max_length=32, null=False, blank=False, db_index=True,
                           help_text=u'该属性用于与终端用户绑定，使得终端用户也可登录')
    mobile = models.CharField(u'手机', max_length=15, null=True, blank=True, help_text=u'管理用户绑定手机号')


class ShipAddress(models.Model):
    uid = models.CharField(u'用户UID', max_length=32, null=False, blank=False, db_index=True)
    receiver = models.CharField(u"收件人", max_length=30, null=True, blank=True)
    receiver_mobile = models.CharField(u"收件人电话", max_length=20, null=True, blank=True)
    ship_province = models.CharField(u"收件省份", choices=PROVINCES, max_length=3, null=False, blank=False)
    ship_city = models.CharField(u"收件市", max_length=10, null=True, blank=True)
    ship_district = models.CharField(u"收件区/县", max_length=10, null=True, blank=True)
    ship_address = models.CharField(u"详细收件地址", max_length=50, null=False, blank=False)
    zip_code = models.CharField(u"邮编", max_length=6, null=True, blank=True)
    is_default = models.BooleanField(u'是否默认地址', default=False)
    # addr_md5 = models.CharField("地址信息MD5", max_length=32, null=True, blank=True, unique=True, editable=False)
    create_time = models.DateTimeField(u'创建时间', null=False, blank=True, auto_now_add=True, editable=False)

    def __unicode__(self):
        return "%s[%s]: %s" % (self.receiver_mobile, self.receiver_mobile, self.ship_address)

    # def md5(self):
    #     import hashlib
    #     return hashlib.md5("%s%s%s%s" % (self.uid, self.receiver, self.receiver_mobile, self.ship_address)).hexdigest()

    # def save(self, force_insert=False, force_update=False, using=None,
    #          update_fields=None):
    #     # self.addr_md5 = self.md5()
    #     super(ShipAddress, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        ordering = ['uid']
        verbose_name_plural = verbose_name = u'用户收件地址'


def _get_account_no():
    return "A%s%s" % (day_str(str_format="%y%m%d%H%M%S"), random_letter(7))


class UserAccountBook(models.Model):
    account_no = models.CharField(u'流水号', max_length=32, default=_get_account_no,
                                  null=False, blank=False, primary_key=True)
    uid = models.CharField(u'用户UID', max_length=32, null=False, blank=False, db_index=True,
                           help_text='对于普通用户是用户的UID，对于供应商，则是"SUP-"前缀 + 供应商编码，如"SUP-TWOHOU"')
    figure = models.DecimalField(u'入账金额', max_digits=10, decimal_places=2, default=0,
                                 blank=False, null=False,
                                 help_text=u"出/入账均计入此栏，正值表示收入，负值表示支出")
    is_income = models.BooleanField(u'是否收入', default=True, help_text=u'如果是支出，应设为False')
    ACCOUNT_TYPES = (
        ('allowance', u'补贴'),
        ('bonus', u'奖励'),
        ('charge', u'充值'),
        ('expense', u'消费支出'),
        ('sales', u'销售收入'),     # 用于供应商
        ('penalty', u'罚款'),
        ('reward', u'回佣'),
        ('roll-in', u'转入'),
        ('roll-out', u'转出'),
        ('withdraw', u'提现'),
        ('deduct', u'扣除'),  # 已收入，因故扣除
        ('return', u'返还'),  # 已扣款，因故返还
        ('other', u'其它')
    )
    type = models.CharField(u'账目类别', max_length=10, null=False, blank=False,
                            default='other', choices=ACCOUNT_TYPES)
    account_desc = models.CharField(u'账目说明', max_length=200, null=True, blank=True)
    trans_no = models.CharField(u'交易单号', max_length=32, null=True, blank=True,
                                help_text=u'收付款时，第三方支付接口返回的交易单号')
    extra_type = models.CharField(u'关联对象类型', max_length=30, null=True, blank=True)
    extra_data = models.CharField(u'补充信息', max_length=500, null=True, blank=True,
                                  help_text=u'用于保存额外的关联数据，比如订单号，转出账号等')
    create_time = models.DateTimeField(u'创建时间', blank=True, null=True, auto_now_add=True)
    effective_time = models.DateTimeField(u'生效时间', blank=True, null=True)

    def __unicode__(self):
        return self.account_no

    # def get_unfrozen_date(self):
    #     delta = timedelta(days=AppSetting.get('app.reward_deferred_days', REWARD_DEFERRED_DAYS))
    #     if self.create_time > now(settings.USE_TZ) - delta:
    #         return self.create_time + delta
    #     else:
    #         return None

    @staticmethod
    def get_account_summary(uid):
        """
        获取指定用户的账号金额统计信息
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
        summary = UserAccountBook.objects.filter(uid=uid).values('is_income')\
            .order_by('is_income').annotate(total=Sum('figure'))

        result = {"uid": uid, "total": 0, "income": 0, "expense": 0}
        for item in summary:
            if item['is_income']:
                result['income'] += item['total']
            else:
                result['expense'] += item['total']

        result['deduct'] = UserAccountBook.objects.filter(uid=uid, is_income=False, type='deduct')\
            .aggregate(total=Sum('figure')).get('total')
        result['deduct'] = result['deduct'] or 0

        result['total'] = result['income'] - result['expense']
        # 未处理的提现请求，提现金额应冻结
        tbd_withdraw_total = WithdrawRequest.objects.filter(uid=uid, status__in=[WithdrawRequest.STATUS_TBD,
                                                            WithdrawRequest.STATUS_AUDITING,
                                                            WithdrawRequest.STATUS_CONFIRMING,
                                                            WithdrawRequest.STATUS_CONFIRMED]).aggregate(Sum('amount'))
        result['withdraw_tbd'] = tbd_withdraw_total.get('amount__sum') or 0
        from config.models import AppSetting
        # delta = now(settings.USE_TZ) - timedelta(days=AppSetting.get('app.reward_deferred_days', REWARD_DEFERRED_DAYS))
        # 收益记录，有一定的冻结时间
        reward_frozen = UserAccountBook.objects.filter(uid=uid, type='reward', effective_time__gt=now(settings.USE_TZ))\
            .aggregate(Sum('figure'))
        result['reward_frozen'] = reward_frozen.get('figure__sum') or 0
        result['available'] = result.get('total', 0) - result.get('withdraw_tbd', 0) - result.get('reward_frozen', 0)
        result['available'] = result['available'] if result['available'] > 0 else 0
        return result

    @staticmethod
    def bd_get_store_summary(store_code):
        """
        获取指定店铺的金额统计信息
        :param store_code:
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
                store_code: "S01234567",
            }
            失败返回错误消息{"error": msg}
        """
        from buding.models import ShopManagerInfo
        uids = []
        uss = ShopManagerInfo.objects.filter(shopcode=store_code)
        for u in uss:
            uids.append(u)

        summary = UserAccountBook.objects.filter(uid__in=uids).values('is_income')\
            .order_by('is_income').annotate(total=Sum('figure'))

        result = {"store_code": store_code, "total": 0, "income": 0, "expense": 0}
        for item in summary:
            if item['is_income']:
                result['income'] += item['total']
            else:
                result['expense'] += item['total']

        result['deduct'] = UserAccountBook.objects.filter(uid__in=uids, is_income=False, type='deduct')\
            .aggregate(total=Sum('figure')).get('total')
        result['deduct'] = result['deduct'] or 0

        result['total'] = result['income'] - result['expense']
        # 未处理的提现请求，提现金额应冻结
        tbd_withdraw_total = WithdrawRequest.objects.filter(uid__in=uids, status__in=[WithdrawRequest.STATUS_TBD,
                                                            WithdrawRequest.STATUS_AUDITING,
                                                            WithdrawRequest.STATUS_CONFIRMING,
                                                            WithdrawRequest.STATUS_CONFIRMED]).aggregate(Sum('amount'))
        result['withdraw_tbd'] = tbd_withdraw_total.get('amount__sum') or 0
        from config.models import AppSetting
        # delta = now(settings.USE_TZ) - timedelta(days=AppSetting.get('app.reward_deferred_days', REWARD_DEFERRED_DAYS))
        # 收益记录，有一定的冻结时间
        reward_frozen = UserAccountBook.objects.filter(uid__in=uids, type='reward', effective_time__gt=now(settings.USE_TZ))\
            .aggregate(Sum('figure'))
        result['reward_frozen'] = reward_frozen.get('figure__sum') or 0
        result['available'] = result.get('total', 0) - result.get('withdraw_tbd', 0) - result.get('reward_frozen', 0)
        result['available'] = result['available'] if result['available'] > 0 else 0
        return result

    def to_dict(self):
        res = model_to_dict(self)
        res['create_time'] = self.create_time
        res['type_display'] = self.get_type_display()
        return res

    def charge_back(self):
        """
        对于当前的流水记录进行相反操作，出账的新增一笔入账记录，入账的则新增一笔扣除操作，不重复处理
        :return:
        """
        acct_type = 'deduct' if self.is_income else 'return'
        try:
            UserAccountBook.objects.get(extra_type='profile.UserAccountBook',
                                        extra_data=self.account_no,
                                        type=acct_type)
            pass  # do nothing if ever exists
        except UserAccountBook.DoesNotExist:
            account_desc = u'撤销[%s]' % self.account_desc
            UserAccountBook.objects.create(extra_type='profile.UserAccountBook',
                                           extra_data=self.account_no,
                                           uid=self.uid,
                                           figure=self.figure,
                                           is_income=not self.is_income,
                                           type=acct_type,
                                           account_desc=account_desc)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # set default effective time immediately
        self.effective_time = self.effective_time or self.create_time or now(settings.USE_TZ)
        super(UserAccountBook, self).save(force_insert=force_insert,
                                          force_update=force_update,
                                          using=using,
                                          update_fields=update_fields)

    class Meta:
        ordering = ['-pk']
        verbose_name_plural = verbose_name = u'用户资金流水'


class UserCapitalAccount(models.Model):
    CAPITAL_ACCOUNT_TYPES = (
        ('wechat', u'微信钱包'),
        ('alipay', u'支付宝'),
        ('deposit', u'储蓄卡'),
        ('credit', u'信用卡'),
        ('enterprise', u'企业账号'),
        ('other', u'其它')
    )
    uid = models.CharField(u'用户UID', max_length=32, null=False, blank=False, db_index=True,
                           help_text='外部用户填写用户uid，内部供应商填写“SUP-供应商id”'
                                     '(id不足12位的需用"0"在左侧补齐)，如SUP-000000000001')
    ca_no = models.CharField(u'资金帐号', max_length=32, null=False, blank=False, unique=True,
                             help_text=u'如果是微信钱包，则为用户openid')
    ca_type = models.CharField(u'账号类别', max_length=10, null=False, blank=False,
                               default='wechat', choices=CAPITAL_ACCOUNT_TYPES)
    ca_name = models.CharField(u'开户名称', max_length=50, null=True, blank=True,
                               help_text='仅用于银行账户')
    ca_mobile = models.CharField(u'预留手机号', max_length=15, null=True, blank=True,
                                 help_text='在银行开户时预留的手机号')
    ca_desc = models.CharField(u'账号说明', max_length=200, null=True, blank=True)
    bank_name = models.CharField(u'银行名称', max_length=30, null=True, blank=True)
    bank_code = models.CharField(u'银行编码', max_length=20, null=True, blank=True)
    open_bank = models.CharField(u'开户行名称', max_length=50, null=True, blank=True)
    is_valid = models.BooleanField(u'是否验证有效', default=False)
    is_default = models.BooleanField(u'是否默认账号', default=False)
    create_time = models.DateTimeField(u'创建时间', blank=True, null=True, auto_now_add=True)

    def clean(self):
        err = []
        if self.ca_type in ['deposit', 'credit']:
            if not self.ca_name:
                err.append(ValidationError({'ca_name': '请提供开户名称'}))
            if not self.ca_mobile:
                err.append(ValidationError({'ca_name': '请提供开户预留手机号'}))
            if not self.open_bank:
                err.append(ValidationError({'ca_name': '请提供开户银行名称'}))
        if len(err) > 0:
            raise ValidationError(err)

    def __unicode__(self):
        return "%s:%s" % (self.get_ca_type_display(), self.ca_no)

    class Meta:
        verbose_name_plural = verbose_name = u'用户资金账号'


class WithdrawRequest(models.Model):
    STATUS_TBD = 0
    STATUS_DONE = 1
    STATUS_FAILED = 2
    STATUS_AUDITING = 3
    STATUS_CONFIRMING = 4
    STATUS_CONFIRMED = 5
    WITHDRAW_STATUSES = (
        (STATUS_TBD, u'处理中'),
        (STATUS_DONE, u'完成'),
        (STATUS_FAILED, u'提现失败'),
        (STATUS_AUDITING, u'待审核'),
        (STATUS_CONFIRMING, u'待确认'),
        (STATUS_CONFIRMED, u'已确认')
    )
    TYPE_PERSONAL = 0
    TYPE_SUPPLIER = 1
    TYPE_OTHER = 2
    UID_TYPE = (
        (TYPE_PERSONAL, u'个人'),
        (TYPE_SUPPLIER, u'供应商'),
        (TYPE_OTHER, u'其他'),
    )
    uid = models.CharField(u'用户UID', max_length=32, null=False, blank=False, db_index=True)
    ca_no = models.CharField(u'资金帐号', max_length=32, null=False, blank=False, db_index=True,
                             help_text=u'提现到指定资金账号，如果是微信钱包，则为用户openid')
    ca_type = models.CharField(u'账号类别', max_length=10, null=False, blank=False,
                               default='wechat', choices=UserCapitalAccount.CAPITAL_ACCOUNT_TYPES)
    # bank_name = models.CharField(u'银行名称', max_length=30, null=True, blank=True)
    # bank_code = models.CharField(u'银行编码', max_length=20, null=True, blank=True)
    # open_bank = models.CharField(u'开户行名称', max_length=50, null=True, blank=True)
    amount = models.DecimalField(u'提现金额', max_digits=10, decimal_places=2, default=0,
                                 blank=False, null=False,
                                 help_text=u"提现金额不得超过当时用户账户可用余额")
    status = models.PositiveSmallIntegerField(u'提现结果', default=STATUS_TBD, choices=WITHDRAW_STATUSES)
    result = models.CharField(u'提现结果说明', max_length=200, null=True, blank=True)
    account_no = models.CharField(u'流水号', max_length=32, null=True, blank=True, db_index=True)
    create_time = models.DateTimeField(u'创建时间', blank=True, null=True, auto_now_add=True)
    process_time = models.DateTimeField(u'完成时间', blank=True, null=True)
    uid_type = models.PositiveSmallIntegerField(u'用户类型', default=TYPE_OTHER, choices=UID_TYPE)
    real_uid = models.CharField(u'提现用户UID', max_length=32, null=True, blank=True, db_index=False,
                                help_text=u'对于非个人提现申请，这里将保存发起提现申请的用户UID')

    def confirm(self, trans_no=None):
        """
        确认提现申请已执行打款操作
        :param trans_no:
            第三方交易接口交易流水号
        :return:
            返回TMS系统的资金流水号
        """
        # if self.status != self.STATUS_TBD:
        if self.status not in [self.STATUS_TBD, self.STATUS_CONFIRMED]:
            raise ValueError(u'已处理的提现申请不可重复确认！')

        desc = u'提现￥%s到%s' % (self.amount, self.get_ca_type_display())
        uab, created = UserAccountBook.objects.get_or_create(type='withdraw',
                                                             uid=self.uid,
                                                             extra_data=self.pk,
                                                             extra_type='profile.WithdrawRequest',
                                                             figure=self.amount,
                                                             is_income=False,
                                                             account_desc=desc,
                                                             trans_no=trans_no)
        if created:
            self.account_no = uab.account_no
            self.status = self.STATUS_DONE
            self.save()

        # TODO: may do sth. if failed
        return self.account_no

    def audited(self, trans_no=None):
        """
        （管理员）审核供应商提现申请
        :param trans_no:
            第三方交易接口交易流水号
        :return:
            返回TMS系统的资金流水号
        """
        if self.status != self.STATUS_AUDITING:
            raise ValueError(u'不是待审核状态待的提现申请不可审核确认通过！')

        # desc = u'提现￥%s到%s' % (self.amount, self.get_ca_type_display())
        # uab, created = UserAccountBook.objects.get_or_create(type='withdraw',
        #                                                      uid=self.uid,
        #                                                      extra_data=self.pk,
        #                                                      extra_type='profile.WithdrawRequest',
        #                                                      figure=self.amount,
        #                                                      is_income=False,
        #                                                      account_desc=desc,
        #                                                      trans_no=trans_no)
        # if created:
        # self.account_no = ''
        self.status = self.STATUS_CONFIRMING
        self.process_time = now(settings.USE_TZ)
        self.save()

        # TODO: may do sth. if failed
        return self.account_no

    def confirmed(self, trans_no=None):
        """
        （财务）确认供应商提现申请
        :param trans_no:
            第三方交易接口交易流水号
        :return:
            返回TMS系统的资金流水号
        """
        if self.status != self.STATUS_CONFIRMING:
            raise ValueError(u'不是待确认状态的提现申请不可确认通过！')

        # desc = u'提现￥%s到%s' % (self.amount, self.get_ca_type_display())
        # uab, created = UserAccountBook.objects.get_or_create(type='withdraw',
        #                                                      uid=self.uid,
        #                                                      extra_data=self.pk,
        #                                                      extra_type='profile.WithdrawRequest',
        #                                                      figure=self.amount,
        #                                                      is_income=False,
        #                                                      account_desc=desc,
        #                                                      trans_no=trans_no)
        # if created:
        # self.account_no = ''
        self.status = self.STATUS_CONFIRMED
        self.process_time = now(settings.USE_TZ)
        self.save()

        # TODO: may do sth. if failed
        return self.account_no

    def __unicode__(self):
        return u"申请提现￥%s到%s" % (self.amount, self.get_ca_type_display())

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.process_time and self.status != WithdrawRequest.STATUS_TBD:
            self.process_time = now(settings.USE_TZ)

        super(WithdrawRequest, self).save(force_insert=force_insert,
                                          force_update=force_update,
                                          using=using,
                                          update_fields=update_fields)

    class Meta:
        ordering = ['-pk']
        verbose_name_plural = verbose_name = u'用户提现申请记录'


