# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin, messages
from django.http.response import HttpResponseRedirect
from django.template import RequestContext
from django import forms
from django.shortcuts import render_to_response

import datetime
from promote.models import CouponTicket, RewardRecord, CouponRule, ComputationRule, CouponRuleSet, RuleSetMap
from util.renderutil import export_excel, day_str
__author__ = 'Winsom'


class RewardCreateDateFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = u'产生日期'
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'create_date'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('today', u'当天'),
            ('yesterday', u'昨天'),
            ('past7days', u'最近7天'),
            ('7daysbefore', u'7天之前'),
            ('lastmonth', u'上个月'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        today = datetime.datetime.now()
        today = datetime.date(today.year, today.month, today.day)

        value = self.value()
        if value == 'today':
            return queryset.filter(create_time__gte=today)
        elif value == 'yesterday':
            return queryset.filter(create_time__range=(today-datetime.timedelta(days=1), today))
        elif value == 'past7days':
            return queryset.filter(create_time__gte=today-datetime.timedelta(days=7))
        elif value == '7daysbefore':
            return queryset.filter(create_time__lt=today-datetime.timedelta(days=7))
        elif value == 'lastmonth':
            return queryset.filter(create_time__month=today.month-1)


class RewardAchievedDateFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = u'结算日期'
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'achieved_date'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('today', u'当天'),
            ('yesterday', u'昨天'),
            ('past7days', u'最近7天'),
            ('7daysbefore', u'7天之前'),
            ('lastmonth', u'上个月'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        today = datetime.datetime.now()
        today = datetime.date(today.year, today.month, today.day)
        if self.value() == 'today':
            return queryset.filter(achieved_time__gte=today)
        elif self.value() == 'yesterday':
            return queryset.filter(achieved_time__range=(today-datetime.timedelta(days=1), today))
        elif self.value() == 'past7days':
            return queryset.filter(achieved_time__gte=today-datetime.timedelta(days=7))
        elif self.value() == '7daysbefore':
            return queryset.filter(achieved_time__lt=today-datetime.timedelta(days=7))
        elif self.value() == 'lastmonth':
            return queryset.filter(achieved_time__month=today.month-1)


def export_reward_order(model_admin, request, queryset):
    if request.POST.get('select_across') == '1':  # more than selected in one page
        request.session['selected_for_export'] = [str(record.id) for record in queryset]
        return HttpResponseRedirect("/tms-api/admin/export/reward_order/csv?ids=select_across")
    else:
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect("/tms-api/admin/export/reward_order/csv?ids=%s" % ",".join(selected))


export_reward_order.short_description = u'导出收益关联订单'


def transfer_reward(self, request, queryset):
    from profile.models import EndUser, UserAccountBook
    from basedata.models import Order
    class TransferForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        uid = forms.CharField(widget=forms.TextInput, max_length=32, label=u'请输入新归属用户的uid ', required=True)
        # uid = forms.TextInput(attrs={'required': True, 'name': 'uid', 'placeholder': })

    form = None

    if 'apply' in request.POST:
        uid = request.POST.get('uid')
        if not EndUser.objects.filter(uid=uid).exists():
            self.message_user(request, u'找不到uid为[%s]的用户' % uid)
        else:
            reward_cnt = account_cnt = 0
            for reward in queryset:
                old_uid = reward.referrer_id
                order = account = None
                try:
                    order = Order.objects.get(order_no=reward.order_no)
                    if reward.account_no:  # 已经入账，也需要转移流水
                        account = UserAccountBook.objects.get(account_no=reward.account_no)
                except Order.DoesNotExist:
                    self.message_user(request, u"找不到订单：%s" % reward.order_no)
                    continue
                except UserAccountBook.DoesNotExist:
                    self.message_user(request, u"找不到资金记录：%s" % reward.account_no)
                    continue

                reward.referrer_id = uid
                reward.save()
                self.log_change(request, reward, u'收益转移自[%s]' % old_uid)
                reward_cnt += 1
                Order.objects.filter(order_no=reward.order_no).update(referrer_id=uid)  # 更新订单的推荐信息
                self.log_change(request, order, u'推广人变更自[%s]' % old_uid)
                if account:
                    account.uid = uid
                    account.save()
                    account_cnt += 1
                    self.log_change(request, account, u'流水转移自[%s]' % old_uid)

            self.message_user(request, u"合计转移%s笔收益及%s笔流水" % (reward_cnt, account_cnt))
        return HttpResponseRedirect(request.get_full_path())

    if not form:
        form = TransferForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

    return render_to_response("admin/promote/rewardrecord/transfer.html",
                               RequestContext(request,
                                              {"rewards": queryset,
                                               "action": "transfer_order",
                                               "form": form}))


transfer_reward.short_description = u'将选中的收益【转移】给指定用户'


class RewardRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_no', 'referrer', 'order_pay_amount', 'reward_type', 'reward', 'achieved', 'status',
                    'create_time', 'achieved_time', 'account_no', )
    readonly_fields = fields = ('id', 'order_no', 'referrer', 'source_uid', 'order_pay_amount', 'reward_type',
                                'status', 'reward', 'achieved', 'achieved_time', 'account_no', 'memo', 'create_time',
                                'activity_code', )
    search_fields = ('account_no', 'referrer_id', 'order_no')
    list_filter = ['status', 'reward_type', 'activity_code', RewardAchievedDateFilter, RewardCreateDateFilter]
    actions = [export_reward_order, ]
    # date_hierarchy = 'create_time'

    def order_pay_amount(self, obj):
        from basedata.models import Order
        try:
            order = Order.objects.get(order_no=obj.order_no)
            return "%s / %s" % (order.pay_amount, order.get_order_state_display())
        except:
            return 'N/A'

    order_pay_amount.short_description = u'订单总额/状态'

    def referrer(self, obj):
        from profile.models import EndUser
        try:
            user = EndUser.objects.get(uid=obj.referrer_id)
            return "%s / %s / %s" % (user.real_name or '-', user.nick_name or user.ex_nick_name or '-', user.uid)
        except:
            return 'N/A'

    referrer.short_description = u'推广人/昵称/uid'

    # def get_search_results(self, request, queryset, search_term):
    #     queryset, use_distinct = super(RewardRecordAdmin, self).get_search_results(request, queryset, search_term)
    #     try:
    #         days_before = - int(search_term)
    #     except ValueError:
    #         pass
    #     else:
    #         queryset = self.model.objects.raw('''
    #             SELECT `a`.id, `b`.`real_name` AS `real_name`,`b`.`mobile` AS `mobile`,
    #             `b`.`ex_nick_name` AS `ex_nick_name`,`b`.`nick_name` AS `nick_name`,
    #             COUNT(0) AS `total_cnt`,
    #             SUM(IF((`a`.`status` = 0),`a`.`reward`,0)) AS `not_settled_reward`,
    #             SUM(IF((`a`.`status` = 1) AND (`a`.`account_no` is NULL or `a`.`account_no`=""),`a`.`reward`,0))
    #             AS `must_settled_reward`,
    #             SUM(IF((`a`.`status` = 1),`a`.`achieved`,0)) AS `settled_reward`,
    #             SUM(IF((`a`.`status` = 2),`a`.`reward`,0)) AS `revoked_reward`,`a`.`referrer_id` AS `uid`
    #             FROM (`promote_rewardrecord` `a`
    #             JOIN `profile_enduser` `b` ON((`a`.`referrer_id` = `b`.`uid`)))
    #             WHERE (`a`.`create_time` < date_add(curdate(), interval %s day))
    #             GROUP BY `a`.`referrer_id`
    #             ORDER BY `settled_reward`,`not_settled_reward` DESC;''', params=[days_before])
    #
    #         def raw_len(self):
    #             sql = 'SELECT COUNT(*) FROM ( %s ) as c;' % str(self.query)[:-1]
    #             cursor = connection.cursor()
    #             cursor.execute(sql)
    #             row = cursor.fetchone()
    #             return row[0]
    #         setattr(type(queryset), '__len__', raw_len)
    #
    #     return queryset, use_distinct

admin.site.register(RewardRecord, RewardRecordAdmin)


class ComputationRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'apply_to', 'effective_date', 'expire_date', 'allow_overlap', 'priority']
    list_editable = ['effective_date', 'expire_date', 'allow_overlap', 'priority']
    save_as = True

    def save_model(self, request, obj, form, change):
        if not obj.create_by:
            obj.create_by = request.user.id
        obj.update_by = request.user.id
        super(ComputationRuleAdmin, self).save_model(request, obj, form, change)

    class Meta:
        exclude = ['create_time', 'create_by', 'update_time', 'update_by', ]
        # js = (settings.STATIC_URL+'tiny_mce/tiny_mce.js', settings.STATIC_URL+'js/textareas.js',)


