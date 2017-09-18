# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals
from django.db import models
from tms import settings
import os
import datetime
from PIL import Image
from django.utils import timezone
from django.utils.functional import cached_property
import urlparse
from django.utils.safestring import mark_safe

'''
RELATED_FIELD = (
    (0, 'Unknown'),
    (1, 'Company Logo'),
    (2, 'Company Logo Thumbnail'),
)
'''
IMAGE_LARGE_SIZE = 600
IMAGE_MEDIUM_SIZE = 480
IMAGE_SMALL_SIZE = 320
IMAGE_THUMBNAIL_SIZE = 80

ABS_MEDIA_ROOT = os.path.abspath(settings.MEDIA_ROOT)
ABS_STATIC_ROOT = os.path.abspath(settings.STATIC_ROOT)


def make_thumb(path, size=32):
    """
    为给定图片创建缩略图
    :param path: 给定图片的完整路径
    :param size: 目标缩略图大小（宽度），默认为32px
    :return: 返回缩略图
    """
    try:
        pixbuf = Image.open(path)
        width, height = pixbuf.size

        # 仅当给定图片尺寸大于目标尺寸时才创建
        if width > size > 0:
            delta = width / size
            height = int(height / delta)
            pixbuf.thumbnail((size, height), Image.ANTIALIAS)
    except IOError:
        pixbuf = None
    return pixbuf


def check_thumb_url(image_path, size, path):
    """
    给定原图路径，检查并返回给定宽度缩略图对应的URL，如
    图片路径“MEDIA_ROOT/images/logo/test.png”，size=64， path="images/logo/test.png"
    api会检查图片是否存在，如果不存在则检查原图是否存在，存在则自动生成相应size宽度的缩略图，并返回有效url
    （如上述的样例中，最终返回的url路径为“/images/thumb/64/logo/test.png”）
    :param image_path: 原图路径
    :param size: 期望的缩略图宽度尺寸，高度按等比例缩放
    :param path: 图片路径
    :return:
    """
    if not os.path.abspath(image_path).startswith(ABS_MEDIA_ROOT) \
            or not os.path.isfile(image_path):
        # TODO: invalid path given (out of MEDIA_ROOT) or file not exists, must be log for security audit
        return ''

    thumb_path = '%sthumb/%s/%s' % (settings.MEDIA_ROOT, size, path)
    thumb_url = '%sthumb/%s/%s' % (settings.MEDIA_URL, size, path)
    if not os.path.isfile(thumb_path) or os.path.getmtime(thumb_path) < os.path.getmtime(image_path):
        thumb_dir, thumb_name = os.path.split(thumb_path)
        os.path.exists(thumb_dir) or os.makedirs(thumb_dir, mode=0744)
        image = make_thumb(image_path, int(size))
        if image:
            image.save(thumb_path)

    return thumb_url


# Create your models here.
# 管理员上传图片
# 如果需要缩略图，则自动生成几种特定规格的图片
# 缩略图保存在origin字段指定路径下的thumb/<width>/子目录中，图片文件名保持不变
# 缩略图创建请求将发到一个任务队列进行处理,考虑第一次请求时创建
class BaseImage(models.Model):
    origin = models.ImageField('原始图片', upload_to='%Y/%m/%d', max_length=200,
                               help_text=mark_safe('应尽量避免使用非英文字符命名的图片文件<br>'
                                                   '头图最佳1200像素-660像素，其次600像素-330像素，宽高比16:9'))
    image_desc = models.CharField('图片描述', max_length=50, null=True, blank=True)
    width = models.PositiveIntegerField('图片宽度', editable=False, null=True, blank=True)
    height = models.PositiveIntegerField('图片高度', editable=False, null=True, blank=True)
    size = models.PositiveIntegerField('文件大小', editable=False, null=True, blank=True)
    USAGE_COMMON = 0
    USAGE_LOGO = 1
    USAGE_AVATAR = 2
    USAGE_BANNER = 3
    USAGE_ICON = 4
    USAGE_EXPRESS_TEMPLATE = 11
    USAGES = (
        (USAGE_COMMON, "通用"),
        (USAGE_LOGO, "Logo"),
        (USAGE_AVATAR, "头像"),
        (USAGE_BANNER, "横幅Banner"),
        (USAGE_ICON, "图标"),
        (USAGE_EXPRESS_TEMPLATE, "快递单模板"),
    )
    usage = models.SmallIntegerField("用途(开发使用)", default=0, choices=USAGES)
    upload_time = models.DateTimeField('上传时间', auto_now_add=True, db_index=True, null=True, blank=True)

    def thumb(self):
        return '<img src="%s" />' % self.thumbnail

    thumb.allow_tags = True
    thumb.short_description = "缩略图"

    def __unicode__(self):
        return self.origin.url

    # def dimension(self):
    #     return '%s x %s' % (self.width, self.height) if self.width and self.height else '-'
    # dimension.short_description = '尺寸（宽x高）'

    @cached_property
    def thumbnail(self):
        """
        返回默认规格的缩略图
        """
        # return self.get_thumbnail(IMAGE_THUMBNAIL_SIZE)
        img_url = self.origin.url
        if img_url:
            url_res = urlparse.urlparse(img_url)
            if url_res.hostname in settings.QINIU_DOMAINS and img_url[-6:] != '-thumb':
                return '%s-thumb' % img_url  # 使用七牛的配置来创建缩略图

        return img_url

    @cached_property
    def large(self):
        """
        返回默认规格的缩略图
        """
        return self.get_thumbnail(IMAGE_LARGE_SIZE)

    @cached_property
    def medium(self):
        """
        返回默认规格的缩略图
        """
        return self.get_thumbnail(IMAGE_MEDIUM_SIZE)

    @cached_property
    def small(self):
        """
        返回默认规格的缩略图
        """
        return self.get_thumbnail(IMAGE_SMALL_SIZE)

    def get_thumbnail(self, size):
        """
        获取指定规格的缩略图
        :param size: 图片宽度，高度按图片比例自动调整
        :return: 返回给定大小的缩略图
        """
        return self.origin.url
        # if size and self.width and size > self.width:
        #     return self.origin.url
        #
        # return check_thumb_url(self.origin.path, size, self.origin.name)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        try:
            self.size = self.origin.size
            self.height = self.origin.height
            self.width = self.origin.width
        except:
            self.size = 0
        self.image_desc = self.image_desc or self.origin.name
        if not self.upload_time:
            self.upload_time = timezone.now() if settings.USE_TZ else datetime.datetime.now()
        #self._thumbnail = {}  # need to reset the thumbnail
        super(BaseImage, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name_plural = verbose_name = '图片'
        ordering = ['id']

