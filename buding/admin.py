# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib import admin
from django.contrib import messages
from django.utils import html
from buding.models import SaleShop, SaleShopProduct, ShopkeeperInfo, ShopManagerInfo, SaleShopIncome
from tms.admin import store_site
from util import qiniu_util
from profile.models import EndUser
from vendor.models import Supplier
from django.db.models import Sum, Count, Q, F
from tms import Convert, settings
# from django.db.models import Q, F, Count
from util.renderutil import get_fields_list
__author__ = 'sz'


# 审核通过店主申请
def auditing_shopkeeper(model_admin, request, queryset):
    cnt = 0
    failed = 0
    for req in queryset:
        if req.state != ShopkeeperInfo.STATUS_AUDITING_WAITTING:
            model_admin.message_user(request, '[ID:%s]%s已被处理，不可重复操作！' % (req.pk, req), messages.ERROR)
            continue

        cnt += 1
        try:
            req.audited()
            send_message_for_shopkeeper(req.uid)
            model_admin.log_change(request, req, '审核通过：批量确认店主%s到%s' % (req.amount, req.get_ca_type_display()))
        except Exception, e:
            failed += 1
            model_admin.message_user(request, e.message, messages.ERROR)

    model_admin.message_user(request, "共为【%s】条店主申请审核通过（其中失败%s个）" % (cnt, failed), messages.INFO)
auditing_shopkeeper.short_description = '1.为选中的店主申请【（管理员）审核通过】'


# 审核拒绝店主申请
def rejecting_shopkeeper(model_admin, request, queryset):
    cnt = 0
    failed = 0
    for req in queryset:
        if req.state != ShopkeeperInfo.STATUS_AUDITING_WAITTING:
            model_admin.message_user(request, '[ID:%s]%s已被处理，不可重复操作！' % (req.pk, req), messages.ERROR)
            continue

        cnt += 1
        try:
            req.rejectd()
            send_message_for_shopkeeper(req.uid)
            model_admin.log_change(request, req, '审核拒绝：批量确认店主%s到%s' % (req.amount, req.get_ca_type_display()))
        except Exception, e:
            failed += 1
            model_admin.message_user(request, e.message, messages.ERROR)

    model_admin.message_user(request, "共为【%s】条店主申请审核拒绝（其中失败%s个）" % (cnt, failed), messages.INFO)
rejecting_shopkeeper.short_description = '2.为选中的店主申请【（管理员）审核拒绝】'


# 审核通过开店申请
def applied_saleshop(model_admin, request, queryset):
    cnt = 0
    failed = 0
    for req in queryset:
        if req.state != ShopkeeperInfo.STATUS_AUDITING_WAITTING:
            model_admin.message_user(request, '[ID:%s]%s已被处理，不可重复操作！' % (req.pk, req), messages.ERROR)
            continue

        cnt += 1
        try:
            req.applied()
            model_admin.log_change(request, req, '审核通过：批量确认店铺%s到%s' % (req.amount, req.get_ca_type_display()))
        except Exception, e:
            failed += 1
            model_admin.message_user(request, e.message, messages.ERROR)

    model_admin.message_user(request, "共为【%s】条店铺申请审核通过（其中失败%s个）" % (cnt, failed), messages.INFO)
applied_saleshop.short_description = '1.为选中的店铺申请【（管理员）审核通过】'


# 审核拒绝开店申请
def closed_saleshop(model_admin, request, queryset):
    cnt = 0
    failed = 0
    for req in queryset:
        if req.state != ShopkeeperInfo.STATUS_AUDITING_WAITTING:
            model_admin.message_user(request, '[ID:%s]%s已被处理，不可重复操作！' % (req.pk, req), messages.ERROR)
            continue

        cnt += 1
        try:
            req.closed()
            model_admin.log_change(request, req, '审核拒绝：批量确认店铺%s到%s' % (req.amount, req.get_ca_type_display()))
        except Exception, e:
            failed += 1
            model_admin.message_user(request, e.message, messages.ERROR)

    model_admin.message_user(request, "共为【%s】条店铺申请审核拒绝（其中失败%s个）" % (cnt, failed), messages.INFO)
closed_saleshop.short_description = '2.为选中的店铺申请【（管理员）审核拒绝】'