class CouponTicketAdmin(admin.ModelAdmin):
    list_display = ['code', 'rule', 'get_time', 'order_no', 'consume_time', 'expiry_date', ]
    readonly_fields = ['rule', 'code', 'consumer', 'get_time', 'order_no', 'consume_time', ]
    list_filter = ['rule']
    search_fields = ['code', 'consumer', 'order_no', 'rule__code']
    date_hierarchy = 'get_time'
    list_per_page = 20


class CouponTicketInline(admin.TabularInline):
    model = CouponTicket
    can_delete = False
    can_add = False
    fields = list_display = readonly_fields = ('code', 'get_time', 'order_no', 'consume_time', 'is_expired', )
    extra = 0
    list_per_page = 10

    # def has_delete_permission(self, request, obj=None):
    #     if obj and obj.status == CouponTicket.STATE_NOT_CLAIMED:
    #         return True
    #     else:
    #         return False


def delete_coupon_rule(self, request, queryset):
    for rule in queryset:
        if rule.tickets.filter(order_no__isnull=False).exists():
            if rule.is_active:
                rule.is_active = False
                rule.save()
            self.message_user(request, '[%s]已有优惠券被使用，无法删除，已设置为失效' % rule.name, messages.WARNING)
        else:
            rule_name = rule.name
            rule.tickets.all().delete()
            rule.delete()
            self.message_user(request, '[%s]已删除' % rule_name)

