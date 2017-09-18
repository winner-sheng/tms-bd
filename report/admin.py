# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from report.models import TmsReport, SupplierBillReport, SupplierBillReportByAgent
from util.renderutil import logger
import json
from tms.admin import store_site
from decimal import Decimal
# from vendor.models import SalesAgent


__author__ = 'Winsom'


class RewardListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = u'未结算收益'
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'ns_reward'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('1000', u'￥1000以上'),
            ('500,1000', u'￥500以上，￥1000以下'),
            ('100,500', u'￥100以上，￥500以下'),
            ('0,100', u'￥100以下（大于￥0）'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == '0,100':
            return queryset.filter(not_settled_reward__gt=0, not_settled_reward__lte=100)
        elif self.value() == '100,500':
            return queryset.filter(not_settled_reward__gt=100, not_settled_reward__lte=500)
        elif self.value() == '500,1000':
            return queryset.filter(not_settled_reward__gt=500, not_settled_reward__lte=1000)
        elif self.value() == '1000':
            return queryset.filter(not_settled_reward__gt=1000)


def export_summary(model_admin, request, queryset):
    if request.POST.get('select_across') == '1':  # more than selected in one page
        request.session['selected_for_export'] = [str(record.id) for record in queryset]
        return HttpResponseRedirect("/tms-api/admin/export/reward/csv?ids=select_across")
    else:
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect("/tms-api/admin/export/reward/csv?ids=%s" % ",".join(selected))


export_summary.short_description = '导出应结算收益清单'


class RewardSummaryAdmin(admin.ModelAdmin):
    list_display = ['uid', 'real_name', 'nick_name', 'total_cnt', 'settled_reward',
                    'not_settled_reward', 'must_settled_reward', 'revoked_reward']
    readonly_fields = ['uid', 'real_name', 'nick_name', 'total_cnt', 'settled_reward', 'must_settled_reward',
                       'not_settled_reward', 'revoked_reward', 'mobile', 'ex_nick_name', ]
    search_fields = ['real_name', 'nick_name', 'uid', ]
    list_filter = (RewardListFilter,)
    actions = [export_summary, ]

    def save_model(self, request, obj, form, change):
        self.message_user(request, '统计数据不可编辑！', messages.WARNING)
        return False

    def render_delete_form(self, request, context):
        self.message_user(request, '统计数据不可编辑！', messages.WARNING)
        return False

    def delete_model(self, request, obj):
        self.message_user(request, '统计数据不可编辑！', messages.WARNING)
        return False

    # def has_add_permission(self, request):
    #     return False
    #
    # def has_change_permission(self, request, obj=None):
    #     return False
    #
    def has_delete_permission(self, request, obj=None):
        return False


class SupplierBillReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'period', 'status', 'create_time')
    list_filter = ('status', )
    search_fields = ('title', )
    readonly_fields = ('period', )

    def period(self, instance):
        return '%s - %s' % (instance.start_time, instance.end_time)
    period.short_description = '报告周期'

    def has_add_permission(self, request):
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)
        extra_context = extra_context or {}
        if obj:
            try:
                summary = json.loads(obj.summary)
                extra_context['report'] = {"header": json.loads(obj.header),
                                           "data": json.loads(obj.data),
                                           "summary": summary,
                                           "is_owner": False}
                if obj.version == 1:
                    extra_context['report']['shipfee_total'] = Decimal(summary[8] or 0) - Decimal(summary[9] or 0)
                    extra_context['report']['bill_total'] = Decimal(summary[13] or 0) \
                                                            + extra_context['report']['shipfee_total'] \
                                                            - Decimal(summary[14] or 0)
                else:
                    extra_context['report']['shipfee_total'] = Decimal(summary[5][1] or 0) - Decimal(summary[6][1] or 0)
                    extra_context['report']['bill_total'] = Decimal(summary[0][1] or 0)

                if request.user.has_perm('basedata.as_supplier'):
                    from vendor.models import SupplierManager
                    supplier_ids = SupplierManager.objects.filter(user_id=request.user.id).values_list('supplier_id', flat=True)
                    if obj.owner and obj.owner[:4] == 'SUP-' and int(obj.owner[4:]) in supplier_ids:
                        extra_context['report']['is_owner'] = True

            except Exception, e:
                logger.exception(e)
        return super(SupplierBillReportAdmin, self).change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def get_queryset(self, request):
        qs = super(SupplierBillReportAdmin, self).get_queryset(request)
        qs = qs.filter(report_type='order_income_by_signoff')
        if request.user.is_superuser or request.user.has_perm('report.manage_supplier_bill'):
            pass
        elif request.user.has_perm('basedata.as_supplier'):
            from vendor.models import SupplierManager
            supplier_ids = SupplierManager.objects.filter(user_id=request.user.id).values_list('supplier_id', flat=True)
            qs = qs.filter(owner__in=["SUP-%s" % sid for sid in supplier_ids])
        else:
            qs = qs.none()

        return qs


