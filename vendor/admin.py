# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.utils import html
from tms.admin import store_site
from vendor.models import Supplier, SupplierManager, SupplierNotice, LogisticsVendor, Manufacturer, \
    Contact, SupplierSalesIncome, Brand, Hotel, HotelImage, SalesAgent
from util.renderutil import get_fields_list
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import F, Q
from tms import Convert, settings
import urllib
from django.utils import safestring
from django.forms.widgets import Textarea


class StoreAgentAdmin(admin.ModelAdmin):
    list_display = ['user', 'username', 'store', ]
    raw_id_fields = ['user']
    search_fields = ['user__username', 'store__code', 'store__name']

    def username(self, obj):
        return obj.user.get_full_name()

    username.short_description = u'姓名'


class VendorAdmin(admin.ModelAdmin):
    list_display = ['code', 'id', 'logo_icon', 'link_name', 'p_contact', 'is_active', ]
    list_editable = ['is_active', ]
    raw_id_fields = ['logo', 'primary_contact', 'backup_contact', ]
    search_fields = ['name', 'code', ]
    list_filter = ['is_active', 'province']
    readonly_fields = ['p_contact', 'link_name', 'logo_icon']

    fieldsets = (
        (None, {'fields': ('code', 'name', 'primary_contact', 'is_active', )}),
        ('介绍', {'fields': ('homepage', 'logo', 'backup_contact', 'intro', ),
                'classes': ['collapse']}),
        ('地址', {'fields': (('province', 'city', ), ('address', 'post_code', ), ),
                'classes': ['collapse']}),
    )

    def get_readonly_fields(self, request, obj=None):
        fields = ['p_contact', 'link_name', 'logo_icon']
        if obj:
            fields.append('code')
        return fields

    def logo_icon(self, obj):
        """
        返回默认规格的缩略图
        """
        return '<img src="%s">' % obj.logo.thumbnail if obj.logo else "无"

    logo_icon.allow_tags = True
    logo_icon.short_description = u'LOGO'

    def link_name(self, obj):
        if obj.homepage:
            return u'%s （<a target="_blank" href="%s">主页</a>）' % (html.escape(obj.name), html.escape(obj.homepage))
        else:
            return html.escape(obj.name)

    link_name.allow_tags = True
    link_name.short_description = u"名称"
    link_name.admin_order_field = 'name'

    def p_contact(self, obj):
        res = []
        if obj.primary_contact_id:
            res = [html.escape(obj.primary_contact.name),
                   "电话：%s" % html.escape(obj.primary_contact.mobile or ''),
                   "微信号：%s" % html.escape(obj.primary_contact.wechat or '')]
        return "<br>".join(res)

    p_contact.allow_tags = True
    p_contact.short_description = u"主联系人"


# class StoreAgentInline(admin.TabularInline):
#     model = StoreAgent
#     fk_name = 'store'
#     raw_id_fields = ['user']
#     fields = ['user', 'fullname', ]
#     readonly_fields = ['fullname', ]
#
#     def fullname(self, obj):
#         return obj.user.get_full_name()
#
#     fullname.short_description = '姓名'


class StoreAdmin(VendorAdmin):
    list_display = ['code', 'name', 'link_home', 'primary_contact', 'backup_contact', 'is_active', ]
    list_editable = ['is_active', ]
    # inlines = [StoreAgentInline]


# class LogisticVendorAdmin(VendorAdmin):
#     list_display = ['name', 'code', 'link_home', 'primary_contact', 'backup_contact', ]
#     list_editable = ['is_active',]

class SupplierManagerInline(admin.TabularInline):
    model = SupplierManager
    fk_name = 'supplier'
    raw_id_fields = ['user']
    fields = ['user', 'fullname', 'has_binded', 'binded', ]
    readonly_fields = ['fullname', 'has_binded', 'binded', ]
    extra = 1

    def fullname(self, obj):
        return obj.user.get_full_name()

    fullname.short_description = u'姓名'

    def has_binded(self, obj):
        from profile.models import EndUserExt
        return EndUserExt.objects.filter(ex_id=obj.user, ex_id_type=EndUserExt.ID_TYPE_INTERNAL).exists()

    has_binded.short_description = u'是否绑定'
    has_binded.boolean = True

    def binded(self, obj):
        from profile.models import EndUserExt
        res = EndUserExt.objects.filter(ex_id=obj.user, ex_id_type=EndUserExt.ID_TYPE_INTERNAL)\
            .values_list('uid', flat=True)
        return "<br>".join(res)

    binded.short_description = u'关联UID'
    binded.allow_tags = True