delete_coupon_rule.short_description = '【删除】选中的优惠活动'


def export_coupon_tickets(self, request, queryset):
    if request.POST.get('select_across') == '1':  # more than selected in one page
        request.session['selected_for_export'] = [str(record.order_no) for record in queryset]
        return HttpResponseRedirect("/tms-api/admin/export/couponticket/xls?ids=select_across")
    else:
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect("/tms-api/admin/export/couponticket/xls?ids=%s" % ",".join(selected))

export_coupon_tickets.short_description = '【导出】选定活动的所有优惠券'


class CouponRuleAdmin(admin.ModelAdmin):
    # inlines = [CouponTicketInline]  # Inline
    list_display = ['code', 'name', 'discount', 'statistic', 'repeatable', 'allow_addon',
                    'start_time', 'end_time', 'allow_dynamic', 'dynamic_days', 'is_active', ]
    list_filter = ['is_active', 'repeatable', 'allow_addon', 'discount']
    list_editable = ['start_time', 'end_time', ]
    search_fields = ['name', 'code']
    date_hierarchy = 'create_time'
    raw_id_fields = ['coupon_image']
    actions = [delete_coupon_rule, export_coupon_tickets]
    save_on_top = True
    save_as = True

    def get_actions(self, request):
        actions = super(CouponRuleAdmin, self).get_actions(request)
        if not request.user.is_superuser and 'delete_coupon_rule' in actions:
            del actions['delete_coupon_rule']  # (name, (func, name, desc))
        return actions

    fields = ['code', 'name', 'link_page', 'description', 'thumbnail', 'coupon_image',
              'discount', 'threshold', 'applied_to_suppliers', 'applied_to_products',
              # 'applied_to_stores', 'applied_to_first_order',
              'pub_number', 'repeatable', 'allow_addon',  'tickets_onetime', 'most_tickets',  # 'format',
              'start_time', 'end_time', 'allow_dynamic', 'dynamic_days', 'is_active',
              'create_time', 'create_by', 'update_time', 'update_by']

    def thumbnail(self, obj):
        """
        返回默认规格的缩略图
        """
        img = obj.coupon_image
        return '<img src="%s">' % img.thumbnail if img else ""

    thumbnail.allow_tags = True
    thumbnail.short_description = u'优惠券缩略图'

    def statistic(self, obj):
        """
        返回优惠券已领用/使用的情况
        :param obj:
        :return:
        """
        if obj:
            claimed = obj.tickets.filter(consumer__isnull=False).count()
            used = obj.tickets.filter(consume_time__isnull=False).count()
            return "%s / %s / %s" % (used, claimed, obj.pub_number)
        else:
            "-"

    statistic.short_description = '已使用/领用/发行总数'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['thumbnail', 'format', 'create_time', 'create_by', 'update_time', 'update_by',
                           'applied_to_stores', 'applied_to_first_order', 'statistic']
        if obj and obj.pk:
            readonly_fields.append('code')
            if obj.is_active:
                readonly_fields.extend(['discount', 'threshold', 'coupon_image', ])
        return readonly_fields

    def save_model(self, request, obj, form, change):
        obj.create_by = obj.create_by or request.user.username
        obj.update_by = request.user.username
        super(CouponRuleAdmin, self).save_model(request, obj, form, change)


