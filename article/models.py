# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime

from django.db import models
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError

from filemgmt.models import BaseImage
from ueditor.models import UEditorField
from django.utils.safestring import mark_safe


class ArticleCategory(models.Model):
    name = models.CharField('类别名称', null=False, blank=False, max_length=32)
    memo = models.CharField('类别说明', max_length=255, null=True, blank=True)
    parent = models.ForeignKey('self', verbose_name='上级类别', null=True, blank=True, related_name='children',
                               on_delete=models.CASCADE, help_text='上级类别，当上级被删除时，下属关联类别将一并删除')
    list_order = models.PositiveIntegerField('排序标记', default=0, help_text='数值越大，排序越靠前')
    path = models.CharField('路径（用于加速查询）', max_length=255, null=True, blank=True,
                            help_text='包含上级编码id及自身id，类似"1,2,3"', db_index=True)

    def __unicode__(self):
        return "%s -> %s" % (self.parent.__unicode__(), self.name) if self.parent_id else self.name

    def clean(self):
        if self.parent and self.parent.path and str(self.pk) in self.parent.path.split(','):
            raise ValidationError('禁止循环引用（当前类别已是要设定的上级类别的上级）！')

    def get_children(self, all=True):
        if all:
            return self.children.all()
        else:
            path = '%s%s,' % (self.path if self.parent_id else '', self.pk)
            descendants = ArticleCategory.objects.filter(path__istartswith=path)
            return descendants

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
        文章保存后自动更新path，形如"<pk>," 或 "<parent_path>,<pk>," (注意末位保留英文逗号“,”)
        :param force_insert:
        :param force_update:
        :param using:
        :param update_fields:
        :return:
        """
        self.path = ("%s%s," % (self.parent.path or '', self.parent.pk)) if self.parent_id else None
        if not self.pk:
            # save first to get the pk
            super(ArticleCategory, self).save(force_insert, force_update, using, update_fields)
            # self.path = "%s%s," % (self.parent.path if self.parent_id else '', self.pk)
            # super(ArticleCategory, self).save(using=using, update_fields=['path'])
        else:
            # path = "%s%s," % (self.parent.path if self.parent_id else '', self.pk)
            # if not self.path or self.path != path:
            #     self.path = path
            super(ArticleCategory, self).save(force_insert, force_update, using, update_fields)
            # 递归更新子类别的路径
            children = self.children.all()
            for child in children:
                # child.path = "%s%s," % (self.path, child.pk)
                child.save()

    class Meta:
        ordering = ['path', '-list_order', 'name']
        verbose_name_plural = verbose_name = '文章分类'


class Article(models.Model):
    subject = models.CharField('文章主题', default='文章主题', max_length=20, null=False, blank=False)
    subject_image = models.ForeignKey(BaseImage, verbose_name='主题图片', related_name='discovery_subject_image+',
                                      null=True, blank=True,
                                      help_text='建议使用宽度为不超过600像素的图片，高度根据需要酌情设计')
    content_image = models.ForeignKey(BaseImage, verbose_name='内容图片', related_name='discovery_content_image+',
                                      null=True, blank=True, help_text='查看文章的详情时显示，默认与主题图片相同')
    category = models.ForeignKey(ArticleCategory, verbose_name="类别", null=True, blank=True)
    tags = models.CharField("文章Tag", max_length=255, db_index=True, null=True, blank=True,
                            help_text='用于文章搜索，每个标签之间应使用英文逗号","分隔，标签为精确匹配')
    brief = models.CharField("简介", max_length=500, null=True, blank=True,
                             help_text='文章简介，一般用于文章列表显示摘要')
    content = UEditorField('内容描述', max_length=200000, null=True, blank=True, width=900, height=600,
                           help_text='注意：建议使用不超过800像素宽度的图片。'
                                     '除非明确知道设置图片大小的目的，否则请不要指定图片大小，由页面自动缩放')
    link_to = models.CharField('目标地址', max_length=100, null=True, blank=True,
                               help_text='即用户点击该主题图片后，打开的外链地址（默认在商城中打开，无需配置）')
    list_order = models.PositiveIntegerField('显示顺序(大的在前)', default=0, null=True, blank=True, db_index=True)
    publish_date = models.DateTimeField('发布时间', null=True, blank=True, default=datetime.datetime.now,
                                        help_text='只有生效时间后的文章才会展示')
    is_active = models.BooleanField("是否有效", default=False, null=False, blank=False)
    product_tags = models.CharField("关联对象表达式", max_length=1024, db_index=True, null=True, blank=True,
                                    help_text=mark_safe('用于文章与关联对象（如商品、优惠活动等）匹配搜索。<br>'
                                                        '格式为"<关联属性>:<关联值>"，可以有多个，中间使用英文逗号","分隔，不同属性用英文";"分隔。<br>'
                                                        '关联属性可以是商品名称、类别、Tag、品牌、产地、供应商中的一种或几种，或者是活动（对应优惠活动编码）。<br>'
                                                        '如：<br>'
                                                        '  - "名称:月饼;类别:食品;Tag:中秋,礼品,烘培食品;品牌:利男居;产地:上海;供应商:TWOHOU-02"<br>'
                                                        '  - "活动:A-160816-TKB"'))
    # 预留，当文章需要审核时使用
    review_date = models.DateTimeField('审核时间', null=True, blank=True, editable=False,
                                       help_text='预留，当用户文章需要被审核时使用')
    review_by = models.CharField('审核人', max_length=36, blank=True, null=True, editable=False)
    # 以下字段信息用于排序、筛选及安全审计
    revision = models.PositiveSmallIntegerField('版本', default=1, null=True, blank=True, editable=False,
                                                help_text='每次保存，版本号自动加1')
    create_time = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True, editable=False)
    create_by = models.CharField('创建人', max_length=36, blank=True, null=True, editable=False)
    update_time = models.DateTimeField('更新时间', auto_now=True, blank=True, null=True, editable=False)
    update_by = models.CharField('更新人', max_length=36, blank=True, null=True, editable=False)

    def clean(self):
        if self.tags:
            self.tags = self.tags.replace('，', ',')
        if self.product_tags:
            self.product_tags = self.product_tags.replace('，', ',').replace('：', ':').replace('；', ';')

    def to_dict(self, detail=False):
        if detail:
            res = model_to_dict(self, exclude=('content_image', ))
            res['content_image'] = self.content_image.large if self.content_image else ''
        else:
            res = model_to_dict(self, fields=('id', 'subject', 'brief',  'tags', 'link_to',
                                              'publish_date', 'product_tags', 'list_order'))
        res['category_id'] = self.category_id
        res['category_txt'] = self.category.name if self.category_id else ''
        res['subject_image'] = self.subject_image.large if self.subject_image else ''
        res['create_by'] = self.create_by
        res['update_time'] = self.update_time
        return res

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.revision += 1
        super(Article, self).save(force_insert, force_update, using, update_fields)

    def __unicode__(self):
        return "%s" % self.subject

    class Meta:
        ordering = ('-list_order', '-update_time')
        verbose_name_plural = verbose_name = '文章'

