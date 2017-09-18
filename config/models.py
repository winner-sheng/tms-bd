# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import json

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone
from django.db.models.fields import NOT_PROVIDED

from filemgmt.models import BaseImage
from tms import settings
from ueditor.models import UEditorField
from util import renderutil
from util.renderutil import now
from copy import deepcopy


class Banner(models.Model):
    subject = models.CharField('主题', max_length=20, null=True, blank=True)
    image = models.ForeignKey(BaseImage, verbose_name='Banner图片', related_name='banner_image+',
                              null=False, blank=False,
                              help_text='请根据前端页面需要上传图片，确保同一场景下多张图片尺寸比例一致！')
    link_to = models.CharField('目标地址', max_length=100, null=True, blank=True,
                               help_text='即用户点击该图片后，打开的页面地址')
    list_order = models.PositiveIntegerField('显示顺序(大的在前)', default=0, null=True, blank=True)
    effective_date = models.DateTimeField('生效时间', null=True, blank=True, default=datetime.datetime.now,
                                          help_text='只有生效时间后的图片才会展示')
    scenario = models.CharField('应用场景', max_length=36, null=True, blank=True, db_index=True,
                                help_text='用于标记该项用于什么样的场景，即显示在不同的前端页面，留空表示默认场景')
    is_active = models.BooleanField("是否有效", default=True, null=False, blank=False)
    owner = models.CharField('归属对象ID', max_length=36, null=True, blank=True, db_index=True,
                             help_text='归属对象可以是用户uid，如"uid:xxx"，也可能是供应商id，如"sup:xxx等"')
    # 以下字段信息用于排序、筛选及安全审计
    create_time = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True, editable=False)
    create_by = models.IntegerField('创建人', blank=True, null=True, editable=False)
    update_time = models.DateTimeField('更新时间', auto_now=True, blank=True, null=True, editable=False)
    update_by = models.IntegerField('更新人', blank=True, null=True, editable=False)

    def __unicode__(self):
        return "%s(ID:%s)" % (self.subject, self.pk)

    def clone(self, exclude=None):
        new_banner = deepcopy(self)
        new_banner.subject = "【克隆自】%s" % self.subject
        if exclude:
            for attr in exclude:
                if 'product_images' == attr:
                    continue
                default = Banner._meta.get_field(attr).default
                setattr(new_banner, attr, None if default is NOT_PROVIDED else default)
        new_banner.pk = None
        new_banner.is_active = False
        new_banner.create_time = new_banner.update_time = now(settings.USE_TZ)
        new_banner.save()
        return new_banner

    def clean(self):
        self.scenario = self.scenario and self.scenario.replace(',', '_')

    @staticmethod
    def get_banners(scenario=None, owner=None):
        results = []
        cur_time = timezone.now() if settings.USE_TZ else datetime.datetime.now()
        banners = Banner.objects.filter(is_active=True, effective_date__lt=cur_time)
        if scenario is None:
            banners = banners.filter(scenario__isnull=True)
        else:
            if ',' in scenario:
                banners = banners.filter(scenario__in=scenario.split(','))
            else:
                banners = banners.filter(scenario=scenario)

        for banner in banners:
            b = model_to_dict(banner, fields=('subject', 'link_to', 'list_order'))
            # b['image'] = banner.image.origin.url
            b['image'] = banner.image.large
            results.append(b)

        return results

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.effective_date is None:
            self.effective_date = renderutil.now(settings.USE_TZ)
        super(Banner, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        ordering = ('-list_order', 'id')
        verbose_name_plural = verbose_name = '页面设置-广告与导航'


# class Channel(models.Model):
#     subject = models.CharField('频道名称', max_length=20, null=False, blank=False)
#     image = models.ForeignKey(BaseImage, verbose_name='频道图片', related_name='channel_image+',
#                               null=False, blank=False, help_text='请注意上传图片尺寸应匹配前端页面布局要求')
#     link_to = models.CharField('目标地址', max_length=100, null=True, blank=True,
#                                help_text='即用户点击该频道后，打开的页面地址')
#     list_order = models.PositiveIntegerField('显示顺序(大的在前)', default=0, null=True, blank=True)
#     scenario = models.CharField('应用场景', max_length=36, null=True, blank=True, db_index=True,
#                                 help_text='用于标记该项用于什么样的场景，即显示在不同的前端页面，留空表示默认场景')
#     is_active = models.BooleanField("是否有效", default=True, null=False, blank=False)
#     # 以下字段信息用于排序、筛选及安全审计
#     create_time = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True, editable=False)
#     create_by = models.IntegerField('创建人', blank=True, null=True, editable=False)
#     update_time = models.DateTimeField('更新时间', auto_now=True, blank=True, null=True, editable=False)
#     update_by = models.IntegerField('更新人', blank=True, null=True, editable=False)
#
#     cache_key = "tms-config-channels"
#     @staticmethod
#     def get_channels(scenario=None):
#         cached_key = "%s-%s" % (Channel.cache_key, scenario or '')
#         cached_val = cache.get(cached_key)
#         if cached_val:
#             return cached_val
#         else:
#             results = []
#             channels = Channel.objects.filter(is_active=True)
#             for channel in channels:
#                 c = model_to_dict(channel, fields=('id', 'subject', 'link_to', 'list_order'))
#                 # c['image'] = channel.image.origin.url
#                 c['image'] = channel.image.large
#                 results.append(c)
#
#             cache.set(cached_key, results)
#             return results
#
#     def save(self, force_insert=False, force_update=False, using=None,
#              update_fields=None):
#         cached_key = "%s-%s" % (Channel.cache_key, self.scenario or '')
#         cache.delete(cached_key)
#         super(Channel, self).save(force_insert, force_update, using, update_fields)
#
#     def __unicode__(self):
#         return "%s" % self.subject
#
#     class Meta:
#         ordering = ('-list_order', 'id')
#         verbose_name_plural = verbose_name = '页面设置-频道'
#
#
# class ChannelProduct(models.Model):
#     channel = models.ForeignKey('Channel', verbose_name='频道', null=False, blank=False)
#     product = models.ForeignKey('basedata.Product', verbose_name='商品', null=False, blank=False,
#                                 limit_choices_to={'status': 1})  # 1.STATUS_ONSHELF
#     list_order = models.PositiveIntegerField('显示顺序(大的在前)', default=0, null=True, blank=True)
#
#     def __unicode__(self):
#         return "%s:%s" % (self.channel, self.product)
#
#     class Meta:
#         ordering = ('-list_order', 'id')
#         verbose_name_plural = verbose_name = '页面设置-频道商品映射表'
#
#
# ARTICLE_CATEGORIES = (
#     (1, '其它'),
#     (2, '精品推荐'),
#     (3, '特产百科')
# )
# class Article(models.Model):
#     subject = models.CharField('文章主题', default='文章主题', max_length=20, null=False, blank=False)
#     subject_image = models.ForeignKey(BaseImage, verbose_name='主题图片', related_name='discovery_subject_image+',
#                                       null=True, blank=True,
#                                       help_text='建议使用宽度为不超过600像素的图片，高度根据需要酌情设计')
#     content_image = models.ForeignKey(BaseImage, verbose_name='内容图片', related_name='discovery_content_image+',
#                                       null=True, blank=True, help_text='查看文章的详情时显示，默认与主题图片相同')
#     category = models.PositiveIntegerField("类别", choices=ARTICLE_CATEGORIES, default=1,
#                                            db_index=True, null=True, blank=True)
#     tags = models.CharField("文章Tag", max_length=255, db_index=True, null=True, blank=True,
#                             help_text='用于文章搜索，每个标签之间应使用英文逗号","分隔，标签为精确匹配')
#     brief = models.CharField("简介", max_length=500, null=True, blank=True,
#                              help_text='文章简介，一般用于文章列表显示摘要')
#     content = UEditorField('内容描述', max_length=20000, null=True, blank=True, width=900, height=600,
#                            help_text='注意：建议使用不超过800像素宽度的图片。'
#                                      '除非明确知道设置图片大小的目的，否则请不要指定图片大小，由页面自动缩放')
#     link_to = models.CharField('目标地址', max_length=100, null=True, blank=True,
#                                help_text='即用户点击该主题图片后，打开的外链地址（默认在商城中打开，无需配置）')
#     list_order = models.PositiveIntegerField('显示顺序(大的在前)', default=0, null=True, blank=True, db_index=True)
#     effective_date = models.DateTimeField('生效时间', null=True, blank=True, default=datetime.datetime.now,
#                                           help_text='只有生效时间后的文章才会展示')
#     is_active = models.BooleanField("是否有效", default=True, null=False, blank=False)
#     product_tags = models.CharField("关联商品Tag", max_length=1024, db_index=True, null=True, blank=True,
#                                     help_text='用于文章与商品匹配搜索，格式为"<关联属性>:<关联值>"，可以有多个，中间使用英文逗号","分隔。'
#                                               '关联属性可以是名称、类别、Tag、品牌、产地、供应商中的一种或几种。'
#                                               '如："名称:月饼,类别:食品,Tag:送礼,品牌:利男居,产地:上海,供应商:TWOHOU-02"')
#     # 以下字段信息用于排序、筛选及安全审计
#     create_time = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True, editable=False)
#     create_by = models.IntegerField('创建人', blank=True, null=True, editable=False)
#     update_time = models.DateTimeField('更新时间', auto_now=True, blank=True, null=True, editable=False)
#     update_by = models.IntegerField('更新人', blank=True, null=True, editable=False)
#
#     def clean(self):
#         if self.product_tags and ',' in self.product_tags and '|' in self.product_tags:
#             raise ValidationError('多个关联商品Tag只能使用","或"|"中的一种符号分隔，不可同时使用')
#
#     def to_dict(self, detail=False):
#         if detail:
#             res = model_to_dict(self, fields=('id', 'subject', 'brief', 'tags', 'content', 'link_to', 'list_order'))
#             res['content_image'] = self.content_image.large if self.content_image else ''
#         else:
#             res = model_to_dict(self, fields=('id', 'subject', 'brief',  'tags', 'link_to', 'list_order'))
#         res['subject_image'] = self.subject_image.large if self.subject_image else ''
#         return res
#
#     def save(self, force_insert=False, force_update=False, using=None,
#              update_fields=None):
#         # cache_key = "tms-config-articles"
#         # cache.delete(cache_key)
#         if self.effective_date is None:
#             self.effective_date = renderutil.now(settings.USE_TZ)
#         if self.tags:
#             self.tags = self.tags.replace('，', ',')
#         super(Article, self).save(force_insert, force_update, using, update_fields)
#
#     def __unicode__(self):
#         return "%s" % self.subject
#
#     class Meta:
#         ordering = ('-list_order', '-update_time')
#         verbose_name_plural = verbose_name = '文章'
#
#
# class ArticleProduct(models.Model):
#     article = models.ForeignKey(Article, verbose_name='文章', null=False, blank=False)
#     # 1.STATUS_ONSHELF, 3, # STATUS_RESHELF
#     product = models.ForeignKey('basedata.Product', verbose_name='商品', null=False, blank=False,
#                                 limit_choices_to={'status': 1})
#     list_order = models.PositiveIntegerField('显示顺序(大的在前)', default=0, null=True, blank=True)
#
#     def __unicode__(self):
#         return "%s:%s" % (self.article, self.product)
#
#     class Meta:
#         ordering = ('-list_order', 'id')
#         verbose_name_plural = verbose_name = '文章商品映射表'


# class SystemSetting(models.Model):
#     property = models.CharField('')


class District(models.Model):
    LEVEL = (
        (0, '国家/地区'),
        (1, '省/直辖市/自治区'),
        (2, '市/区（地级）'),
        (3, '市/区/县（县级）'),
        (4, '镇/乡/街道'),
        (5, '村/弄/小区'),
    )
    # district_id = models.PositiveIntegerField(primary_key=True, auto_created=True, editable=False)
    name = models.CharField('名称', max_length=20, blank=False)
    pinyin = models.CharField('拼音', max_length=80, blank=True, null=True, db_index=True)
    pinyin_abbr = models.CharField('拼音缩写', max_length=20, blank=True, null=True, db_index=True)
    level = models.PositiveSmallIntegerField(choices=LEVEL, blank=False)
    up = models.ForeignKey('self', verbose_name='上级', on_delete=models.SET_NULL,
                           blank=True, null=True, db_index=True)
    use_type = models.PositiveIntegerField(default=0, help_text='保留字段')
    # 顺序，数值越大排序越靠前，如果都为0，则按主键排序
    list_order = models.PositiveIntegerField('排序标记', default=0, help_text='数值越大，排序越靠前', db_index=True)

    @staticmethod
    def get_districts(level=None, up_id=None):
        level = level if level is not None else 1  # default 1, 省级
        records = District.objects.filter(level=level)
        if up_id is not None:
            records = records.filter(up_id=up_id)
        results = records.values("id", "name", "up_id")
        return results

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ['name', 'level']
        ordering = ['level', '-list_order', 'name']
        verbose_name_plural = verbose_name = '行政区划'


def create_token(size=32):
    """
    生成默认令牌，32位
    :return:
    """
    return renderutil.random_str(size)


class ApiAuth(models.Model):
    grant_to = models.CharField('授权对象', max_length=30, null=False, blank=False,
                                help_text='描述接口许可对象是谁')
    visitor_code = models.CharField('授权对象识别码', max_length=30, null=True, blank=True,
                                    help_text='令牌验证通过后，自动返回授权对象的身份编码，'
                                              '某些情况下相关接口返回数据内容需根据此识别码进行区分')
    token = models.CharField('授权令牌(可自动生成)', max_length=32, null=False, blank=False, unique=True,
                             default=create_token,
                             help_text='32位令牌，可自动生成。外部访问授权接口时，必须带此token，否则拒绝访问')
    api_list = models.CharField('许可接口列表', max_length=1024, null=True, blank=True,
                                help_text='如果设定此项，则只允许外部用户使用token访问的接口列表，'
                                          '多个接口用","分隔，默认不做限制')
    ip_list = models.CharField('许可来源IP列表', max_length=1024, null=True, blank=True,
                               help_text='如果设定此项，则只允许列表中的来源IP访问相关接口，'
                                         '多个IP用","分隔，默认不做限制')
    grant_by = models.ForeignKey(User, verbose_name='授权人', null=False, blank=True)

    create_time = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True, editable=False)
    update_time = models.DateTimeField('更新时间', auto_now=True, blank=True, null=True, editable=False)

    def __unicode__(self):
        return self.grant_to

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.token:
            self.token = renderutil.random_str(32)
        super(ApiAuth, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name_plural = verbose_name = 'API接口授权'


class AppSetting(models.Model):
    CATEGORIES = (
        ('app', '全局'),
        ('activity', '活动相关'),
        ('callback', '回调URL'),
        ('payment', '支付参数'),
    )
    category = models.CharField('类别', max_length=30, null=False, blank=False, default='app',
                                choices=CATEGORIES)
    CHAR_TYPE = 0
    INT_TYPE = 1
    FLOAT_TYPE = 2
    HTML_TYPE = 8
    JSON_TYPE = 9
    # PASSWORD_TYPE = 10
    VALUE_TYPES = (
        (CHAR_TYPE, '字符型'),
        (INT_TYPE, '整形数值'),
        (FLOAT_TYPE, '浮点数值'),
        (HTML_TYPE, 'HTML格式'),
        (JSON_TYPE, 'JSON格式'),
        # (PASSWORD_TYPE, '密码/密钥'),
    )
    name = models.CharField('配置项键值', max_length=30, null=False, blank=False,
                            help_text='建议使用英文字符表示')
    usage = models.CharField('配置项用途', max_length=255, null=True, blank=True)
    value_type = models.PositiveSmallIntegerField('数据格式', default=CHAR_TYPE, choices=VALUE_TYPES)
    value = models.CharField('配置项值', max_length=1024, null=True, blank=True)

    def __unicode__(self):
        return "%s.%s:" % (self.category, self.name)

    @staticmethod
    def get_app_setting(force_refresh=False):
        cache_key = 'tms_app_settings'
        app_settings = cache.get(cache_key)
        if not app_settings or force_refresh:
            app_settings = AppSetting.objects.all().values('category', 'name', 'value_type', 'value')
            results = {}
            for s in app_settings:
                results[s['category']] = results.get(s['category'], {})
                v = s['value']
                if s['value_type'] == AppSetting.INT_TYPE:
                    v = int(v)
                elif s['value_type'] == AppSetting.FLOAT_TYPE:
                    v = float(v)
                elif s['value_type'] == AppSetting.JSON_TYPE:
                    v = json.loads(v)
                results[s['category']][s['name'].lower()] = v
            app_settings = results
            cache.set(cache_key, app_settings, timeout=3600*24)
        return app_settings

    @staticmethod
    def get(key, default=None):
        key = key.lower()
        return renderutil.get_value_by_path(AppSetting.get_app_setting(),
                                            key,
                                            default)

    def clean(self):
        try:
            if self.value_type == AppSetting.INT_TYPE:
                int(self.value)
            elif self.value_type == AppSetting.FLOAT_TYPE:
                float(self.value)
            elif self.value_type == AppSetting.JSON_TYPE:
                json.loads(self.value)
        except ValueError:
            raise ValidationError('配置项值跟类型不匹配')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(AppSetting, self).save(force_insert, force_update, using, update_fields)
        AppSetting.get_app_setting(True)

    class Meta:
        verbose_name_plural = verbose_name = '系统设置'