def bd_put_on_shelf(model_admin, request, queryset):
    # if request.user.is_superuser or request.user.has_perm('basedata.can_manage_product'):
    #     reviewed = True
    # elif request.user.has_perm('basedata.as_supplier'):
    #     reviewed = False
    # else:
    #     model_admin.message_user(request, u"访问未授权！", messages.ERROR)
    #     return

    qs = queryset.exclude(status=SaleShopProduct.STATUS_ONSHELF)
    cnt = 0
    for product in qs:
        try:
            # origin_status = product.get_status_display()
            model_admin.log_change(request, product, u'bd_批量上架（原状态：%s）' % product.status)
            product.put_onshelf()
            cnt += 1
        except ValidationError, e:
            model_admin.message_user(request, "%s(%s)" % (e.message, u'操作被取消'), messages.ERROR)

    model_admin.message_user(request, u"共成功上架%d种商品" % cnt, messages.INFO)
bd_put_on_shelf.short_description = u'1.将选中的商品【批量上架】'


def bd_put_off_shelf(model_admin, request, queryset):
    # if request.user.is_superuser or request.user.has_perm('basedata.can_manage_product') \
    #         or request.user.has_perm('basedata.as_supplier'):
    #     pass
    # else:
    #     model_admin.message_user(request, u"访问未授权！", messages.ERROR)

    qs = queryset.exclude(status=SaleShopProduct.STATUS_OFFSHELF)
    cnt = 0
    for product in qs:
        model_admin.log_change(request, product, u'bd_批量下架（原状态：%s）' % product.status)
        product.put_offshelf()
        cnt += 1

    model_admin.message_user(request, u"共成功下架%d种商品" % cnt, messages.INFO)


bd_put_off_shelf.short_description = u'2.将选中的商品【批量下架】'


class SaleshopNameFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = u'店铺名称'
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'name_filter'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        id_name_list = SaleShop.objects.all().values_list('code', 'name').order_by(Convert(F('name')))
        return id_name_list

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        value = self.value()
        if value == 'None':
            return queryset.filter(shopcode__isnull=True)
        elif value:
            return queryset.filter(shopcode=value)
        else:
            return queryset


class SaleShopAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'shopicon', 'state', 'cover', 'uid', 'qrcode', 'keeperqrcode', 'province', 'city',
                    'district', 'address', 'create_time']
    # fields = readonly_fields = ['account_no', 'type', 'user', 'uid', 'figure', 'is_income', 'account_desc',
    #                             'extra_type', 'extra_data', 'trans_no', 'create_time', 'effective_time']
    readonly_fields = ['code', 'uid', 'create_time']
    list_filter = ['shop_type', 'state', 'province', ]
    search_fields = ['code', 'name', 'province', 'city', 'district', 'uid', ]
    list_per_page = 20
    actions = [applied_saleshop, closed_saleshop, ]
    pass


class SaleShopProductAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ['shopcode', 'name', 'product_link', 'status', 'retail_price', 'settle_price', 'tags', 'list_order',
                    'create_time', 'update_time']
    # fields = ['shopcode', 'productid', 'retail_price', 'settle_price', 'create_time', 'update_time']
    readonly_fields = ['shopcode', 'productid', 'create_time']
    list_filter = ['shopcode', 'status', SaleshopNameFilter]
    search_fields = ['shopcode', 'productid']
    list_per_page = 20
    actions = [bd_put_on_shelf, bd_put_off_shelf, ]

    def name(self, obj):
        try:
            ss = SaleShop.objects.get(code=obj.shopcode)
            return "%s" % (ss.name or '-')
        except:
            # return "%s : %s" % (supplier.province or '-', supplier.name)
            return 'N/A'

    name.short_description = u'店铺名称'

    def product_link(self, obj):
        return '<a href="/tms/basedata/product/%s/">%s</a>' % (obj.productid, obj.productid)

    product_link.allow_tags = True
    product_link.short_description = u'商品代码'

    pass


class ShopkeeperInfoAdmin(admin.ModelAdmin):
    list_display = ['uid', 'truename', 'mobile', 'state', 'wx_openid', 'city', 'id_card', 'photo', 'photoReverse', 'create_time']
    list_filter = ['state', 'city', ]
    search_fields = ['uid', 'truename', 'mobile', 'city', 'district', 'id_card', ]
    list_per_page = 20
    actions = [auditing_shopkeeper, rejecting_shopkeeper, ]
    pass


