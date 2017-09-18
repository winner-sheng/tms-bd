# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.decorators.cache import cache_page

from .models import Banner, District
from util.renderutil import now, json_response
from tms import settings
from django.db.models import Q
from django.forms.models import model_to_dict
import time
import urlparse
import hashlib
from django.core.urlresolvers import reverse


def index(request):
    """
    转到首页，默认为app首页
    """
    return HttpResponseRedirect('/tms/login')


# @cache_page(30, key_prefix="tms.api")
# def get_home(request):
#     """
#     获取首页配置信息，如Banner，导航图标等
#     :param request:
#         [scenario], 可选，场景，获取指定场景的首页配置
#     :return:
#     返回以下格式数据
#         {
#             banners: [
#                 {
#                     image: "http://7xs6ch.com2.z0.glb.qiniucdn.com/static/2016/08/12/0bbdef18d353f69dc0021442ed3ba002.png",
#                     link_to: "",
#                     subject: "主题",
#                     list_order: 0
#                 }
#             ]
#         }
#     eg. <a href="/tms-api/get_home">查看样例</a>
#     """
#     # from util import jsonall
#     # print jsonall.json_encode(request.POST)
#     scenario = request.GET.get('scenario')
#     results = {
#         'banners': Banner.get_banners(scenario),
#         # 'channels': Channel.get_channels(),
#         # 'products': []
#     }
#     return json_response(results)


@cache_page(30, key_prefix="tms.api")
def get_navilinks(request):
    """
    获取首页配置信息，如Banner，导航图标等
    :param request:
        - [scenario], 可选，场景，获取指定场景的首页配置，多种场景可用英文逗号分隔（定义场景时不可包含逗号）
        - [owner], 可选，归属，默认为空（即归属系统设置）
            如果是用户相关的设置，owner可以是"uid:<uid>"，
            如果是供应商相关的设置，owner可以是"sup:<supplier_id>"
    :return:
    返回以下格式数据
        [
            {
                image: "http://7xs6ch.com2.z0.glb.qiniucdn.com/static/2016/08/12/0bbdef18d353f69dc0021442ed3ba002.png",
                link_to: "",
                subject: "主题",
                list_order: 0
            }
        ]
    eg. <a href="/tms-api/get_navilinks">查看样例</a>
    """
    results = []
    scenario = request.REQUEST.get('scenario')
    owner = request.REQUEST.get('owner')
    cur_time = now(settings.USE_TZ)
    banners = Banner.objects.filter(is_active=True, effective_date__lt=cur_time)
    if scenario is None:
        banners = banners.filter(Q(scenario__isnull=True) | Q(scenario=''))
    else:
        if ',' in scenario:
            banners = banners.filter(scenario__in=scenario.split(','))
        else:
            banners = banners.filter(scenario=scenario)

    if owner is None:
        banners = banners.filter(Q(owner__isnull=True) | Q(owner=''))
    else:
        banners = banners.filter(owner=owner)

    for banner in banners:
        b = model_to_dict(banner, fields=('subject', 'scenario', 'owner', 'link_to', 'list_order'))
        b['image'] = banner.image.large
        results.append(b)

    return json_response(results)