class RuleSetMapInline(admin.TabularInline):
    model = RuleSetMap
    fields = list_display = list_editable = ('rule', 'number', 'list_order', )
    raw_id_fields = ['rule']
    extra = 1


class CouponRuleSetAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'thumbnail', 'rules_content', 'start_time', 'end_time', ]
    list_editable = ['start_time', 'end_time', ]
    readonly_fields = ['thumbnail', 'create_time', 'create_by', 'update_time', 'update_by', 'rules_content']
    search_fields = ['name', 'code']
    date_hierarchy = 'start_time'
    raw_id_fields = ['image']
    actions = ['delete_selected']
    save_on_top = True
    save_as = True
    inlines = [RuleSetMapInline]

    fields = ['code', 'name', 'link_page', 'description', 'thumbnail', 'image',
              'start_time', 'end_time', 'create_time', 'create_by', 'update_time', 'update_by']

    def thumbnail(self, obj):
        """
        返回缩略图
        """
        img = obj.image
        return '<img src="%s">' % img.thumbnail if img else ""

    thumbnail.allow_tags = True
    thumbnail.short_description = u'套餐图片'

    def rules_content(self, obj):
        """
        返回套餐中内容简要描述
        :param obj:
        :return:
        """
        if obj:
            rules = obj.rules.all()
            return "<br>".join(["%s*%s" % (r.rule.name, r.number) for r in rules])
        else:
            "-"

    rules_content.allow_tags = True
    rules_content.short_description = '套餐内容'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['thumbnail', 'rules_content', 'create_time', 'create_by', 'update_time', 'update_by', 'link_page']
        if obj and obj.pk:
            readonly_fields.append('code')
        return readonly_fields

    def save_model(self, request, obj, form, change):
        obj.create_by = obj.create_by or request.user.username
        obj.update_by = request.user.username
        super(CouponRuleSetAdmin, self).save_model(request, obj, form, change)


admin.site.register(ComputationRule, ComputationRuleAdmin)
admin.site.register(CouponRule, CouponRuleAdmin)
admin.site.register(CouponRuleSet, CouponRuleSetAdmin)
admin.site.register(CouponTicket, CouponTicketAdmin)
