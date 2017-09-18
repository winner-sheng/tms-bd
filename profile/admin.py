# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib import messages
from django.utils import html
from profile.models import *
from util import qiniu_util
from vendor.models import Supplier

__author__ = 'Winsom'


class ShipAddressAdmin(admin.ModelAdmin):
    list_display = ['receiver', 'receiver_mobile', 'ship_province', 'ship_city', 'ship_district', 'ship_address',
                    'zip_code', 'is_default',]
    readonly_fields = ['uid', 'receiver', 'receiver_mobile', 'ship_address', 'zip_code', 'is_default',]
    pass
    # exclude = ['addr_md5']


def charge_back(model_admin, request, queryset):
    cnt = 0
    for item in queryset:
        item.charge_back()
        model_admin.log_change(request, item, u'撤销')
        cnt += 1

    model_admin.message_user(request, '已撤销%s笔资金流水' % cnt, messages.INFO)

charge_back.short_description = '【撤销】选中的资金流水'


class UserAccountBookAdmin(admin.ModelAdmin):
    list_display = ['account_no', 'type', 'user', 'figure', 'account_desc', 'is_income', 'create_time']
    fields = readonly_fields = ['account_no', 'type', 'user', 'uid', 'figure', 'is_income', 'account_desc',
                                'extra_type', 'extra_data', 'trans_no', 'create_time', 'effective_time']
    list_filter = ['is_income', 'type', 'extra_type', 'create_time', ]
    search_fields = ['account_no', 'uid', 'account_desc', 'extra_data']
    list_per_page = 20

    def user(self, obj):
        try:
            user = EndUser.objects.get(uid=obj.uid)
            return "%s / %s" % (user.real_name or '-', user.nick_name or user.ex_nick_name or '-')
        except:
            u = obj.uid.split('-')
            i = int(u[1])
            supplier = Supplier.objects.get(id=i)
            return "%s : %s" % (supplier.province or '-', supplier.name)
            # return 'N/A'

    user.short_description = u'用户'

    actions = [charge_back]

    def get_actions(self, request):
        actions = super(UserAccountBookAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        if not request.user.is_superuser:
            del actions['charge_back']
        return actions

    def save_model(self, request, obj, form, change):
        self.message_user(request, '资金流水不能编辑！', messages.WARNING)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


def confirm_withdraw(model_admin, request, queryset):
    cnt = 0
    failed = 0
    for req in queryset:
        if req.status != WithdrawRequest.STATUS_TBD:
            model_admin.message_user(request, '[ID:%s]%s已被处理，不可重复操作！' % (req.pk, req), messages.ERROR)
            continue

        cnt += 1
        try:
            req.confirm()
            model_admin.log_change(request, req, '批量确认提现%s到%s' % (req.amount, req.get_ca_type_display()))
        except Exception, e:
            failed += 1
            model_admin.message_user(request, e.message, messages.ERROR)

    model_admin.message_user(request, "共为【%s】条申请确认提现（其中失败%s个）" % (cnt, failed), messages.INFO)


confirm_withdraw.short_description = '3.为选中的申请【确认提现】'


def auditing_withdraw(model_admin, request, queryset):  # 提现审核通过，老蔡审核
    cnt = 0
    failed = 0
    for req in queryset:
        if req.status != WithdrawRequest.STATUS_AUDITING:
            model_admin.message_user(request, '[ID:%s]%s已被处理，不可重复操作！' % (req.pk, req), messages.ERROR)
            continue

        cnt += 1
        try:
            req.audited()
            model_admin.log_change(request, req, '审核通过：批量确认提现%s到%s' % (req.amount, req.get_ca_type_display()))
        except Exception, e:
            failed += 1
            model_admin.message_user(request, e.message, messages.ERROR)

    model_admin.message_user(request, "共为【%s】条申请审核通过提现（其中失败%s个）" % (cnt, failed), messages.INFO)


auditing_withdraw.short_description = '1.为选中的申请【（管理员）审核通过提现】'


def confirmed_withdraw(model_admin, request, queryset):  # 提现确认通过，财务确定
    cnt = 0
    failed = 0
    for req in queryset:
        if req.status != WithdrawRequest.STATUS_CONFIRMING:
            model_admin.message_user(request, '[ID:%s]%s已被处理，不可重复操作！' % (req.pk, req), messages.ERROR)
            continue

        cnt += 1
        try:
            req.confirmed()
            model_admin.log_change(request, req, '确认通过：批量确认提现%s到%s' % (req.amount, req.get_ca_type_display()))
        except Exception, e:
            failed += 1
            model_admin.message_user(request, e.message, messages.ERROR)

    model_admin.message_user(request, "共为【%s】条申请确认通过提现（其中失败%s个）" % (cnt, failed), messages.INFO)


confirmed_withdraw.short_description = '2.为选中的申请【（财务）确认通过提现】'


class WithdrawRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'uid', 'ca_type', 'ca_no', 'amount', 'status',
                    'create_time', 'process_time', 'uid_type', 'real_uid', 'result', ]    # 'bank_name', 'open_bank',
    fields = ['id', 'user', 'uid', 'ca_type', 'ca_no', 'amount', 'status',
              'create_time', 'process_time', 'uid_type', 'real_uid', 'account_no', 'result', ]    # 'bank_code', 'bank_name', 'open_bank',
    readonly_fields = fields
    # readonly_fields = ['id', 'user', 'uid', 'ca_type', 'ca_no', 'amount',
    #                    'create_time', 'process_time', 'uid_type', 'real_uid', 'account_no', 'result', ]
    # list_editable = ('status', )
    list_filter = ['ca_type', 'uid_type', 'status', ]
    search_fields = ['uid', 'ca_no', ]
    actions = [auditing_withdraw, confirmed_withdraw, confirm_withdraw, ]

    def get_actions(self, request):
        actions = super(WithdrawRequestAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def user(self, obj):
        try:
            user = EndUser.objects.get(uid=obj.uid)
            return "%s / %s" % (user.real_name, user.nick_name or user.ex_nick_name)
        except:
            u = obj.uid.split('-')
            i = int(u[1])
            supplier = Supplier.objects.get(id=i)
            return "%s : %s" % (supplier.province or '-', supplier.name)
            # return 'N/A'

    user.short_description = u'用户'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        super(WithdrawRequestAdmin, self).save_model(request, obj, form, change)


def ban_user(model_admin, request, queryset):
    cnt = queryset.update(status=EndUser.STATUS_BANNED)
    model_admin.message_user(request, "已将【%s】名选中的用户加入黑名单" % cnt, messages.INFO)


ban_user.short_description = '将选中的用户【加入黑名单】'


def pass_review(model_admin, request, queryset):
    cnt = queryset.update(review_status=EndUserEnterprise.REVIEW_PASSED,
                          status=EndUserEnterprise.STATUS_ACTIVE)
    for record in queryset:
        if record.created_by:
            _notify_review_result(record.created_by,
                                  '企业账号申请审核通知',
                                  '恭喜您！您申请的企业账号[%s]已审核通过！' % record.real_name)

    model_admin.message_user(request, "已审核通过【%s】条选中的用户记录" % cnt, messages.INFO)


pass_review.short_description = '【审核通过】选中的用户'


class EndUserAdmin(admin.ModelAdmin):
    list_display = ['uid', 'real_name', 'nick_name', 'mobile', 'gender', 'status', 'user_ext', 'register_time']
    readonly_fields = fields = ['uid', 'nick_name', 'avatar', 'ex_nick_name', 'ex_avatar', 'real_name', 'mobile',
                                'gender', 'status', 'entry_uid', 'referrer', 'org_uid', 'user_ext',
                                'register_time', 'last_login', 'update_time']
    # list_editable = ['status']
    search_fields = ['uid', 'real_name', 'nick_name', 'mobile', ]
    list_filter = ['status', 'gender', 'register_time', 'last_login']
    ordering = ['-update_time']
    actions = [ban_user]

    def get_queryset(self, request):
        qs = super(EndUserAdmin, self).get_queryset(request)
        return qs.filter(user_type=EndUser.USER_PERSON)

    def user_ext(self, instance):
        ext = EndUserExt.objects.filter(uid=instance.uid)
        return "<br>".join(["%s: %s" % (item.get_ex_id_type_display(), item.ex_id) for item in ext]) if ext else '-'

    user_ext.short_description = '第三方账号'
    user_ext.allow_tags = True

    class Meta(object):
        exclude = ['password']


class EndUserExtAdmin(admin.ModelAdmin):
    readonly_fields = list_display = ['uid', 'ex_id_type', 'ex_id', 'reg_time', ]
    search_fields = ['uid', 'ex_id', 'reg_time']
    list_filter = ['ex_id_type', 'reg_time']


def _notify_review_result(uids, subject='', body=''):
    from log.models import WechatMsgLog
    WechatMsgLog.put_in_queue(uids, open_id=None, subject=subject, body=body)


class EndUserEnterpriseAdmin(admin.ModelAdmin):
    list_display = ['name', 'user_type', 'logo', 'status', 'overhead_rate', 'review_status', 'uid', ]
    readonly_fields = ['uid', 'user_type', 'logo', 'links', 'name', 'status', 'referrer', 'org_uid',
                       'register_time', 'update_time', 'id_card_img', 'license_img', 'created_by', 'review_status']
    fields = readonly_fields + ['review_note', 'overhead_rate']
    # list_editable = ['status']
    save_on_top = True
    search_fields = ['uid', 'real_name', ]
    list_filter = ['user_type', 'status', 'review_status', 'register_time', ]
    ordering = ['-update_time']
    actions = [ban_user, pass_review]

    def name(self, instance):
        return instance.real_name

    name.short_description = '企业名称'
    name.allow_tags = True
    name.admin_order_field = 'real_name'

    def logo(self, instance):
        return "<img src='%s' style='max-width:60px;max-height:60px;'>" % html.escape(instance.avatar) if instance.avatar else ''

    logo.short_description = 'LOGO'
    logo.allow_tags = True

    def id_card_img(self, instance):
        if instance.id_card_image:
            img_url = qiniu_util.get_private_url(instance.id_card_image)
            return "<img src='%s' style='max-width:800px;'>" % img_url
        else:
            return '-'

    id_card_img.short_description = '身份证照'
    id_card_img.allow_tags = True

    def license_img(self, instance):
        return "<img src='%s' style='max-width:800px;'>" % qiniu_util.get_private_url(instance.license_image) if instance.license_image else ''

    license_img.short_description = '执照/资质证照'
    license_img.allow_tags = True

    def links(self, instance):
        links = EndUserLink.objects.filter(uid=instance.uid)
        return "<br>".join(["<a href='%s'>%s</a>" % (link.link, link.get_link_type_display()) for link in links])

    links.short_description = '关联链接'
    links.allow_tags = True

    def save_model(self, request, obj, form, change):
        if '_pass' in form.data:
            form.instance.review_status = EndUserEnterprise.REVIEW_PASSED
            form.instance.status = EndUserEnterprise.STATUS_ACTIVE
            if form.instance.created_by:
                _notify_review_result(form.instance.created_by, '企业账号申请审核通知', '恭喜您！您申请的企业账号[%s]已审核通过！' % form.instance.real_name)
        elif '_reject' in form.data:
            form.instance.review_status = EndUserEnterprise.REVIEW_REJECTED
            form.instance.status = EndUserEnterprise.STATUS_INACTIVE
            if form.instance.created_by:
                _notify_review_result(form.instance.created_by,
                                      '企业账号申请审核通知',
                                      '很抱歉的通知您！您申请的企业账号[%s]审核未通过：%s！' % (form.instance.real_name, form.instance.review_note))
        return super(EndUserEnterpriseAdmin, self).save_model(request, obj, form, change)

    class Meta(object):
        exclude = EndUserEnterprise.unused_fields


admin.site.register(ShipAddress, ShipAddressAdmin)
admin.site.register(EndUser, EndUserAdmin)
admin.site.register(EndUserEnterprise, EndUserEnterpriseAdmin)
admin.site.register(EndUserExt, EndUserExtAdmin)
admin.site.register(UserAccountBook, UserAccountBookAdmin)
admin.site.register(WithdrawRequest, WithdrawRequestAdmin)
admin.site.register(UserCapitalAccount)