class SupplierBillReportByAgentAdmin(admin.ModelAdmin):
    list_display = ('title', 'period', 'status', 'create_time')
    list_filter = ('status', 'create_time')
    search_fields = ('title', )
    readonly_fields = ('period', )

    def period(self, instance):
        return '%s - %s' % (instance.start_time, instance.end_time)
    period.short_description = '报告周期'

    def has_add_permission(self, request):
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)
        extra_context = extra_context or {}
        if obj:
            try:
                summary = json.loads(obj.summary)
                extra_context['report'] = {"header": json.loads(obj.header),
                                           "data": json.loads(obj.data),
                                           "summary": summary,
                                           "is_owner": False}
                if obj.version == 1:
                    extra_context['report']['shipfee_total'] = Decimal(summary[8] or 0) - Decimal(summary[9] or 0)
                    extra_context['report']['bill_total'] = Decimal(summary[13] or 0) \
                                                            + extra_context['report']['shipfee_total'] \
                                                            - Decimal(summary[14] or 0)
                else:
                    extra_context['report']['shipfee_total'] = Decimal(summary[5][1] or 0) - Decimal(summary[6][1] or 0)
                    extra_context['report']['bill_total'] = Decimal(summary[0][1] or 0)

                if request.user.has_perm('basedata.as_supplier'):
                    from vendor.models import SupplierManager
                    supplier_ids = SupplierManager.objects.filter(user_id=request.user.id).values_list('supplier_id', flat=True)
                    if obj.owner and obj.owner[:4] == 'SUP-' and int(obj.owner[4:]) in supplier_ids:
                        extra_context['report']['is_owner'] = True
                    # agent_ids = SaleAgent.objects.filter(user_id=request.user.id).values_list('supplier_id', flat=True)

            except Exception, e:
                logger.exception(e)
        return super(SupplierBillReportByAgentAdmin, self).change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def get_queryset(self, request):
        qs = super(SupplierBillReportByAgentAdmin, self).get_queryset(request)
        qs = qs.filter(report_type='order_income_by_signoff_by_agent')
        if request.user.is_superuser or request.user.has_perm('report.manage_supplier_bill'):
            pass
        elif request.user.has_perm('basedata.as_supplier'):
            from vendor.models import SupplierManager
            supplier_ids = SupplierManager.objects.filter(user_id=request.user.id).values_list('supplier_id', flat=True)
            qs = qs.filter(owner__in=["SUP-%s" % sid for sid in supplier_ids])
        else:
            qs = qs.none()

        return qs


admin.site.register(SupplierBillReport, SupplierBillReportAdmin)
store_site.register(SupplierBillReport, SupplierBillReportAdmin)
# admin.site.register(RewardSummary, RewardSummaryAdmin)
admin.site.register(SupplierBillReportByAgent, SupplierBillReportByAgentAdmin)
store_site.register(SupplierBillReportByAgent, SupplierBillReportByAgentAdmin)
