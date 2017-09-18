# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib import messages

from credit.models import CreditBook, RankSeries, RankTitle, MedalCatalog, UserMedal, UserTitle
from profile.models import EndUser
from util.renderutil import get_fields_list


__author__ = 'Winsom'

#
# def charge_back(model_admin, request, queryset):
#     cnt = 0
#     for item in queryset:
#         item.charge_back()
#         model_admin.log_change(request, item, u'撤销')
#         cnt += 1
#
#     model_admin.message_user(request, '已撤销%s笔资金流水' % cnt, messages.INFO)
#
# charge_back.short_description = '【撤销】选中的资金流水'


class CreditBookAdmin(admin.ModelAdmin):
    list_display = ['user', 'figure', 'source', 'is_income', 'create_time']
    fields = readonly_fields = get_fields_list(CreditBook)
    # readonly_fields.append('user')

    list_filter = ['is_income', ]
    search_fields = ['uid', 'source', 'extra_data']
    list_per_page = 20

    def user(self, obj):
        try:
            user = EndUser.objects.get(uid=obj.uid)
            return "%s / %s" % (user.real_name or '-', user.nick_name or user.ex_nick_name or '-')
        except:
            return 'N/A'

    user.short_description = u'用户'

    # actions = [charge_back]

    # def get_actions(self, request):
    #     actions = super(UserAccountBookAdmin, self).get_actions(request)
    #     if 'delete_selected' in actions:
    #         del actions['delete_selected']
    #     if not request.user.is_superuser:
    #         del actions['charge_back']
    #     return actions

    def save_model(self, request, obj, form, change):
        self.message_user(request, '积分不能编辑！', messages.WARNING)

    def has_delete_permission(self, request, obj=None):
        return False

    # def has_add_permission(self, request, obj=None):
    #     return False


class MedalCatalogAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'threshold', 'thumbnail', 'thumbnail2', 'remark', 'list_order']
    list_editable = ['list_order']
    search_fields = ['code', 'name']
    raw_id_fields = ['image', 'image2']
    fields = ['code', 'name', 'threshold', 'thumbnail', 'image', 'thumbnail2', 'image2', 'remark',
              'create_by', 'create_time', 'update_by', 'update_time']
    readonly_fields = ['thumbnail', 'thumbnail2', 'create_by', 'create_time', 'update_by', 'update_time']

    def thumbnail(self, obj):
        """
        返回默认规格的缩略图
        """
        return '<img src="%s">' % obj.image.thumbnail if obj else ""

    thumbnail.allow_tags = True
    thumbnail.short_description = u'勋章（激活）'

    def thumbnail2(self, obj):
        """
        返回默认规格的缩略图
        """
        return '<img src="%s">' % obj.image2.thumbnail if obj and obj.image2 else ""

    thumbnail2.allow_tags = True
    thumbnail2.short_description = u'勋章（未激活）'

    def save_model(self, request, obj, form, change):
        if not obj.create_by:
            obj.create_by = request.user.username

        obj.update_by = request.user.username
        super(MedalCatalogAdmin, self).save_model(request, obj, form, change)


class RankTitleInline(admin.TabularInline):
    model = RankTitle
    list_editable = list_display = ['name', 'left_value', 'right_value', 'image']
    raw_id_fields = ['image']
    extra = 1


class RankSeriesAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    inlines = [RankTitleInline]
    readonly_fields = ['create_by', 'update_by']

    def save_model(self, request, obj, form, change):
        if not obj.create_by:
            obj.create_by = request.user.username

        obj.update_by = request.user.username
        super(RankSeriesAdmin, self).save_model(request, obj, form, change)


# class UserMedalAdmin(admin.ModelAdmin):
#     list_display = ['user', 'figure', 'source', 'is_income', 'create_time']
#     # fields = readonly_fields = get_fields_list(CreditBook)
#     # readonly_fields.append('user')
#
#     list_filter = ['is_income', ]
#     search_fields = ['uid', 'source', 'extra_data']
#     list_per_page = 20
#
#     def user(self, obj):
#         try:
#             user = EndUser.objects.get(uid=obj.uid)
#             return "%s / %s" % (user.real_name or '-', user.nick_name or user.ex_nick_name or '-')
#         except:
#             return 'N/A'
#
#     user.short_description = u'用户'

class UserMedalAdmin(admin.ModelAdmin):
    list_display = ['uid', 'user', 'medal', 'thumbnail', 'grant_time']
    search_fields = ['uid']
    list_filter = ['medal']
    readonly_fields = list_display

    def user(self, obj):
        try:
            user = EndUser.objects.get(uid=obj.uid)
            return "%s / %s" % (user.real_name or '-', user.nick_name or user.ex_nick_name or '-')
        except:
            return 'N/A'

    user.short_description = u'用户'

    def thumbnail(self, obj):
        """
        返回默认规格的缩略图
        """
        return '<img src="%s">' % obj.medal.image.thumbnail if obj else ""

    thumbnail.allow_tags = True
    thumbnail.short_description = u'已激活的勋章'


class UserTitleAdmin(admin.ModelAdmin):
    list_display = ['uid', 'user', 'series', 'user_title', 'update_time']
    search_fields = ['uid']
    readonly_fields = list_display

    def user(self, obj):
        try:
            user = EndUser.objects.get(uid=obj.uid)
            return "%s / %s" % (user.real_name or '-', user.nick_name or user.ex_nick_name or '-')
        except:
            return 'N/A'

    user.short_description = u'用户'

    def user_title(self, obj):
        if not obj:
            return '-'
        summary = CreditBook.get_credit_summary(obj.uid)
        title = CreditBook.get_user_title(obj.uid, summary['income'])
        return title['rank_title']

    user_title.short_description = u'用户当前级别'

admin.site.register(CreditBook, CreditBookAdmin)
admin.site.register(RankSeries, RankSeriesAdmin)
admin.site.register(MedalCatalog, MedalCatalogAdmin)
admin.site.register(UserMedal, UserMedalAdmin)
admin.site.register(UserTitle, UserTitleAdmin)

