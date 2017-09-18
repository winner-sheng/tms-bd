# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

from django.db.models import Q
from django.contrib import admin
from django.contrib import messages

from .models import ExpressTemplate, ExpressSender, ShapeImage, ShipReport
from tms.admin import store_site
from filemgmt.admin import BaseImageAdmin
from tms.config import SHIP_STATUS_SIGNOFF

__author__ = 'Winsom'


class ExpressTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "update_time"]
    # list_editable = ["type",]
    # raw_id_fields = ['shape_image',]
    add_form_template = 'admin/logistic/edit_express_template.html'
    change_form_template = 'admin/logistic/edit_express_template.html'
    # def add_view(self, request, form_url='', extra_context=None):
    #     pass

    def get_readonly_fields(self, request, obj=None):
        if request.user and request.user.is_superuser:
            return []
        else:
            return ['type']

    def get_queryset(self, request):
        qs = super(ExpressTemplateAdmin, self).get_queryset(request)
        if request.user and request.user.is_superuser:
            return qs
        # TODO: simply set permission to creator
        return qs.filter(Q(create_by=request.user.id) | Q(type=ExpressTemplate.TYPE_PUBLIC))

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        templates = ExpressTemplate.objects.filter(Q(create_by=request.user.id)
                                                   | Q(type=ExpressTemplate.TYPE_PUBLIC))

        try:
            shape_images = ShapeImage.objects.filter(usage=ShapeImage.USAGE_EXPRESS_TEMPLATE)
        except ShapeImage.DoesNotExist:
            shape_images = []

        extra_context['templates'] = templates
        extra_context['shape_images'] = shape_images
        return super(ExpressTemplateAdmin, self).add_view(request, form_url,
                                                          extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        templates = ExpressTemplate.objects.filter(Q(create_by=request.user.id)
                                                   | Q(type=ExpressTemplate.TYPE_PUBLIC))
        shape_images = ShapeImage.objects.filter(usage=ShapeImage.USAGE_EXPRESS_TEMPLATE)
        extra_context['templates'] = templates
        extra_context['shape_images'] = shape_images
        return super(ExpressTemplateAdmin, self).change_view(request, object_id,
                                                             form_url, extra_context=extra_context)


class ShapeImageAdmin(BaseImageAdmin):
    def get_queryset(self, request):
        qs = super(ShapeImageAdmin, self).get_queryset(request)
        return qs.filter(usage=ShapeImage.USAGE_EXPRESS_TEMPLATE)


class InvoiceTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "update_time"]
    list_editable = ["type", ]
    save_as = True
    save_on_top = True

    # class Media:
    #     js = (settings.STATIC_URL+'tiny_mce/tiny_mce.js', settings.STATIC_URL+'js/textareas.js',)


class ExpressSenderAdmin(admin.ModelAdmin):
    list_display = ['name', 'mobile', 'phone', 'address', 'post_code', 'supplier']
    list_editable = ['mobile', 'phone', 'address', ]
    save_as = True
    save_on_top = True

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "supplier":
            if not request.user.is_superuser and request.user.has_perm('basedata.as_supplier'):
                from vendor.models import Supplier
                kwargs['queryset'] = Supplier.objects.filter(suppliermanager__user=request.user)
        return super(ExpressSenderAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super(ExpressSenderAdmin, self).get_queryset(request)
        if request.user.is_superuser or request.user.has_perm('basedata.can_manage_order'):
            return qs
        else:
            return qs.filter(supplier__suppliermanager__user=request.user)


admin.site.register(ExpressTemplate, ExpressTemplateAdmin)
# admin.site.register(InvoiceTemplate, InvoiceTemplateAdmin)
admin.site.register(ShapeImage, ShapeImageAdmin)
store_site.register(ShapeImage)
store_site.register(ExpressTemplate, ExpressTemplateAdmin)
admin.site.register(ExpressSender, ExpressSenderAdmin)
store_site.register(ExpressSender, ExpressSenderAdmin)


def refresh_report(model_admin, request, queryset):
    ok_cnt = failed = 0
    for report in queryset:
        if report.refresh():
            ok_cnt += 1
        else:
            failed += 1

    model_admin.message_user(request, "共成功刷新订阅[%s]条，失败[%s]条" % (ok_cnt, failed), messages.INFO)


refresh_report.short_description = '刷新物流信息'


class ShipReportAdmin(admin.ModelAdmin):
    list_display = ['package_no', 'ship_code', 'vendor_code', 'state', 'order_status', 'latest_status', 'update_time']
    readonly_fields = ['package_no', 'ship_code', 'vendor_code', 'state', 'order_status', 'latest_status', 'update_time',
                       'report', 'report_list']
    list_filter = ['vendor_code', 'state']
    search_fields = ['package_no', 'ship_code']

    fields = ['package_no', 'ship_code', 'vendor_code', 'state', 'latest_status', 'update_time', 'report_list']
    actions = [refresh_report, ]
    list_per_page = 20

    def order_status(self, obj):
        from basedata.models import Order
        try:
            order = Order.objects.get(order_no=obj.package_no)
            if order.order_state not in [Order.STATE_RECEIVED,
                                         Order.STATE_CUSTOMER_SERVICE,
                                         Order.STATE_RETURN,
                                         Order.STATE_REFUNDED] \
                    and obj.state == SHIP_STATUS_SIGNOFF:
                return "<span style='background:red;' title='订单状态不一致，请刷新物流信息'>%s</span>" \
                       % order.get_order_state_display()
            else:
                return order.get_order_state_display()
        except Order.DoesNotExist:
            return '[订单无效]'
    order_status.short_description = '订单状态'
    order_status.allow_tags = True

    def report_list(self, obj):
        if not obj.report:
            return '-'
        else:
            res = []
            try:
                res_list = json.loads(obj.report)
                res = ['<li>%s - %s</li>' % (item['ftime'], item['context']) for item in res_list]
            except:
                pass
            return "<ul>%s</ul>" % ''.join(res)

    report_list.short_description = '物流状态报告'
    report_list.allow_tags = True


admin.site.register(ShipReport, ShipReportAdmin)


class ShipPackageAdmin(admin.ModelAdmin):
    list_display = ('package_no', 'order_no', 'receiver', 'receiver_mobile', 'ship_province', 'ship_address',
                    'ship_vendor', 'ship_code')


