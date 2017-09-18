# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib import messages
from .models import ApiAuth, Banner, AppSetting, District
from django.forms.widgets import Textarea


def clone_navilink(model_admin, request, queryset):
    for navilink in queryset:
        t = navilink.clone()
        model_admin.log_change(request, t, u'克隆自%s(id: %s)' % (navilink.subject, navilink.id))
        model_admin.message_user(request, u"已克隆%s(id: %s)为(id: %s)" % (navilink.subject, navilink.id, t.id), messages.INFO)


clone_navilink.short_description = '【克隆】选中的导航项'


class BannerAdmin(admin.ModelAdmin):
    list_display = ['thumb', 'scenario', 'subject', 'link_to', 'list_order', 'effective_date', 'is_active']
    list_editable = ['subject', 'link_to', 'list_order', 'effective_date', 'is_active']
    raw_id_fields = ['image', ]
    list_filter = ['scenario', 'is_active']
    # readonly_fields = ['dimension', ]
    actions = [clone_navilink]

    def thumb(self, obj):
        """
        返回默认规格的缩略图
        """
        return "<img src='%s'>" % obj.image.thumbnail

    thumb.allow_tags = True
    thumb.short_description = '缩略图'

    # def dimension(self, obj):
    #     return obj.image.dimension()
    #
    # dimension.allow_tags = False
    # dimension.short_description = "图片尺寸"
    def save_model(self, request, obj, form, change):
        obj.create_by = obj.create_by or request.user.id
        obj.update_by = obj.update_by or request.user.id
        super(BannerAdmin, self).save_model(request, obj, form, change)


# class ChannelProductTabInline(admin.TabularInline):
#     model = ChannelProduct
#     fields = ['product', 'icon', 'item_code', 'item_name', ]
#     extra = 3
#     raw_id_fields = ['product']
#     readonly_fields = ['item_code', 'item_name', 'icon', ]
#     can_delete = True
#
#     def icon(self, obj):
#         """
#         返回默认规格的缩略图
#         """
#         icon = obj.product.icon
#         return '<img src="%s">' % icon if icon else ""
#
#     icon.allow_tags = True
#     icon.short_description = '缩略图'
#
#     def item_code(self, obj):
#         return obj.product.code
#
#     item_code.allow_tags = False
#     item_code.short_description = "商品编码"
#
#     def item_name(self, obj):
#         return obj.product.name
#
#     item_name.allow_tags = False
#     item_name.short_description = "商品名称"
#
#
# class ChannelAdmin(admin.ModelAdmin):
#     list_display = ['thumb', 'scenario', 'subject', 'link_to', 'list_order', 'is_active', ]
#     list_editable = ['subject', 'link_to', 'list_order', 'is_active', ]
#     list_filter = ['scenario', 'is_active']
#     readonly_fields = []
#     raw_id_fields = ['image', ]
#     inlines = [ChannelProductTabInline, ]
#
#     def thumb(self, obj):
#         """
#         返回默认规格的缩略图
#         """
#         return "<img src='%s'>" % obj.image.thumbnail
#
#     thumb.allow_tags = True
#     thumb.short_description = '频道缩略图'
#
#     # def dimension(self, obj):
#     #     return obj.image.dimension()
#     #
#     # dimension.allow_tags = False
#     # dimension.short_description = "图片尺寸"


# class ArticleProductTabInline(admin.TabularInline):
#     model = ArticleProduct
#     fields = ['product', 'item_code', 'item_name', ]
#     extra = 3
#     raw_id_fields = ['product']
#     readonly_fields = ['item_code', 'item_name', ]
#     can_delete = True
#
#     def item_code(self, obj):
#         return obj.product.code
#
#     item_code.allow_tags = False
#     item_code.short_description = "商品编码"
#
#     def item_name(self, obj):
#         return obj.product.name
#
#     item_name.allow_tags = False
#     item_name.short_description = "商品名称"
#
#
# class ArticleAdmin(admin.ModelAdmin):
#     list_display = ['subject', 'thumb', 'tags', 'link_to', 'list_order', 'effective_date', 'is_active']
#     list_editable = ['link_to', 'list_order', 'effective_date', 'is_active']
#     raw_id_fields = ['subject_image', 'content_image', ]
#     # inlines = [ArticleProductTabInline, ]
#
#     def thumb(self, obj):
#         """
#         返回默认规格的缩略图
#         """
#         return "<img src='%s'>" % obj.subject_image.thumbnail
#
#     thumb.allow_tags = True
#     thumb.short_description = '主题图片'
#
#     def save_model(self, request, obj, form, change):
#         obj.create_by = obj.create_by or request.user.id
#         obj.update_by = obj.update_by or request.user.id
#         super(ArticleAdmin, self).save_model(request, obj, form, change)
#     # class Media:
#     #     js = [settings.STATIC_URL+'tiny_mce/tiny_mce.js', settings.STATIC_URL+'js/textareas.js',]
#
#
# class ChannelProductAdmin(admin.ModelAdmin):
#     list_display = ['channel', 'product', 'list_order', ]
#     list_editable = ['product', 'list_order', ]
#     list_filter = ['channel', 'product__supplier', 'product__origin_province']
#     raw_id_fields = ['product', ]
#     search_fields = ['product__name', 'product__code']
#
#
# class ArticleProductAdmin(admin.ModelAdmin):
#     list_display = ['article', 'product', 'list_order', ]
#     list_editable = ['product', 'list_order', ]
#     list_filter = ['article', 'product__supplier', 'product__origin_province']
#     raw_id_fields = ['product', ]
#     search_fields = ['product__name', 'product__code']


class ApiAuthAdmin(admin.ModelAdmin):
    list_display = ['grant_to', 'visitor_code', 'api_list', 'ip_list', 'grant_by', 'update_time']
    list_editable = ['api_list', 'ip_list']
    readonly_fields = ['create_time', 'update_time', 'grant_by', ]

    def save_model(self, request, obj, form, change):
        obj.grant_by = request.user
        super(ApiAuthAdmin, self).save_model(request, obj, form, change)


class AppSettingAdmin(admin.ModelAdmin):
    list_display = ['refer_key', 'category', 'usage', 'value_type', 'value']
    list_editable = ['value']
    readonly_fields = ['refer_key']
    list_filter = ['category', 'value_type']
    search_fields = ['name', 'usage']

    def refer_key(self, obj):
        return "%s.%s" % (obj.category, obj.name)

    refer_key.short_description = '引用键值'
    refer_key.admin_order_field = 'name'

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'usage':
            kwargs['widget'] = Textarea(attrs={'rows': 3, 'cols': 60})
            try:
                del kwargs['request']
            except KeyError:
                pass
            return db_field.formfield(**kwargs)
        return super(AppSettingAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'up', 'pinyin', 'pinyin_abbr', 'list_order']
    list_editable = ['list_order']
    search_fields = ['name', 'pinyin', 'pinyin_abbr']
    list_filter = ['level']
    save_on_top = True


admin.site.register(Banner, BannerAdmin)
# admin.site.register(Channel, ChannelAdmin)
# admin.site.register(Article, ArticleAdmin)
# admin.site.register(ChannelProduct, ChannelProductAdmin)
# admin.site.register(ArticleProduct, ArticleProductAdmin)
admin.site.register(AppSetting, AppSettingAdmin)
admin.site.register(ApiAuth, ApiAuthAdmin)
admin.site.register(District, DistrictAdmin)
