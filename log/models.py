# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
# from vendor.models import BusinessEntity, Supplier, Manufacturer, LogisticsVendor, Contact
from django.contrib.auth.models import User
from tms.config import *
from util import jsonall
from util.renderutil import random_code, now, logger
from util.webtool import sendmail
# from django.core.mail import send_mail

# class UserLog(models.Model):
#     user = models.ForeignKey(User, verbose_name="用户", null=False, blank=True, editable=False)
#     content_type = models.PositiveIntegerField("对象类型", null=False, blank=False)
#     content_id = models.PositiveIntegerField("对象ID", default=0, null=False, blank=False, db_index=True)
#     act_time = models.DateTimeField('操作时间', auto_now_add=True, blank=True, null=True, editable=False)
#     log = models.CharField("日志信息", max_length=300, null=False, blank=False)
#     log_time = models.DateTimeField('记录时间', auto_now_add=True, blank=True, null=True, editable=False)
#
#     def __unicode__(self):
#         return "%s: USER(%s) %s" % (self.log_time, self.user, self.log)
#
#     class Meta:
#         verbose_name_plural = verbose_name = '操作日志'


class UserFeedback(models.Model):
    user = models.ForeignKey(User, verbose_name="用户", null=False, blank=True)
    feedback = models.TextField("意见或者建议", max_length=500, null=False, blank=False)
    answer = models.CharField("答复", max_length=200, null=True, blank=True)
    # 以下字段信息用于排序、筛选及安全审计
    create_time = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True, editable=False)
    create_by = models.IntegerField('创建人', blank=True, null=True, editable=False)
    update_time = models.DateTimeField('更新时间', auto_now=True, blank=True, null=True, editable=False)
    update_by = models.IntegerField('更新人', blank=True, null=True, editable=False)

    def __unicode__(self):
        return "%s@%s: %s" % (self.user,
                              self.create_time,
                              self.feedback[:10]+"..." if len(self.feedback) > 10 else self.feedback)

    class Meta:
        ordering = ['-id']
        verbose_name_plural = verbose_name = '用户反馈'


class UserSmsLog(models.Model):
    STATUS_TBD = 0  # 待发送
    STATUS_SENT_OK = 1    # 发送成功
    STATUS_SENT_FAILURE = 2    # 发送失败
    STATUS_SENDING = 3    # 发送中
    SMS_STATUSES = (
        (STATUS_TBD, "待发送"),
        (STATUS_SENDING, "发送中"),
        (STATUS_SENT_OK, "发送成功"),
        (STATUS_SENT_FAILURE, "发送失败"),
    )
    mobile = models.CharField('手机', max_length=15, null=False, blank=False, db_index=True)
    sms = models.CharField("短信内容", max_length=300, null=False, blank=False)
    status = models.PositiveSmallIntegerField("状态", default=STATUS_TBD, choices=SMS_STATUSES)
    allow_retries = models.PositiveSmallIntegerField("允许重试次数", default=1,
                                                     help_text="当允许重试次数减为0后不再发送该短信")
    send_time = models.DateTimeField('发送时间', auto_now_add=True, blank=True, null=True)
    log = models.CharField('操作结果', max_length=300, blank=True, null=True)

    def __unicode__(self):
        return "SMS TO %s@%s: %s" % (self.mobile, self.send_time, self.sms)

    @staticmethod
    def put_in_queue(data, instant=False):
        if not data:
            return
        elif isinstance(data, list):
            logs = [UserSmsLog(mobile=d.get('mobile'), sms=d.get('message')) for d in data]
            UserSmsLog.objects.bulk_create(logs)
        elif isinstance(data, dict):
            logs = [UserSmsLog.objects.create(mobile=data.get('mobile'), sms=data.get('message'))]

    class Meta:
        ordering = ['-id']
        verbose_name_plural = verbose_name = '短信发送日志'


