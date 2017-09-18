# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import Article, ArticleCategory
from tms import settings
from django.core.urlresolvers import reverse


class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'article_cnt', 'parent', 'list_order', 'memo', ]  # 'path'
    list_editable = ['list_order']
    search_fields = ['name']
    readonly_fields = ['path', 'article_cnt', ]

    def article_cnt(self, obj):
        """
        返回该类文章数
        """
        if not obj:
            return 0
        cnt = Article.objects.filter(category_id=obj.pk).count()
        if cnt == 0:
            return 0
        else:
            return '%s (<a href="%s?category__id__exact=%s">查看</a>)' % (cnt, reverse('admin:article_article_changelist'), obj.pk)

    article_cnt.allow_tags = True
    article_cnt.short_description = '文章数'


class ArticleAdmin(admin.ModelAdmin):
    list_display = ['subject', 'thumb', 'category', 'tags', 'list_order', 'publish_date', 'is_active', 'create_by']
    list_editable = ['list_order', 'publish_date', 'is_active']
    raw_id_fields = ['subject_image', 'content_image', ]
    search_fields = ['subject', 'tags', 'brief', ]
    list_filter = ['category', 'publish_date', 'is_active']
    date_hierarchy = 'publish_date'

    # inlines = [ArticleProductTabInline, ]

    def thumb(self, obj):
        """
        返回默认规格的缩略图
        """
        return ("<img src='%s'>" % obj.subject_image.thumbnail) if obj.subject_image else '-'

    thumb.allow_tags = True
    thumb.short_description = '主题图片'

    def get_view_on_site_url(self, obj=None):
        return ('%s/tms-api/admin/preview/article/%s' % (settings.APP_URL, obj.pk)) if obj else None

    def save_model(self, request, obj, form, change):
        obj.create_by = obj.create_by or request.user.username
        obj.update_by = obj.update_by or request.user.username
        super(ArticleAdmin, self).save_model(request, obj, form, change)
        if not obj.is_active or not obj.publish_date:
            self.message_user(request, '本文尚未发布，用户暂不可见。如需发布，请填写发布时间并选中“是否有效”')
    # class Media:
    #     js = [settings.STATIC_URL+'tiny_mce/tiny_mce.js', settings.STATIC_URL+'js/textareas.js',]


admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleCategory, ArticleCategoryAdmin)