# @cache_page(30, key_prefix="tms.api")
# def get_article(request):
#     """
#     获取文章列表，或指定id的文章详情
#     :param request:
#         - [id], 可选，文章的id
#         - [tags]，可选，获取包含指定tag的文章列表，如果多个tag，可用","（需同时包含所有tag）或"|"（只需包含其中一个tag）分隔
#         - [pos], 可选，获取的结果可能存在多页时，给定开始选取的位置，默认为0
#         - [size], 可选，获取的结果可能存在多页时，确定返回每页记录数，默认为4
#         - [detail], 可选，只要带上该参数，则返回"文章"的详细信息（主要是content属性），无需有值。
#     :return:
#         - 返回数组：
#         如果参数不包含detail，则返回简单格式的结果：
#         [
#             {
#                 link_to: "",
#                 list_order: 0,
#                 tags: "test,test3",
#                 brief: "摘要，简述",
#                 subject_image: "http://7xs6ch.com2.z0.glb.qiniucdn.com/static/2016/08/17/ooopic_1426320399.png",
#                 id: 2,
#                 subject: "测试文章2"
#             }
#         ]
#         如果参数包含detail，则返回文章详情
#         [
#             {
#                 link_to: "" （链接目标地址，留空默认是文章详情页，也可能额外指定）,
#                 subject_image: "http://7xs6ch.com2.z0.glb.qiniucdn.com/static/images/2015/07/13/father2015.jpg" （“文章”的主题Banner图片，用于“文章”列表）,
#                 id: 3,
#                 subject: "父爱如山，给父亲最好的礼物" （主题）,
#                 tags: "父亲节,礼物",
#                 brief: "摘要，简述",
#                 effective_date: "2015-07-13 07:52:00" （生效日期，获取详情时才有）,
#                 content: "&lt;p&gt;深沉内敛的父亲也希望得到你的祝福呢&lt;/p&gt;..." (“文章”详情说明，可以是HTML),
#                 content_image: "" （“文章”详情的主题Banner图片，用于“文章”详情页，默认为空，即与subject_image相同））,
#             }
#         ]
#
#     eg. <a href="/tms-api/get_article">查看样例</a>
#     """
#     results = []
#     try:
#         article_id = int(request.REQUEST.get('id', '0'))
#         if article_id > 0:
#             article = Article.objects.get(id=article_id)
#             # d = model_to_dict(article, exclude=('list_order', 'subject_image_id', 'content_image_id',
#             #                                       'is_active'))
#             # d['subject_image'] = article.subject_image.origin.url if article.subject_image else ''
#             # d['content_image'] = article.content_image.origin.url if article.content_image else ''
#             results = [article.to_dict(detail=True)]
#         else:
#             cur_time = now(settings.USE_TZ)
#             articles = Article.objects.filter(is_active=True, effective_date__lt=cur_time)
#             tags = request.REQUEST.get('tags')
#             if tags:
#                 use_or = '|' in tags
#                 tags_list = tags.split('|') if use_or else tags.split(',')
#                 tags_filter = Q(tags__inset=tags_list[0])
#                 for tag in tags_list[1:]:
#                     if use_or:
#                         tags_filter |= Q(tags__inset=tag)
#                     else:
#                         tags_filter &= Q(tags__inset=tag)
#                 articles = articles.filter(tags_filter)
#             start_pos = int(request.REQUEST.get('pos', 0))
#             page_size = int(request.REQUEST.get('size', 4))
#             # page_size = page_size if 2 < page_size < 20 else 20 if page_size >= 20 else 2
#             if request.REQUEST.get('page'):
#                 start_pos = int(request.REQUEST.get('page')) * page_size
#             detail = 'detail' in request.REQUEST
#             articles = articles[start_pos:start_pos+page_size]
#             for article in articles:
#                 # if detail:
#                 #     d = model_to_dict(article, exclude=('list_order', 'subject_image_id', 'content_image_id',
#                 #                                           'is_active'))
#                 #     d['content_image'] = article.content_image.origin.url if article.content_image else ''
#                 # else:
#                 #     d = model_to_dict(article, fields=('id', 'subject', 'link_to'))
#                 # d['subject_image'] = article.subject_image.origin.url if article.subject_image else ''
#                 results.append(article.to_dict(detail))
#     except Article.DoesNotExist:
#         pass
#
#     return json_response(results)


def get_auth_url(url, token, timeout=300):
    deadline = int(time.time()) + timeout
    if '?' in url:
        url += '&'
    else:
        url += '?'
    url = "%se=%s" % (url, str(deadline))
    tokenized = hashlib.md5(url+token).hexdigest()
    return "%s&token=%s" % (url, tokenized)


def validate_auth_url(url, token):
    if not url:
        return False
    url_parsed = urlparse.urlparse(url)
    query_parsed = urlparse.parse_qs(url_parsed.query)
    if 'token' not in query_parsed or 'e' not in query_parsed \
            or not query_parsed.get('token')[0] or not query_parsed.get('e')[0]:
        return False
    timeout = int(query_parsed.get('e')[0])
    if timeout < time.time():
        return False
    tokenized = hashlib.md5(url[:-39]+token).hexdigest()
    return tokenized == query_parsed.get('token')[0]


