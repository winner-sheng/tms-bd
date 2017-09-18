# -*- coding: utf-8 -*-
import datetime

from django.contrib import admin
from django.utils.timezone import now, localtime
from django.http.response import HttpResponseRedirect
from django.contrib import messages

from .models import AgentQueryLog, UserPayLog, UserMailLog, TaskLog, UserFeedback, WechatMsgLog, UserSmsLog
from tms import settings


class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'feedback', 'answer', 'create_time',]
    readonly_fields = ['user']

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return (
                (None, {'fields': ('feedback',)}),
            )
        else:
            return (
                (None, {'fields': ('feedback', 'answer', )}),
            )

    def save_model(self, request, obj, form, change):
        if not obj.create_by:
            obj.create_by = request.user.id
        obj.update_by = request.user.id
        if not obj.user_id:
            obj.user = request.user
        super(UserFeedbackAdmin, self).save_model(request, obj, form, change)


class PingppHookLogAdmin(admin.ModelAdmin):
    list_display = ['event_id', 'livemode', 'created', 'pending_webhooks', 'type', 'request']
    readonly_fields = ['event_id', 'object', 'livemode', 'created', 'data', 'pending_webhooks', 'type', 'request']
    fields = ['event_id', 'type', 'object', 'data', 'pending_webhooks', 'request', 'livemode', 'created']

    def save_model(self, request, obj, form, change):
        self.message_user(request, '日志记录不能编辑！', messages.WARNING)


class UserPayLogAdmin(admin.ModelAdmin):
    list_display = ['pay_code', 'is_refund', 'order_no', 'uid',
                    'pay_type', 'pay_amount', 'pay_time', 'is_confirmed', ]
    readonly_fields = ['pay_code', 'is_refund', 'order_no', 'uid', 'pay_type',
                       'pay_amount', 'pay_time', 'is_confirmed', 'pay_log']
    search_fields = ['pay_code', 'uid', 'order_no']
    list_filter = ['pay_type', 'is_confirmed', 'is_refund', ]
    date_hierarchy = 'pay_time'
    actions = ['export_log', ]

    def has_delete_permission(self, request, obj=None):
        return False

    def export_log(self, request, queryset):
        if request.POST.get('select_across') == '1':  # more than selected in one page
            request.session['selected_for_export'] = [str(record.id) for record in queryset]
            return HttpResponseRedirect("/tms-api/admin/export/paylog/csv?ids=select_across")
        else:
            selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
            return HttpResponseRedirect("/tms-api/admin/export/paylog/csv?ids=%s" % ",".join(selected))

    export_log.short_description = '【导出】选中的日志'

    def save_model(self, request, obj, form, change):
        self.message_user(request, '日志记录不能编辑！', messages.WARNING)


class UserSmsLogAdmin(admin.ModelAdmin):
    list_display = ['mobile', 'send_time', 'sms', 'log', ]
    readonly_fields = ['mobile', 'send_time', 'sms', 'log', ]

    def save_model(self, request, obj, form, change):
        self.message_user(request, '日志记录不能编辑！', messages.WARNING)


class AgentQueryLogAdmin(admin.ModelAdmin):
    list_display = ['agent', 'query_time', 'query_res', 'order_no', 'user_id', 'pay_amount', 'is_checked']
    list_editable = ['is_checked']
    readonly_fields = ['agent', 'query_time', 'order_no', 'user_id', 'pay_amount', 'query_res', ]
    search_fields = ['agent__username', 'order_no', 'user_id', ]
    list_filter = ['query_result', 'is_checked', ]

    def query_res(self, obj):
        if not obj.is_checked and obj.query_result == AgentQueryLog.RESULT_NO_ACTION and obj.query_time:
            if settings.USE_TZ:
                delta = localtime(now()) - localtime(obj.query_time)
            else:
                delta = datetime.datetime.now() - obj.query_time

            if delta.total_seconds() > settings.AGENT_QUERY_EXPIRY:
                return '<span style="background-color:red;color:white">' \
                        + obj.get_query_result_display() \
                        + '[可疑行为]</span>'
        return obj.get_query_result_display()

    query_res.allow_tags = True
    query_res.short_description = "查询结果"

    def save_model(self, request, obj, form, change):
        self.message_user(request, '日志记录不能编辑！', messages.WARNING)


class TaskLogAdmin(admin.ModelAdmin):
    list_display = ['name', 'exec_result', 'is_ok', 'start_time', 'end_time', 'time_cost', ]
    list_filter = ['name', 'is_ok', ]

    date_hierarchy = 'start_time'
    readonly_fields = ['name', 'exec_result', 'is_ok', 'start_time', 'end_time', 'time_cost', 'result_file']

    def save_model(self, request, obj, form, change):
        self.message_user(request, '日志记录不能编辑！', messages.WARNING)


class UserMailLogAdmin(admin.ModelAdmin):
    list_display = ['mail_to', 'subject', 'is_sent', 'retries', 'send_time', ]
    fields = readonly_fields = ['mail_to'] + [f.name for f in UserMailLog._meta.fields]

    list_filter = ['is_sent']
    search_fields = ['mail_to', 'subject']

    def mail_to(self, obj):
        return ";".join(["%s: %s" % (m[0], m[1]) for m in obj.get_mail_to() if m[0] != 'bcc'])

    mail_to.short_description = '收件地址'
    mail_to.allow_tags = False

    def save_model(self, request, obj, form, change):
        self.message_user(request, '日志记录不能编辑！', messages.WARNING)

admin.site.register(UserFeedback, UserFeedbackAdmin)
# admin.site.register(PingppHookLog, PingppHookLogAdmin)
admin.site.register(UserPayLog, UserPayLogAdmin)
# admin.site.register(UserSmsLog, UserSmsLogAdmin)
# admin.site.register(AgentQueryLog, AgentQueryLogAdmin)
admin.site.register(TaskLog, TaskLogAdmin)
admin.site.register(UserMailLog, UserMailLogAdmin)
admin.site.register(WechatMsgLog)
admin.site.register(UserSmsLog)