class ShopManagerInfoAdmin(admin.ModelAdmin):
    list_display = ['uid', 'truename', 'mobile', 'name', 'role', 'reward_percent', 'wx_openid', 'pid_name', 'create_time']
    list_filter = ['shopcode', 'role', SaleshopNameFilter]
    search_fields = ['uid', 'truename', 'mobile', 'shopcode']
    readonly_fields = ['uid', 'wx_openid', 'pid_name', 'pid', 'shopcode', 'create_by', 'create_time']
    list_per_page = 20

    def name(self, obj):
        try:
            ss = SaleShop.objects.get(code=obj.shopcode)
            return "%s" % (ss.name or '-')
        except:
            # return "%s : %s" % (supplier.province or '-', supplier.name)
            return 'N/A'

    name.short_description = u'店铺名称'

    def pid_name(self, obj):
        try:
            user = EndUser.objects.get(uid=obj.pid)
            return "%s / %s" % (user.real_name or '-', user.nick_name or user.ex_nick_name or '-')
        except:
            # u = obj.pid.split('-')
            # i = int(u[1])
            # supplier = Supplier.objects.get(id=i)
            # return "%s : %s" % (supplier.province or '-', supplier.name)
            return 'N/A'

    pid_name.short_description = u'推荐人'
    pass


class SaleShopIncomeAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'code', 'product_cost', 'ship_fee', 'adjust_fee',
                    'status', 'has_doubt', 'account_no', 'create_time', ]
    readonly_fields = fields = get_fields_list(SaleShopIncome)
    # actions = [settle_income, mark_question, unmark_question]
    search_fields = ['order_no', 'account_no', ]
    list_filter = ['status', 'has_doubt', 'code']
    date_hierarchy = 'create_time'


def send_message_for_shopkeeper(uid):
    import urllib2
    import urllib

    # body = self.body.split(":")
    # credit = body[1].strip()
    # 定义一个要提交的数据数组(字典)
    data = {}
    data['uid'] = uid
    # data['integral'] = credit
    # 定义post的地址
    # local test server
    # url = 'http://192.168.10.132:5000/itravelbuy-api/onInformCheckShopkeeper?%s'
    # remote test server
    # url = 'http://test2.itravelbuy.twohou.com/itravelbuy-api/onInformCheckShopkeeper?%s'
    # product server
    url = 'http://abuhome.podinns.com/itravelbuy-api/onInformCheckShopkeeper?%s'
    get_data = urllib.urlencode(data)
    # 提交，发送数据
    req = urllib2.urlopen(url % get_data)
    # 获取提交后返回的信息
    content = req.read()

    return


# def bd_put_offshelf_shop(productid):
#     """
#     内部调用，下架商品
#     :param:
#         - [productid], 必选，商品代码
#     :return:
#         成功，返回0
#         失败，返回1
#     """
#     try:
#         products = SaleShopProduct.objects.filter(productid=productid)
#         for product in products:
#             product.put_offshelf()
#     except:
#         return 1
#
#     return 0
#
#
# def bd_put_onshelf_shop(productid):
#     """
#     内部调用，下架商品
#     :param:
#         - [productid], 必选，商品代码
#     :return:
#         成功，返回0
#         失败，返回1
#     """
#     try:
#         products = SaleShopProduct.objects.filter(productid=productid)
#         for product in products:
#             product.put_onshelf()
#     except:
#         return 1
#
#     return 0


admin.site.register(SaleShop, SaleShopAdmin)
admin.site.register(SaleShopProduct, SaleShopProductAdmin)
admin.site.register(ShopkeeperInfo, ShopkeeperInfoAdmin)
admin.site.register(ShopManagerInfo, ShopManagerInfoAdmin)
admin.site.register(SaleShopIncome, SaleShopIncomeAdmin)

store_site.register(SaleShop, SaleShopAdmin)
store_site.register(SaleShopProduct, SaleShopProductAdmin)
store_site.register(ShopkeeperInfo, ShopkeeperInfoAdmin)
store_site.register(ShopManagerInfo, ShopManagerInfoAdmin)
store_site.register(SaleShopIncome, SaleShopIncomeAdmin)