# @cache_page(30, key_prefix="tms.api")
def show_api_helper(request):
    """
    输出API帮助信息
    :param request:
    :return:

    eg. <a href="/tms-api">查看样例</a>
    """
    from basedata.views import get_product, query_products, query_distributes, make_product, update_product,\
        add_to_cart, remove_cartitem, clear_cartitem, get_shopcart, update_cartitem, get_categories, \
        update_stock_volume, update_logistic, set_shelf, update_product_price, create_product_for_ls, mark_selected_cartitem
    from basedata.orderviews import get_order, query_orders, query_orders_with_reward, make_order, pay_order, \
        revoke_order, del_order, query_ship, set_ship_addr, set_invoice, set_order_note, update_ship_address_order,\
        request_refund, mark_refunded, use_coupon, unuse_coupon, ship_signoff, pre_order, transfer_order  # update_ship_status
    from profile.views import get_user, update_user, bind_user, unbind_user, \
        get_ship_addr, add_ship_addr, del_ship_addr, update_ship_addr, query_accounts, get_accounts_summary, \
        get_supplier_accounts_summary, get_capital_accounts, bind_capital_account, unbind_capital_account, \
        request_withdraw, confirm_withdraw, query_withdraw_request, result_withdraw, result_audit_withdraw, \
        deduct, thanksgiving, review_org, \
        register_user, register_org, query_users, query_orgs, update_org, add_link, del_link, set_org_role, \
        bd_get_store_summary, bd_query_accounts, bd_get_account_summary_all_staff
    from vendor.views import get_supplier, query_suppliers, query_logistic_vendors, create_store, query_stores, \
        query_supplier_incomes, get_brands, get_hotel, query_hotels, get_notice, update_notice, query_agents
    from promote.views import query_rewards, transfer_reward, get_rewards_summary, is_coupon_ok, fetch_coupons, \
        query_coupon_rules, query_coupons, use_haoli_coupon, get_coupon_ruleset, bd_get_rewards_summary, \
        bd_query_rewards
    from log.views import mark_wechat_msg, query_wechat_msg, wechat_to, email_to
    from report.views import get, query, feedback, order_periodical_summary
    from article.views import get_article_categories, get_article, update_article
    from credit.views import get_credit_summary, query_credits, set_credit, get_medals, set_medal
    from buding.views import bd_query_shops, bd_register_shop, bd_register_shopkeeper, bd_update_shop, \
        bd_update_shopkeeper, bd_get_shopkeeper, bd_query_products, bd_get_saleshop, bd_register_employee, \
        bd_put_offshelf, bd_put_onshelf, bd_delete_shopproduct, bd_get_user, bd_update_product, bd_getusersfromshop, \
        bd_deleteuserfromshop
    from config.views import get_appsettings

    api_group = (
        ('商品管理', [
            get_product, query_products, query_distributes, get_categories, get_brands, update_product_price,
            create_product_for_ls, make_product, update_product,
            ],),
        ('购物车管理', [
            get_shopcart, add_to_cart, remove_cartitem, clear_cartitem, update_cartitem, mark_selected_cartitem,
            ],),
        ('订单管理', [
            get_order, query_orders, query_orders_with_reward, make_order, pay_order, revoke_order, del_order,
            query_ship, set_order_note, request_refund, mark_refunded, ship_signoff, pre_order, set_invoice,
            transfer_order, update_ship_address_order,
            ],),
        ('个人/企业信息管理', [
            get_user, update_user, get_ship_addr, add_ship_addr, del_ship_addr, update_ship_addr, set_ship_addr,
            register_user, register_org, query_users, query_orgs, update_org, add_link, del_link, set_org_role,
            review_org
            ],),
        ('资金/收益管理', [
            get_capital_accounts, bind_capital_account, unbind_capital_account, request_withdraw, result_audit_withdraw,
            confirm_withdraw, query_withdraw_request, result_withdraw, deduct, query_rewards, transfer_reward,
            get_rewards_summary, query_accounts, get_accounts_summary, thanksgiving
            ],),
        ('积分/勋章管理', [
            get_credit_summary, query_credits, set_credit, get_medals, set_medal,
            ],),
        ('供应商相关', [
            get_supplier, query_suppliers, query_logistic_vendors, update_stock_volume, update_logistic,
            set_shelf, bind_user, unbind_user, query_supplier_incomes, get_supplier_accounts_summary,
            get_notice, update_notice,
            ],),
        ('酒店/民宿相关', [
            get_hotel, query_hotels,
            ],),
        ('店铺相关', [create_store, query_stores, ],),
        ('渠道相关', [query_agents, order_periodical_summary, ],),
        ('优惠券相关', [is_coupon_ok, fetch_coupons, query_coupon_rules, get_coupon_ruleset,
                   query_coupons, use_coupon, unuse_coupon, use_haoli_coupon],),
        ('消息相关', [mark_wechat_msg, query_wechat_msg, wechat_to, email_to] ),
        ('报表相关', [get, query, feedback, order_periodical_summary] ),
        ('文章/链接相关', [get_article_categories, get_article, get_navilinks, update_article] ),
        ('配置/设置相关', [get_appsettings] ),
        ('PODINNS相关', [
            bd_query_shops, bd_register_shop, bd_register_shopkeeper, bd_update_shop, bd_update_shopkeeper,
            bd_get_shopkeeper, bd_query_products, bd_get_saleshop, bd_register_employee, bd_put_offshelf,
            bd_put_onshelf, bd_delete_shopproduct, bd_get_user, bd_get_store_summary, bd_query_accounts,
            bd_get_rewards_summary, bd_query_rewards, bd_get_account_summary_all_staff, bd_update_product,
            bd_getusersfromshop, bd_deleteuserfromshop
            ],),
    )
    # print get_company.func_name, get_company.func_doc
    api_dict = []
    for k, v in api_group:
        api_list = []
        for api in v:
            api_list.append((api.func_name, api.func_doc, reverse(api)))
        api_list.sort()
        api_dict.append((k, api_list, ))
    return render_to_response('api.html', {'api_dict': api_dict})