class UserMailLog(models.Model):
    # msg_type = models.PositiveSmallIntegerField("邮件类型", default=MSG_TYPE_OTHER, choices=MSG_TYPES)
    mail_from = models.CharField('发件地址', max_length=60, default=settings.DEFAULT_FROM_EMAIL, null=True, blank=True)
    # mail_to = models.CharField('收件地址', max_length=60, null=False, blank=False)
    # mail_cc = models.CharField('抄送地址', max_length=60, null=True, blank=True)
    # mail_bcc = models.CharField('密件抄送地址', max_length=60, null=True, blank=True)
    subject = models.CharField("主题", max_length=100, null=False, blank=False)
    body = models.CharField('正文', max_length=1000, blank=True, null=True)
    attachments = models.CharField('附件地址', max_length=1000, blank=True, null=True,
                                   help_text='多个附件以分号分隔')
    create_time = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    send_time = models.DateTimeField('最近发送时间', auto_now=True, blank=True, null=True)
    retries = models.PositiveSmallIntegerField('发送次数', default=0)
    is_sent = models.BooleanField('是否已发送', default=False, db_index=True)

    def __unicode__(self):
        return "[%s]: %s" % (self.create_time, self.subject)

    def get_mail_to(self):
        return [(r.mail_type, r.mail_to) for r in self.emailrecipient_set.all()]

    @staticmethod
    def put_in_queue(mail_to, subject='', body='', mail_cc=None, mail_bcc=None,
                     attachments=None, mail_from=settings.DEFAULT_FROM_EMAIL):
        """
        将邮件发送请求放入邮件队列，返回队列中的id
        """
        addr = []
        if mail_to:
            if isinstance(mail_to, basestring):
                mail_to = mail_to.split(',')
            mail_to = set(mail_to)
            addr.extend([('to', t) for t in mail_to])

        if mail_cc:
            if isinstance(mail_cc, basestring):
                mail_cc = mail_cc.split(',')
            mail_cc = set(mail_cc)
            addr.extend([('cc', t) for t in mail_cc])

        if mail_bcc:
            if isinstance(mail_bcc, basestring):
                mail_bcc = mail_bcc.split(',')
            mail_bcc = set(mail_bcc)
            addr.extend([('bcc', t) for t in mail_bcc])

        mail_log = UserMailLog(subject=subject, body=body,
                               attachments=attachments, mail_from=mail_from)
        mail_log.save()
        EmailRecipient.objects.bulk_create([EmailRecipient(mail=mail_log, mail_to=to, mail_type=t) for t, to in addr])

        return mail_log.id

    def send_mail(self):
        # TODO: mail_cc, mail_bcc, attachments not yet supported
        if getattr(settings, 'FAKE_EMAIL', False):
            self.is_sent = True
        else:
            recipient_list = [r.mail_to for r in self.emailrecipient_set.all()]
            try:
                sendmail(subject=self.subject,
                         message=self.body,
                         from_email=self.mail_from or settings.DEFAULT_FROM_EMAIL,
                         recipient_list=recipient_list)
                self.is_sent = True
            except Exception, e:
                logger.error('sending mail to %s failed: %s' % (','.join(recipient_list), self.subject))
                logger.exception(e)
        self.retries += 1
        self.send_time = now(settings.USE_TZ)
        self.save()

    class Meta:
        ordering = ['-send_time']
        verbose_name_plural = verbose_name = u'Email通知发送日志'


class EmailRecipient(models.Model):
    mail = models.ForeignKey(UserMailLog, verbose_name=u'邮件', null=False, blank=False)
    mail_to = models.CharField(u'收件地址', max_length=60, null=False, blank=False)
    mail_type = models.CharField(u'发送类型', max_length=3, default='to', null=False, blank=True,
                                 choices=(('to', u'正常'), ('cc', u'抄送'), ('bcc', u'密送')))

    def __unicode__(self):
        return "%s:%s" % (self.mail_type, self.mail_to)

    class Meta:
        verbose_name_plural = verbose_name = u'Email收件人'