class SupplierManagerAdmin(admin.ModelAdmin):
    list_display = ['supplier', 'user', 'has_binded', 'binded', ]
    search_fields = ['supplier__name', 'supplier__code', 'user__username']
    raw_id_fields = ['user', 'supplier']
    fields = ['supplier', 'user', 'fullname', 'has_binded', 'binded', ]
    readonly_fields = ['fullname', 'has_binded', 'binded', ]
    actions = ['delete_selected']

    def fullname(self, obj):
        return obj.user.get_full_name()

    fullname.short_description = u'姓名'

    def has_binded(self, obj):
        from profile.models import EndUserExt
        return EndUserExt.objects.filter(ex_id=obj.user, ex_id_type=EndUserExt.ID_TYPE_INTERNAL).exists()

    has_binded.short_description = u'是否绑定'
    has_binded.boolean = True
    # has_binded.admin_order_field = ''

    def binded(self, obj):
        from profile.models import EndUserExt
        res = EndUserExt.objects.filter(ex_id=obj.user, ex_id_type=EndUserExt.ID_TYPE_INTERNAL)\
            .values_list('uid', flat=True)
        return "<br>".join(res)

    binded.short_description = u'关联UID'
    binded.allow_tags = True


class SupplierAdmin(VendorAdmin):
    inlines = [SupplierManagerInline]

    fieldsets = (
        (None, {'fields': ('id', 'code', 'name', 'primary_contact', 'capital_accounts', 'settlement', 'is_active', )}),
        (u'介绍', {'fields': ('homepage', 'logo', 'backup_contact', 'intro', ),
                'classes': ['collapse']}),
        (u'地址', {'fields': (('province', 'city', ), ('address', 'post_code', ), ),
                'classes': ['collapse']}),
    )

    def get_readonly_fields(self, request, obj=None):
        fields = super(SupplierAdmin, self).get_readonly_fields(request, obj)
        fields.append('capital_accounts')
        fields.append('id')
        return fields

    def capital_accounts(self, obj):
        accounts = ["%s (<a href='#' onclick='unbind_account(%s, %s)'>解绑</a>)" % (unicode(acct), obj.id, acct.id) for acct in obj.capital_accounts]
        accounts = accounts or ['未登记']
        link = reverse('admin:profile_usercapitalaccount_add')
        accounts.append("(<a href='%s'>绑定新账号</a>)" % link)
        return "<br>".join(accounts) if accounts else '未登记'

    capital_accounts.short_description = '资金账号'
    capital_accounts.allow_tags = True

    # def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
    #     if db_field.name == "capital_account":
    #         kwargs['queryset'] = UserCapitalAccount.objects.none()
    #     return super(SupplierAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    class Media:
        js = [settings.STATIC_URL+'js/capital_account.js',]