@cache_page(30, key_prefix="tms.api")
def get_district(request):
    """
    获取地区列表
    :param request (GET):
     - level, 级别, 默认为1，返回省/直辖市/自治区一级地区列表
     - up_id, 上级id
     - [ignore_no_product], 可选，如果设为1则忽略没有对应上架商品的省份，仅当level为1时有效
    :return:
        返回数组[{up_id: 1, id: 2, name: "北京"}]

    eg. <a href='/tms-api/get_district?level=1'>查看样例</a>
    """
    from basedata.models import Product
    level = request.REQUEST.get("level", "1")
    results = District.get_districts(level, request.REQUEST.get("up_id"))
    if level == '1' and '1' == request.REQUEST.get('ignore_no_product'):
        prd_provinces = Product.objects.filter(status=Product.STATUS_ONSHELF).distinct().order_by('origin_province').values_list('origin_province')
        prd_provinces = set([p[0] for p in prd_provinces if p[0]])
        results = [d for d in results if d['name'] in prd_provinces]
    return json_response(results)


def get_appsettings(request):
    """
    获取系统设置/配置值
    :param request (GET):
    :return:

            CATEGORIES = (
                ('app', '全局'),
                ('activity', '活动相关'),
                ('callback', '回调URL'),
                ('payment', '支付参数'),
            )
            CHAR_TYPE = 0
            INT_TYPE = 1
            FLOAT_TYPE = 2
            HTML_TYPE = 8
            JSON_TYPE = 9
            VALUE_TYPES = (
                (CHAR_TYPE, '字符型'),
                (INT_TYPE, '整形数值'),
                (FLOAT_TYPE, '浮点数值'),
                (HTML_TYPE, 'HTML格式'),
                (JSON_TYPE, 'JSON格式'),
            )

    [
        {
            "category": "app",
            "name": "default_reward_rate_for_local",
            "value": "1",
            "value_type": 2,
            "usage": "本地配送商品平台抽佣百分比，客户端新建商品时，在结算价中直接扣除",
            "id": 17
        },
        {
            "category": "app",
            "name": "forward_reward_rate",
            "value": "5",
            "value_type": 2,
            "usage": "转发收益比率，0: 表示活动停止，1,2,3...: 表示转发收益提成的%比率（商品价格），将从导游收益中扣除，转换为土猴币（100币=1元）发放给商品转发者",
            "id": 18
        },
        {
            "category": "app",
            "name": "supplier_income_deferred_days",
            "value": "15",
            "value_type": 1,
            "usage": "供应商收入冻结天数",
            "id": 19
        },
        {
            "category": "app",
            "name": "reward_zhiyingdian",
            "value": "40",
            "value_type": 1,
            "usage": "直营店默认分润比例。40表示店员收益比例是的40%，店长收益60%。",
            "id": 20
        },
        {
            "category": "app",
            "name": "reward_jiamengdian",
            "value": "0",
            "value_type": 1,
            "usage": "加盟店默认分润比例。0表示店员没有收益，店长得全部收益。",
            "id": 21
        }
    ]
    eg. <a href='/tms-api/get_appsettings'>查看样例</a>
    """
    from config.models import AppSetting
    results = AppSetting.objects.all()
    return json_response(results)

# def flush_cache(request):
#     if request.user.is_superuser:
#         cache
#     else:
#         return report_error('无权操作')