class UserPayLog(models.Model):
    uid = models.CharField('付款人UID', max_length=32, null=False, blank=False, db_index=True)
    pay_code = models.CharField('支付码', max_length=32, null=False, blank=False, db_index=True)
    order_no = models.CharField("订单编号", max_length=20, blank=False, null=False, db_index=True)
    pay_type = models.IntegerField('支付方式', default=PAY_NOT_YET, choices=PAY_TYPES,
                                   null=False, blank=False)
    pay_amount = models.DecimalField('支付总额', max_digits=10, decimal_places=2,
                                     blank=False, null=False)
    pay_time = models.DateTimeField('支付时间', auto_now_add=True, blank=True, null=True, db_index=True)
    pay_log = models.TextField('支付记录', max_length=2000, blank=True, null=True)
    is_confirmed = models.BooleanField('支付确认', default=False,
                                       help_text='支付后跟支付平台确认支付结果')
    is_refund = models.BooleanField('是否退款', default=False, help_text="仅当退款时标记为True")

    def __unicode__(self):
        res = '已确认' if self.is_confirmed else '待确认'
        type_txt = "支付" if self.is_refund else "退款"
        return "【%s】%s 于 %s 为 %s %s(%s) %s" % \
               (res, self.uid, self.pay_time, self.order_no, type_txt,
                self.get_pay_type_display(), self.pay_amount)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.pay_code:
            self.pay_code = 'UP' + random_code(30)
        super(UserPayLog, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name_plural = verbose_name = '订单支付/退款记录'
        unique_together = ['order_no', 'is_refund']


class PingppHookLog(models.Model):
    event_id = models.CharField('事件id', max_length=32, null=True, blank=True)
    object = models.CharField('对象（值为event）', default='event', max_length=32,
                              null=True, blank=True)
    livemode = models.BooleanField('是否生产')
    created = models.PositiveIntegerField('时间戳', null=True, blank=True)
    data = models.CharField('事件绑定数据', max_length=2000, null=True, blank=True)
    pending_webhooks = models.PositiveIntegerField('推送未成功数', default=0, null=True, blank=True)
    type = models.CharField('事件类型', max_length=50, null=True, blank=True)
    request = models.CharField('API Request ID', max_length=32, null=True, blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True, null=True, blank=True)

    def __unicode__(self):
        return "%s[%s]" % (self.object, self.event_id)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not isinstance(self.data, str):
            self.data = jsonall.json_encode(self.data)

        super(PingppHookLog, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name_plural = verbose_name = 'PingppHook事件反馈及统计记录'


class AgentQueryLog(models.Model):
    agent = models.ForeignKey(User, verbose_name='前台', null=False, blank=False, db_index=True)
    query_time = models.DateTimeField('查询时间', auto_now_add=True, blank=True, null=True, db_index=True)
    RESULT_NO_ACTION = 0
    RESULT_PAID = 1
    RESULT_INVOKED = 2
    RESULT_RECEIVED_BYSELF = 3
    RESULT_ADD_TO_PMS = 4
    QUERY_RESULTS = (
        (RESULT_NO_ACTION, '无操作'),
        (RESULT_ADD_TO_PMS, '已入账PMS'),
        (RESULT_PAID, '已支付'),
        (RESULT_RECEIVED_BYSELF, '已自提'),
        (RESULT_INVOKED, '已取消'),
    )
    query_result = models.SmallIntegerField('订单结果', default=RESULT_NO_ACTION, choices=QUERY_RESULTS,
                                            help_text='前台查询订单后操作结果')
    order_no = models.CharField("订单编号", max_length=20, blank=False, null=False, db_index=True)
    user_id = models.CharField('用户手机号', max_length=36, null=False, blank=False, db_index=True)
    pay_amount = models.DecimalField('支付总额￥', max_digits=10, decimal_places=2,
                                     blank=False, null=False, help_text="含订单商品总额、运费、优惠等费用")
    is_checked = models.BooleanField('是否已验证', default=False, help_text='如果存在可疑行为，此项记录已经验证过，无需再提示')

    def __unicode__(self):
        return "%s 于 %s 查询订单 %s（应支付%s），操作结果：%s" % \
               (self.agent.get_full_name(), self.query_time, self.order_no, self.pay_amount, self.get_query_result_display())

    class Meta:
        verbose_name_plural = verbose_name = '前台订单查询日志'


class TaskLog(models.Model):
    name = models.CharField('任务名称', max_length=30, null=False, blank=False, db_index=True)
    start_time = models.DateTimeField('开始时间', null=True, blank=True, db_index=True)
    end_time = models.DateTimeField('结束时间', null=True, blank=True)
    time_cost = models.PositiveIntegerField('耗时(秒)', default=0)
    exec_result = models.CharField('执行结果', max_length=20480, null=True, blank=True)
    is_ok = models.BooleanField('是否正常', default=True)
    result_file = models.FilePathField('结果文件', max_length=200, null=True, blank=True)

    def __unicode__(self):
        return "%s: %s" % (self.name, "成功" if self.is_ok else "未成功")

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.start_time and self.end_time:
            time_delta = self.end_time - self.start_time
            self.time_cost = time_delta.total_seconds()

        super(TaskLog, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name_plural = verbose_name = '计划任务执行日志'


class WechatMsgLog(models.Model):
    """
    微信消息记录
    """
    # msg_type = models.PositiveSmallIntegerField("消息类型", default=MSG_TYPE_OTHER, choices=MSG_TYPES)
    business_code = models.CharField('业务代码', max_length=32, null=True, blank=True, db_index=True,
                                     help_text='用于不同业务场景')
    uid = models.CharField('接收用户ID', max_length=32, null=False, blank=False, db_index=True)
    open_id = models.CharField('微信OpenID', max_length=32, null=True, blank=True, db_index=True)
    subject = models.CharField("主题", max_length=100, null=False, blank=False)
    body = models.CharField('正文', max_length=1000, blank=True, null=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True, db_index=True)
    send_time = models.DateTimeField('最近发送时间', auto_now=True, blank=True, null=True)
    retries = models.PositiveSmallIntegerField('发送次数', default=0)
    is_sent = models.BooleanField('是否已发送', default=False, db_index=True)
    sender = models.CharField('发送者', max_length=18, null=True, blank=True, db_index=True,
                              help_text='用于多任务处理避免访问冲突')
    claim_time = models.DateTimeField('发送者领取任务时间', blank=True, null=True)

    def __unicode__(self):
        return "微信消息: %s" % self.subject

    @staticmethod
    def put_in_queue(uid=None, open_id=None, subject='无主题', body='', business_code=None):
        from profile.models import EndUserExt
        users = []
        if uid:
            uids = uid if isinstance(uid, list) else uid.split(',')
            users = EndUserExt.objects.filter(uid__in=uids,
                                              ex_id_type__in=[EndUserExt.ID_TYPE_WECHAT_OPENID, EndUserExt.ID_TYPE_WECHAT_UNIONID])\
                .values_list('uid', 'ex_id')
        elif open_id:
            open_ids = open_id if isinstance(open_id, list) else open_id.split(',')
            users = EndUserExt.objects.filter(ex_id__in=open_ids,
                                              ex_id_type__in=[EndUserExt.ID_TYPE_WECHAT_OPENID, EndUserExt.ID_TYPE_WECHAT_UNIONID])\
                .values_list('uid', 'ex_id')

        if not subject or not body:
            raise ValueError('消息标题及内容不能为空！')

        if len(users) > 0:
            WechatMsgLog.objects.bulk_create(
                [WechatMsgLog(business_code=business_code,
                              uid=user_uid,
                              open_id=user_oid,
                              subject=subject,
                              body=body) for user_uid, user_oid in users])
        return len(users)

    def send_message(self):
        import urllib2
        import urllib

        body = self.body.split(":")
        credit = body[1].strip()
        # 定义一个要提交的数据数组(字典)
        data = {}
        data['uid'] = self.uid
        data['integral'] = credit
        # 定义post的地址
        # local test server
        # url = 'http://192.168.10.132:4000/itravelbuy-api/onInformShareGetIntegral?%s'
        # remote test server
        # url = 'http://test2.itravelbuy.twohou.com/itravelbuy-api/onInformShareGetIntegral?%s'
        # product server
        url = 'http://abuhome.podinns.com/itravelbuy-api/onInformShareGetIntegral?%s'
        get_data = urllib.urlencode(data)
        # 提交，发送数据
        req = urllib2.urlopen(url % get_data)
        # 获取提交后返回的信息
        content = req.read()

        self.is_sent = True
        self.retries += 1
        self.send_time = now(settings.USE_TZ)
        self.save()

    class Meta:
        verbose_name_plural = verbose_name = '微信消息发送日志'