class SupplierNoticeAdmin(admin.ModelAdmin):
    list_display = ['supplier', 'content', 'effective_time', 'expire_time']
    # raw_id_fields = ['supplier']
    readonly_fields = ['create_by', 'update_by']
    date_hierarchy = 'effective_time'
    list_filter = ['effective_time', 'expire_time', ]
    search_fields = ['supplier__name']

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'content':
            kwargs['widget'] = Textarea(attrs={'rows': 3, 'cols': 60})
            try:
                del kwargs['request']
            except KeyError:
                pass
            return db_field.formfield(**kwargs)
        return super(SupplierNoticeAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "supplier":
            if not request.user.is_superuser and request.user.has_perm('basedata.as_supplier'):
                kwargs['queryset'] = Supplier.objects.filter(suppliermanager__user=request.user).order_by(
                    Convert(F('name')))
            else:
                kwargs['queryset'] = Supplier.objects.order_by(Convert(F('name')))

        return super(SupplierNoticeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super(SupplierNoticeAdmin, self).get_queryset(request)
        if request.user.is_superuser or request.user.has_perm('basedata.can_manage_product'):
            return qs
        elif request.user.has_perm('basedata.as_supplier'):
            mgrs = SupplierManager.objects.filter(user=request.user).values_list('supplier_id', flat=True)
            # suppliers = [mgr.supplier_id for mgr in mgrs]
            # return qs.filter(supplier_id__in=suppliers)
            return qs.filter(supplier_id__in=mgrs)
        else:
            return qs.none()

    def save_model(self, request, obj, form, change):
        obj.create_by = obj.create_by or request.user.username
        obj.update_by = request.user.username
        super(SupplierNoticeAdmin, self).save_model(request, obj, form, change)


class HotelImageInline(admin.TabularInline):
    model = HotelImage
    readonly_fields = ['thumb', ]  # 'dimension',
    # list_display = ['thumb', 'origin', 'image_desc', 'dimension', ]
    fields = ['origin', 'thumb', 'image_desc', 'list_order', ] # 'dimension',
    extra = 1
    can_delete = True


class HotelAdmin(VendorAdmin):
    inlines = [HotelImageInline]
    fieldsets = (
        (None, {'fields': ('code', 'name', 'primary_contact', 'phone', 'fax', 'is_active', )}),
        (u'介绍', {'fields': ('homepage', 'logo', 'backup_contact', 'tags', 'intro', ),
                 'classes': ['collapse']}),
        (u'预定', {'fields': ('link_to_book1', 'link_to_book2', ),
                 'classes': ['collapse']}),
        (u'地址', {'fields': (('province', 'city', ), ('address', 'post_code', ), ),
                 'classes': ['collapse']}),
    )

    def get_view_on_site_url(self, obj=None):
        return ('%s/tms-api/admin/preview/hotel/%s' % (settings.APP_URL, obj.pk)) if obj else None


class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'suppliers', 'mobile', 'wechat', 'email', 'phone', 'qq',]   #
    # list_editable = ['mobile', 'phone', 'qq', 'wechat', 'email']
    readonly_fields = ['suppliers']

    def suppliers(self, obj):
        related = []
        if obj:
            suppliers = Supplier.objects.filter(Q(primary_contact_id=obj.pk) | Q(backup_contact_id=obj.pk)).values_list('name', flat=True)
            if suppliers:
                related.extend(['%s（供应商）' % html.escape(s) for s in suppliers])
        return "<br>".join(related) if related else '-'

    suppliers.short_description = '关联商家'
    suppliers.allow_tags = True

    # class Media:
    #     css = {
    #         "all": (urllib.basejoin(settings.QINIU_URL, "/static/css/tms-forms.css"), )
    #     }


def settle_income(model_admin, request, queryset):
    cnt = 0
    for income in queryset:
        if income.status != SupplierSalesIncome.INCOME_TO_BE_SETTLED:
            model_admin.message_user(request,
                                     '%s收入[订单号: %s]不可结算' % (income.get_status_display(), income.order_no),
                                     messages.ERROR)
        else:
            try:
                income.charge()
                cnt += 1
                model_admin.log_change(request, income, u'收入结算')
            except Exception, e:
                model_admin.message_user(request, e.message, messages.ERROR)
    model_admin.message_user(request, u"成功结算%s笔收入" % cnt, messages.INFO)


settle_income.short_description = u'【结算】选中的收入'


def mark_question(model_admin, request, queryset):
    cnt = 0
    for income in queryset:
        if not income.has_doubt:
            income.has_doubt = True
            income.save()
            if income.account_no:
                income.charge_back()
            cnt += 1

    model_admin.message_user(request, u"已标记%s笔收入为有疑问" % cnt, messages.INFO)


mark_question.short_description = u'将选中的收入【标记为有疑问】'


def unmark_question(model_admin, request, queryset):
    cnt = 0
    for income in queryset:
        if income.has_doubt:
            income.has_doubt = False
            income.save()
            if income.status == SupplierSalesIncome.INCOME_SETTLED:
                income.charge()
            cnt += 1

    model_admin.message_user(request, u"已取消%s笔收入的疑问标记" % cnt, messages.INFO)


unmark_question.short_description = u'【取消】选中的收入的疑问标记'


class SupplierSalesIncomeAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'supplier', 'product_cost', 'ship_fee', 'adjust_fee',
                    'status', 'has_doubt', 'account_no', 'create_time', ]
    readonly_fields = fields = get_fields_list(SupplierSalesIncome)
    actions = [settle_income, mark_question, unmark_question]
    search_fields = ['order_no', 'account_no', ]
    list_filter = ['status', 'has_doubt', 'supplier']
    date_hierarchy = 'create_time'


class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'list_order']
    list_editable = ['list_order']
    search_fields = ['name', ]

    actions = ['delete_selected']

    def get_queryset(self, request):
        qs = super(BrandAdmin, self).get_queryset(request)
        return qs.order_by('-list_order').order_by(Convert(F('name')))

    def get_actions(self, request):
        actions = super(BrandAdmin, self).get_actions(request)
        if not request.user.is_superuser and 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        elif request.user.has_perm('basedata.as_supplier') and obj:
            mgrs = SupplierManager.objects.filter(user=request.user).values_list('supplier_id', flat=True)
            if obj.supplier_id in mgrs:
                return True

        return False

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

admin.site.register(Brand, BrandAdmin)
store_site.register(Brand, BrandAdmin)
admin.site.register(SalesAgent, VendorAdmin)
admin.site.register(SupplierSalesIncome, SupplierSalesIncomeAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(SupplierNotice, SupplierNoticeAdmin)
admin.site.register(Hotel, HotelAdmin)
# admin.site.register(Store, StoreAdmin)
admin.site.register(Manufacturer, VendorAdmin)
admin.site.register(LogisticsVendor, VendorAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(SupplierManager, SupplierManagerAdmin)
# admin.site.register(StoreAgent, StoreAgentAdmin)
store_site.register(LogisticsVendor)
store_site.register(Manufacturer)


