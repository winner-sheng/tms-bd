# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from util.renderutil import report_error, json_response
from django.core.exceptions import ObjectDoesNotExist
from buding.models import *
from django.shortcuts import render
# Create your views here.
from profile.views import get_user_by_uid
from basedata.models import Product


def bd_get_user(request):
    """
    取某个uid所在的店长/店员信息
    :param request (POST):
        - [uid], 必选，用户UID
    :return:
        ROLE_SHOPSTORE_STAFF = 0
        ROLE_SHOPSTORE_MANAGER = 1
        ROLE_SHOPSTORE_OWNER = 2
        ROLE_SHOPSTORE_TYPES = (
            (ROLE_SHOPSTORE_STAFF, '员工'),
            (ROLE_SHOPSTORE_MANAGER, '经理'),
            (ROLE_SHOPSTORE_OWNER, '店主'),
        )
        成功，返回用户jason
        [
            {
                "update_time": null,
                "uid": "07913a02c3e9498bb8968cb725dfdfb5",
                "mobile": "18601701234",
                "is_active": true,
                "shopcode": "S8496051",
                "pid": "a657373d5de845be920c1809c186dd3c",
                "truename": "盛哲",
                "create_time": "2017-07-20 17:24:19",
                "role": 0,
                "wx_openid": "0123456789",
                "create_by": null,
                "id": 3
            },
            {
                "update_time": null,
                "uid": "07913a02c3e9498bb8968cb725dfdfb5",
                "mobile": "18601701234",
                "is_active": true,
                "shopcode": "S9461537",
                "pid": "a657373d5de845be920c1809c186dd3c",
                "truename": "盛哲",
                "create_time": "2017-07-20 17:32:26",
                "role": 0,
                "wx_openid": "0123456789",
                "create_by": null,
                "id": 4
            }
        ]
        失败返回错误提示{"error": "msg"}
        eg. <a href="/tms-api/bd_get_user">查看样例</a>
    """
    # req = request.POST if 'POST' == request.method else request.GET
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号！')

    try:
        users = ShopManagerInfo.objects.filter(uid=user.uid)
    except ObjectDoesNotExist:
        return renderutil.report_ok()
    return renderutil.json_response(users)


def bd_getusersfromshop(request):
    """
    取某家店的所有店主/店长/店员信息
    :param request (POST):
        - [uid], 必选，用户uid
        - [shopcode], 必选，店铺代码
    :return:
        ROLE_SHOPSTORE_STAFF = 0
        ROLE_SHOPSTORE_MANAGER = 1
        ROLE_SHOPSTORE_OWNER = 2
        ROLE_SHOPSTORE_TYPES = (
            (ROLE_SHOPSTORE_STAFF, '员工'),
            (ROLE_SHOPSTORE_MANAGER, '经理'),
            (ROLE_SHOPSTORE_OWNER, '店主'),
        )
        成功，返回用户jason
        [
            {
                "update_time": null,
                "uid": "686358eac965405c9721f7ba387e037c",
                "mobile": "13482864769",
                "is_active": true,
                "shopcode": "01442494",
                "pid": null,
                "reward_percent": 75,
                "truename": "张三丰",
                "create_time": "2017-07-27 16:40:05",
                "role": 2,
                "wx_openid": "o5GrSvyu65ynqvwkK-RY1ngd6c9A",
                "create_by": null,
                "id": 2
            },
            {
                "update_time": null,
                "uid": "c3c9442971ac4b8699619ea3495db903",
                "mobile": "18601705978",
                "is_active": true,
                "shopcode": "01442494",
                "pid": "686358eac965405c9721f7ba387e037c",
                "reward_percent": 75,
                "truename": "盛哲",
                "create_time": "2017-07-28 15:47:23",
                "role": 0,
                "wx_openid": "o5GrSvzJVPMgGjrT9m-m_Psql9cw",
                "create_by": null,
                "id": 9
            }
        ]
        失败返回错误提示{"error": "msg"}
        eg. <a href="/tms-api/bd_getusersfromshop">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号')

    if not req.get('shopcode'):
        return renderutil.report_error(u'缺少参数：shopcode')
    try:
        users = ShopManagerInfo.objects.filter(shopcode=req.get('shopcode'))
    except ObjectDoesNotExist:
        return renderutil.report_ok()
    return renderutil.json_response(users)


def bd_deleteuserfromshop(request):
    """
    删除指定id的用户信息，物理删除
    :param request (POST):
        - [uid], 必选，用户uid，需店主／店长身份
        - [shopcode], 必选，店铺代码
        - [id], 必选，需要删除的用户id
    :return:
        ROLE_SHOPSTORE_STAFF = 0
        ROLE_SHOPSTORE_MANAGER = 1
        ROLE_SHOPSTORE_OWNER = 2
        ROLE_SHOPSTORE_TYPES = (
            (ROLE_SHOPSTORE_STAFF, '员工'),
            (ROLE_SHOPSTORE_MANAGER, '经理'),
            (ROLE_SHOPSTORE_OWNER, '店主'),
        )
        成功，返回ok

        失败返回错误提示{"error": "msg"}
        eg. <a href="/tms-api/bd_deleteuserfromshop">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号')

    if not req.get('shopcode'):
        return renderutil.report_error(u'缺少参数：shopcode')
    if not req.get('id'):
        return renderutil.report_error(u'缺少参数：id')
    id = int(req.get('id').strip())
    try:
        ShopManagerInfo.objects.filter(shopcode=req.get('shopcode').strip(), uid=user.uid,
                                       role__in=[ShopManagerInfo.ROLE_SHOPSTORE_OWNER,
                                                 ShopManagerInfo.ROLE_SHOPSTORE_MANAGER])[0]
    except ObjectDoesNotExist:
        return renderutil.report_error(u'错误：操作者店主或店长身份无法确认')
    try:
        ShopManagerInfo.objects.filter(id=id).delete()
    except ObjectDoesNotExist:
        return renderutil.report_error(u'错误：操作者店主或店长身份无法确认')
    return renderutil.report_ok()


def bd_put_offshelf(request):
    """
    下架商品
    :param request (POST):
        - [uid], 必选，用户UID
        - [shopcode], 必选，店铺代码，
        - [productid], 必选，商品代码
            STATUS_PRESHELF = 0
            STATUS_ONSHELF = 1
            STATUS_OFFSHELF = 2
            RECORD_STATUS = (
                (STATUS_PRESHELF, '待上架'),
                (STATUS_ONSHELF, '上架'),
                (STATUS_OFFSHELF, '已下架'),
            )
    :return:
        成功，返回jason
        {
            "status": 2,
            "update_time": "2017-07-19 15:07:34",
            "settle_price": "72.00",
            "create_by": null,
            "shopcode": "S1584390",
            "create_time": "2017-07-19 13:06:09",
            "retail_price": "88.00",
            "id": 5,
            "productid": "P17060563STAM"
        }
        失败返回错误提示{"error": "msg"}
        eg. <a href="/tms-api/bd_put_offshelf">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号！')

    if not req.get('uid'):
        return renderutil.report_error(u'缺少参数：uid！')
    if not req.get('shopcode'):
        return renderutil.report_error(u'缺少参数：shopcode！')
    if not req.get('productid'):
        return renderutil.report_error(u'缺少参数：productid！')

    try:
        ss = SaleShop.objects.get(uid=user.uid, code=req.get('shopcode'))
    except:
        return renderutil.report_error(u'没有找到相应的店铺信息！')

    try:
        product = SaleShopProduct.objects.get(shopcode=req.get('shopcode'), productid=req.get('productid'))
        product.put_offshelf()
        # product = SaleShopProduct.objects.get(shopcode=req.get('shopcode'), productid=req.get('productid'))
        # return renderutil.json_response(product)
    except:
        return renderutil.report_error(u'没有找到此店铺内的该商品信息！')

    product = SaleShopProduct.objects.get(shopcode=req.get('shopcode'), productid=req.get('productid'))
    return renderutil.json_response(product)


def bd_put_onshelf(request):
    """
    上架商品
    :param request (POST):
        - [uid], 必选，用户UID
        - [shopcode], 必选，店铺代码，
        - [productid], 必选，商品代码
            STATUS_PRESHELF = 0
            STATUS_ONSHELF = 1
            STATUS_OFFSHELF = 2
            RECORD_STATUS = (
                (STATUS_PRESHELF, '待上架'),
                (STATUS_ONSHELF, '上架'),
                (STATUS_OFFSHELF, '已下架'),
            )
    :return:
        成功，返回jason
        {
            "status": 1,
            "update_time": "2017-07-19 15:07:34",
            "settle_price": "72.00",
            "create_by": null,
            "shopcode": "S1584390",
            "create_time": "2017-07-19 13:06:09",
            "retail_price": "88.00",
            "id": 5,
            "productid": "P17060563STAM"
        }
        失败返回错误提示{"error": "msg"}
        eg. <a href="/tms-api/bd_put_onshelf">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号！')

    if not req.get('uid'):
        return renderutil.report_error(u'缺少参数：uid！')
    if not req.get('shopcode'):
        return renderutil.report_error(u'缺少参数：shopcode！')
    if not req.get('productid'):
        return renderutil.report_error(u'缺少参数：productid！')

    try:
        ss = SaleShop.objects.get(uid=user.uid, code=req.get('shopcode'))
    except:
        return renderutil.report_error(u'没有找到相应的店铺信息！')

    try:
        product = SaleShopProduct.objects.get(shopcode=req.get('shopcode'), productid=req.get('productid'))
        product.put_onshelf()
        # product = SaleShopProduct.objects.get(shopcode=req.get('shopcode'), productid=req.get('productid'))
        # return renderutil.json_response(product)
    except:
        return renderutil.report_error(u'没有找到此店铺内的该商品信息！')

    product = SaleShopProduct.objects.get(shopcode=req.get('shopcode'), productid=req.get('productid'))
    return renderutil.json_response(product)


def bd_update_product(request):
    """
    修改商品资料
    :param request (POST):
        - [uid], 必选，用户UID
        - [id], 必选
            STATUS_PRESHELF = 0
            STATUS_ONSHELF = 1
            STATUS_OFFSHELF = 2
            RECORD_STATUS = (
                (STATUS_PRESHELF, '待上架'),
                (STATUS_ONSHELF, '上架'),
                (STATUS_OFFSHELF, '已下架'),
            )
        - status, 状态
        - retail_price, 零售价
        - settle_price, 结算价
        - tags, 标签
        - list_order, 排序值

    :return:
        成功，返回jason
        {
            "status": 2,
            "update_time": "2017-08-21 11:50:48",
            "settle_price": "76.00",
            "tags": null,
            "create_by": null,
            "shopcode": "03003524",
            "create_time": "2017-08-10 19:49:55",
            "list_order": "101",
            "retail_price": "101.00",
            "id": 32319,
            "productid": "P170518BDKRXL"
        }
        失败返回错误提示{"error": "msg"}
        eg. <a href="/tms-api/bd_update_product">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号！')

    if not req.get('id'):
        return renderutil.report_error(u'缺少参数：id')
    # if not req.get('shopcode'):
    #     return renderutil.report_error(u'缺少参数：shopcode')
    # if not req.get('productid'):
    #     return renderutil.report_error(u'缺少参数：productid')

    # try:
    #     ss = SaleShop.objects.get(id=req.get('id'))
    # except:
    #     return renderutil.report_error(u'没有找到相应的店铺信息！')

    try:
        product = SaleShopProduct.objects.get(id=req.get('id'))
        if req.get('status'):
            product.status = int(req.get('status'))
        if req.get('retail_price'):
            product.retail_price = req.get('retail_price')
        if req.get('settle_price'):
            product.settle_price = req.get('settle_price')
        if req.get('tags'):
            product.tags = req.get('tags').strip()
        if req.get('list_order'):
            product.list_order = req.get('list_order')
        product.update_time = now(settings.USE_TZ)
        product.save()
            # product = SaleShopProduct.objects.get(shopcode=req.get('shopcode'), productid=req.get('productid'))
        return renderutil.json_response(product)
    except:
        return renderutil.report_error(u'没有找到该商品的纪录！')

    # product = SaleShopProduct.objects.get(shopcode=req.get('shopcode'), productid=req.get('productid'))
    # return renderutil.json_response(product)


def bd_delete_shopproduct(request):
    """
    删除商品
    :param request (POST):
        - [uid], 必选，用户UID
        - [shopcode], 必选，店铺代码，
        - [productid], 必选，商品代码
    :return:
        成功，返回 ok
        失败返回错误提示{"error": "msg"}
        eg. <a href="/tms-api/bd_delete_shopproduct">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号！')

    if not req.get('uid'):
        return renderutil.report_error(u'缺少参数：uid！')
    if not req.get('shopcode'):
        return renderutil.report_error(u'缺少参数：shopcode！')
    if not req.get('productid'):
        return renderutil.report_error(u'缺少参数：productid！')

    try:
        ss = SaleShop.objects.get(uid=user.uid, code=req.get('shopcode'))
    except:
        return renderutil.report_error(u'没有找到相应的店铺信息！')

    try:
        product = SaleShopProduct.objects.get(shopcode=req.get('shopcode'), productid=req.get('productid'))
        product.delete()
        # product = SaleShopProduct.objects.get(shopcode=req.get('shopcode'), productid=req.get('productid'))
        # return renderutil.json_response(product)
    except:
        return renderutil.report_error(u'没有找到此店铺内的该商品信息！')

    # product = SaleShopProduct.objects.get(shopcode=req.get('shopcode'), productid=req.get('productid'))
    return renderutil.report_ok()


def bd_register_employee(request):
    """
    注册店长/店员
    :param request (POST):
        - [uid], 必选，用户UID
        - [mobile], 必选，用户手机，
        - [wx_openid], 必选，微信openid
        - [truename], 必选，真实姓名
        - [shopcode], 必选
        - [role], 必选，
        - [pid], 可选，
            ROLE_SHOPSTORE_STAFF = 0
            ROLE_SHOPSTORE_MANAGER = 1
            ROLE_SHOPSTORE_TYPES = (
                (ROLE_SHOPSTORE_STAFF, '员工'),
                (ROLE_SHOPSTORE_MANAGER, '经理'),
                )
    :return:
        创建成功，返回用户jason
            {
                "update_time": null,
                "uid": "07913a02c3e9498bb8968cb725dfdfb5",
                "mobile": "18601701234",
                "is_active": true,
                "shopcode": "S5671234",
                "pid": "07913a02c3e9498bb8968cb725dfdfb5",
                "truename": "盛哲",
                "create_time": "2017-07-19 09:38:13",
                "role": "1",
                "wx_openid": "0123456789",
                "create_by": null,
                "id": 1
            }
        失败返回错误提示{"error": "msg"}
        eg. <a href="/tms-api/bd_register_employee">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号！')

    if not req.get('uid'):
        return renderutil.report_error(u'缺少参数：uid！')
    if not req.get('wx_openid'):
        return renderutil.report_error(u'缺少参数：wx_openid！')
    if not req.get('truename'):
        return renderutil.report_error(u'缺少参数：truename！')
    if not req.get('mobile'):
        return renderutil.report_error(u'缺少参数：mobile！')
    if not req.get('shopcode'):
        return renderutil.report_error(u'缺少参数：shopcode！')
    if not req.get('role'):
        return renderutil.report_error(u'缺少参数：role！')

    attributes = ['uid', 'wx_openid', 'truename', 'mobile', 'shopcode', 'pid']

    # try:
    if ShopManagerInfo.objects.filter(uid=req.get('uid'), shopcode=req.get('shopcode')).exists():
    # if ShopManagerInfo.objects.filter(uid=req.get('uid'), shopcode=req.get('shopcode'), role=req.get('role')).exists():
    # if user:
        return renderutil.report_error(u'该用户已存在，不能重复添加！')
    else:
        employee = ShopManagerInfo()
        for attr in attributes:
            if req.get(attr):
                setattr(employee, attr, req.get(attr).strip())
        employee.role = 0 if req.get('role') in [0, '0'] else 1
        employee.save()

        # return json_response({'uid': employee.uid})
        return renderutil.json_response(employee)


def bd_get_saleshop(request):
    """
    查询店铺商品信息
    :param request (POST):
        - 'code', 必选，店铺code
    :return:
        成功，返回
         {
            "province": "江苏",
            "city": "苏州",
            "update_time": "2017-07-13 22:54:29",
            "code": "S1584390",
            "name": "盛哲的小店",
            "district": null,
            "shopicon": null,
            "create_by": null,
            "cover": null,
            "state": 0,
            "shop_type": 0,
            "create_time": "2017-07-13 22:46:07",
            "watchcount": 0,
            "address": null,
            "qrcode": null,
            "keeperqrcode": null,
            "uid": "07913a02c3e9498bb8968cb725dfdfb5"
        }
       失败返回错误提示{"error": "msg"}

    eg. <a href="/tms-api/bd_get_saleshop">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    code = req.get('code')
    if not code:
        return renderutil.report_error(u'缺少参数：code！')

    if SaleShop.objects.filter(code=code).exists():
        ss = SaleShop.objects.get(code=code)
        return renderutil.json_response(ss)
    else:
        return renderutil.report_error(u'没有找到这个代码[%s]的店铺' % code)


def bd_query_products(request):
    """
    查询店铺商品信息
    :param request (POST):
        - 'code', 必选，店铺code
        - [status], 可选，商品状态，没有此参数也表示'all'，包括：
            0, '待上架/待审核'
            1, '上架' (默认值)
            2, '已下架'
            "all", 所有状态
    :return:
        成功，返回
        {
            "products": [
                {
                    "status": 2,
                    "settle_price": "76.00",
                    "list_order": 0,
                    "shopcode": "S9461537",
                    "retail_price": "90.00",
                    "id": 32325,
                    "tags": null,
                    "productid": "P170518BDKRXL"
                },
                {
                    "status": 2,
                    "settle_price": "98.00",
                    "list_order": 0,
                    "shopcode": "S9461537",
                    "retail_price": "128.00",
                    "id": 32332,
                    "tags": null,
                    "productid": "P160519MBPZTK"
                },
            ]
        }
        失败返回错误提示{"error": "msg"}

    eg. <a href="/tms-api/bd_query_products">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    code = req.get('code')
    if not req.get('code'):
        return renderutil.report_error(u'缺少参数：code！')

    res = []
    if SaleShop.objects.filter(code=code).exists():
        ss = SaleShop.objects.get(code=code)
        if ss.state == SaleShop.STATUS_SHOPSTORE_IS_OPEN:
            sps = SaleShopProduct.objects.filter(shopcode=req.get('code'))
            status = req.get('status', 'all')
            if 'all' == status:
                pass
            elif status in ('0', '1', '2'):
                sps = sps.filter(status=status)
            else:
                sps = sps.filter(status=SaleShopProduct.STATUS_ONSHELF)  # default on shelf
            for sp in sps:
                res.append(sp.to_dict())
            return renderutil.json_response({'products': res})
        elif ss.state == SaleShop.STATUS_SHOPSTORE_IS_CLOSED:
            return renderutil.report_error(u'该店铺停业中！')
        elif ss.state == SaleShop.STATUS_SHOPSTORE_WATTING_FOR_APPLY:
            return renderutil.report_error(u'该店铺还未通过审核！')
        else:
            return renderutil.report_error(u'未知的错误！')
    else:
        return renderutil.report_error(u'没有找到这个代码[%s]的店铺' % code)


def bd_register_shopkeeper(request):
    """
    注册新店主
    :param request (POST):
        - [uid],
        - [mobile], 用户手机，必须唯一（必须通过短信验证码验证有效）
        - [wx_openid], 必选，微信openid
        - [truename], 必选，真实姓名
        - [city], 可选
        - [photo], 可选，身份证正面照片链接
        - [photoReverse], 可选，身份证背面照片链接
        - [id_card], 可选，身份证号
        - [state], 可选，状态，0, 1, 2
            STATUS_AUDITING_TYPES = (
                (STATUS_AUDITING_WAITTING, '待审核'),
                (STATUS_AUDITING_APPLYED, '审核通过'),
                (STATUS_AUDITING_REJECTED, '审核不通过'),
            )

    :return:
        创建成功，返回用户jason
            {
                "city": "浙江",
                "update_time": "2017-07-13 23:09:28",
                "rejectmessage": null,
                "uid": "07913a02c3e9498bb8968cb725dfdfb5",
                "mobile": "18601705978",
                "photo": "",
                "id_card": "310228197110202810",
                "truename": "盛哲",
                "state": 1,
                "create_time": "2017-07-13 15:01:46",
                "wx_openid": "0123456789",
                "create_by": null,
                "photoReverse": "",
                "id": 1
            }
        失败返回错误提示{"error": "msg"}

    eg. <a href="/tms-api/bd_register_shopkeeper">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号')

    if req.get('mobile'):
        if ShopkeeperInfo.objects.filter(mobile=req.get('mobile').strip()).exists():  # 手机号唯一
            return renderutil.report_error('手机号[%s]已注册店主身份，不可重复注册' % req.get('mobile'))
    else:
        return renderutil.report_error(u'缺少参数：mobile')

    if req.get('uid'):
        if ShopkeeperInfo.objects.filter(mobile=req.get('uid').strip()).exists():  # uid唯一
            return renderutil.report_error('uid[%s]已注册店主身份，不可重复注册' % req.get('uid'))
    else:
        return renderutil.report_error(u'缺少参数：uid')

    if req.get('wx_openid'):
        if ShopkeeperInfo.objects.filter(mobile=req.get('wx_openid').strip()).exists():  # openid唯一
            return renderutil.report_error('wx_openid[%s]已注册店主身份，不可重复注册' % req.get('wx_openid'))
    else:
        return renderutil.report_error(u'缺少参数：wx_openid')

    if not req.get('truename'):
        return renderutil.report_error(u'缺少参数：truename')

    shopkeeper = ShopkeeperInfo()
    attributes = ['uid', 'mobile', 'wx_openid', 'truename', 'city', 'photo', 'photoReverse', 'id_card',
                  'rejectmessage', 'state']
    for attr in attributes:
        if req.get(attr):
            setattr(shopkeeper, attr, req.get(attr).strip())
    shopkeeper.save()

    # return json_response({'uid': shopkeeper.uid})
    return renderutil.json_response(shopkeeper)


def bd_update_shopkeeper(request):
    """
    修改店主信息
    :param request (POST):
        - [uid], 必选
        - [mobile], 必选，用户手机，必须唯一（必须通过短信验证码验证有效）
        - [wx_openid], 必选，微信openid
        - [truename], 必选，真实姓名
        - [city], 可选
        - [photo], 可选，身份证正面照片链接
        - [photoReverse], 可选，身份证背面照片链接
        - [id_card], 可选，身份证号
        - [state], 可选，状态, 0, 1, 2
            STATUS_AUDITING_TYPES = (
                (STATUS_AUDITING_WAITTING, '待审核'),
                (STATUS_AUDITING_APPLYED, '审核通过'),
                (STATUS_AUDITING_REJECTED, '审核不通过'),
            )

    :return:
        创建成功，返回用户jason
            {
                "city": "浙江",
                "update_time": "2017-07-13 23:09:28",
                "rejectmessage": null,
                "uid": "07913a02c3e9498bb8968cb725dfdfb5",
                "mobile": "18601705978",
                "photo": "",
                "id_card": "310228197110202810",
                "truename": "盛哲",
                "state": 1,
                "create_time": "2017-07-13 15:01:46",
                "wx_openid": "0123456789",
                "create_by": null,
                "photoReverse": "",
                "id": 1
            }
        失败返回错误提示{"error": "msg"}

    eg. <a href="/tms-api/bd_register_shopkeeper">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号！')
    if req.get('mobile'):
        if ShopkeeperInfo.objects.filter(mobile=req.get('mobile').strip()).exists():  # 手机号唯一
            return renderutil.report_error('手机号[%s]已注册店主身份，不可重复注册！' % req.get('mobile'))

    if req.get('uid'):
        if ShopkeeperInfo.objects.filter(mobile=req.get('uid').strip()).exists():  # uid唯一
            return renderutil.report_error('uid[%s]已注册店主身份，不可重复注册' % req.get('uid'))
    else:
        return renderutil.report_error(u'缺少参数：uid')

    if req.get('wx_openid'):
        if ShopkeeperInfo.objects.filter(mobile=req.get('wx_openid').strip()).exists():  # openid唯一
            return renderutil.report_error('wx_openid[%s]已注册店主身份，不可重复注册' % req.get('wx_openid'))
    else:
        return renderutil.report_error(u'缺少参数：wx_openid')

    shopkeeper = ShopkeeperInfo.objects.get(uid=user.uid)
    attributes = ['wx_openid', 'truename', 'city', 'photo', 'photoReverse', 'id_card',
                  'rejectmessage', 'state']
    for attr in attributes:
        if req.get(attr):
            setattr(shopkeeper, attr, req.get(attr).strip())
    shopkeeper.update_time = now(settings.USE_TZ)
    shopkeeper.save()

    return renderutil.json_response(shopkeeper)


def bd_get_shopkeeper(request):
    """
    获取店主信息
    :param request (POST):
        - [uid], 必选
    :return:
        创建成功，返回用户jason
            {
                "city": "浙江",
                "update_time": "2017-07-13 23:09:28",
                "rejectmessage": null,
                "uid": "07913a02c3e9498bb8968cb725dfdfb5",
                "mobile": "18601705978",
                "photo": "",
                "id_card": "310228197110202810",
                "truename": "盛哲",
                "state": 1,
                "create_time": "2017-07-13 15:01:46",
                "wx_openid": "0123456789",
                "create_by": null,
                "photoReverse": "",
                "id": 1
            }
        失败返回错误提示{"error": "msg"}

    eg. <a href="/tms-api/bd_register_shopkeeper">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号！')

    if ShopkeeperInfo.objects.filter(uid=user.uid).exists():
        s = ShopkeeperInfo.objects.get(uid=user.uid)
        return renderutil.json_response(s)
    else:
        return renderutil.report_error(u'错误：此用户还未申请店主！')


def bd_register_shop(request):
    """
    注册新店铺/同时创建店主信息至店员信息表
    :param request (POST):
        'code', 必选，店铺code
        'uid', 必选，用户uid
        'name',
        'qrcode',
        'keeperqrcode',
        'shopicon',
        'cover',
        'watchcount',
        'state', 0, 1, 2
            STATUS_SHOPSTORE_TYPES = (
                (STATUS_SHOPSTORE_WATTING_FOR_APPLY, '审核中'),
                (STATUS_SHOPSTORE_IS_OPEN, '开业中'),
                (STATUS_SHOPSTORE_IS_CLOSED, '休息中'),
            )
        'shop_type', 0, 1
                TYPES_OF_SHOP = (
                    (SHOPTYPE_ZHIYINGDIAN, '直营店'),
                    (SHOPTYPE_JIAMENGDIAN, '加盟店'),
                )
        'province',
        'city',
        'district',
        'address',
    :return:
        创建成功，返回店铺jason
        {
            "province": null,
            "city": "上海",
            "update_time": "2017-07-13 17:22:05",
            "code": "S8496051",
            "name": "盛哲的小店",
            "district": null,
            "shopicon": null,
            "create_by": null,
            "cover": null,
            "state": 1,
            "shop_type": 0,
            "create_time": "2017-07-13 15:23:46",
            "watchcount": 0,
            "address": null,
            "qrcode": null,
            "keeperqrcode": null,
            "uid": "07913a02c3e9498bb8968cb725dfdfb5"
        }
        失败返回错误提示{"error": "msg"}

    eg. <a href="/tms-api/bd_register_shop">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号！')

    uid = req.get('uid')
    if uid:
        if ShopkeeperInfo.objects.filter(uid=uid).exists():
            s = ShopkeeperInfo.objects.get(uid=uid)
            if s.state != ShopkeeperInfo.STATUS_AUDITING_APPLYED:
                return renderutil.report_error(u'错误：此用户的店主申请待审核中或未通过！')
        else:
            return renderutil.report_error(u'错误：此用户还未申请店主！')
    else:
        return renderutil.report_error(u'缺少参数：uid！')

    if not req.get('code'):
        return renderutil.report_error(u'缺少参数：code！')
    if SaleShop.objects.filter(code=req.get('code')).exists():
        return renderutil.report_error(u'系统已存在此code的店铺，请检查数据！')

    if not req.get('name'):
        shop_name = s.truename + '的小店'
    else:
        shop_name = req.get('name').strip()
    if SaleShop.objects.filter(name=shop_name).exists():
        return renderutil.report_error(u'此名称的店铺已存在，请修改！')

    shop = SaleShop()
    attributes = ['code', 'uid', 'qrcode', 'keeperqrcode', 'shopicon', 'cover', 'watchcount', 'state', 'shop_type',
                  'province', 'city', 'district', 'address']
    for attr in attributes:
        if req.get(attr):
            setattr(shop, attr, req.get(attr).strip())
    # shop.uid = shopkeeper.uid
    shop.name = shop_name
    shop.state = SaleShop.STATUS_SHOPSTORE_IS_OPEN
    shop.create_time = now(settings.USE_TZ)
    shop.save()

    # 同时创建店主信息至店铺员工信息表
    # sk = ShopkeeperInfo.objects.get(uid=uid)
    shop_emp, created = ShopManagerInfo.objects.get_or_create(uid=user.uid,
                                                              role=ShopManagerInfo.ROLE_SHOPSTORE_OWNER,
                                                              wx_openid=s.wx_openid,
                                                              truename=s.truename,
                                                              mobile=s.mobile,
                                                              shopcode=req.get('code'),
                                                              pid=None,
                                                              is_active=True
                                                              )
    # 同时创建店员信息至店铺员工信息表
    # sk = ShopkeeperInfo.objects.get(uid=uid)
    # shop_emp, created = ShopManagerInfo.objects.get_or_create(uid=user.uid,
    #                                                           role=ShopManagerInfo.ROLE_SHOPSTORE_STAFF,
    #                                                           wx_openid=s.wx_openid,
    #                                                           truename=s.truename,
    #                                                           mobile=s.mobile,
    #                                                           shopcode=req.get('code'),
    #                                                           pid=None,
    #                                                           is_active=True
    #                                                           )

    # 先删除此店铺code的所有商品
    SaleShopProduct.objects.filter(shopcode=req.get('code')).delete()
    # 复制商品库中上架的商品到店铺商品库
    prds = Product.objects.all()
    # prds = Product.objects.filter(status=Product.STATUS_ONSHELF)
    for prd in prds:
        sp = SaleShopProduct()
        sp.shopcode = req.get('code')
        sp.status = prd.status
        sp.productid = prd.code
        sp.retail_price = prd.retail_price
        sp.settle_price = prd.settle_price
        sp.tags = prd.tags
        sp.list_order = prd.list_order
        sp.create_time = now(settings.USE_TZ)
        sp.save()

    # return json_response({'code': shop.code})
    return renderutil.json_response(shop)


def bd_update_shop(request):
    """
    修改店铺信息
    :param request (POST):
        'code', 必选，店铺代码
        'uid', 必选，用户uid
        'name',
        'qrcode',
        'keeperqrcode',
        'shopicon',
        'cover',
        'watchcount',
        'state', 0, 1, 2
                STATUS_SHOPSTORE_TYPES = (
                    (STATUS_SHOPSTORE_WATTING_FOR_APPLY, '审核中'),
                    (STATUS_SHOPSTORE_IS_OPEN, '开业中'),
                    (STATUS_SHOPSTORE_IS_CLOSED, '休息中'),
                )
        'shop_type', 0, 1
                TYPES_OF_SHOP = (
                    (SHOPTYPE_ZHIYINGDIAN, '直营店'),
                    (SHOPTYPE_JIAMENGDIAN, '加盟店'),
                )
        'province',
        'city',
        'district',
        'address',
    :return:
        创建成功，返回店铺jason
        {
            "province": null,
            "city": "上海",
            "update_time": "2017-07-13 17:22:05",
            "code": "S8496051",
            "name": "盛哲的小店",
            "district": null,
            "shopicon": null,
            "create_by": null,
            "cover": null,
            "state": 1,
            "shop_type": 0,
            "create_time": "2017-07-13 15:23:46",
            "watchcount": 0,
            "address": null,
            "qrcode": null,
            "keeperqrcode": null,
            "uid": "07913a02c3e9498bb8968cb725dfdfb5"
        }
        失败返回错误提示{"error": "msg"}

    eg. <a href="/tms-api/bd_update_shop">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    if not req.get('uid') or not req.get('code'):
        return renderutil.report_error(u'错误：缺少必要参数uid和code！')
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号！')

    # uid = req.get('uid')
    # if uid:
    #     if ShopkeeperInfo.objects.filter(uid=uid).exists():
    #         s = ShopkeeperInfo.objects.get(uid=uid)
    #         if s.state != ShopkeeperInfo.STATUS_AUDITING_APPLYED:
    #             return renderutil.report_error(u'错误：此用户的店主申请待审核中或未通过！')
    #         # if not req.get('name'):
    #         #     shop_name = s.truename + '的小店'
    #         # else:
    #         #     shop_name = req.get('name')
    #     else:
    #         return renderutil.report_error(u'错误：此用户还未申请店主！')
    # else:
    #     return renderutil.report_error(u'缺少参数：uid！')

    try:
        shop = SaleShop.objects.get(code=req.get('code'))
    except:
        return renderutil.report_error(u'系统中不存在此id: %s的店铺' % req.get('code'))

    if not shop:
        return renderutil.report_error(u'系统中不存在此id: %s的店铺' % req.get('code'))

    if not req.get('name'):
        # shop_name = shop.truename + '的小店'
        return renderutil.report_error(u'店铺名称为空，请提供店铺名称')
    else:
        shop_name = req.get('name').strip()
    if SaleShop.objects.filter(name=shop_name).exists():
        return renderutil.report_error(u'此名称的店铺已存在，请修改')

    try:
        s = ShopManagerInfo.objects.get(shopcode=req.get('code'), uid=user.uid)
        if s.role not in [ShopManagerInfo.ROLE_SHOPSTORE_MANAGER, ShopManagerInfo.ROLE_SHOPSTORE_OWNER]:
            return renderutil.report_error(u'用户非店主或店长身份，请确认')
    except:
        return renderutil.report_error(u'用户非店主或店长身份，请确认')

    attributes = ['qrcode', 'name', 'keeperqrcode', 'shopicon', 'cover', 'watchcount', 'state', 'shop_type',
                  'province', 'city', 'district', 'address']
    for attr in attributes:
        if req.get(attr):
            setattr(shop, attr, req.get(attr).strip())
    # shop.uid = shopkeeper.uid
    # shop.name = shop_name
    shop.update_time = now(settings.USE_TZ)
    shop.save()

    # return json_response({'code': shop.code})
    return renderutil.json_response(shop)


def bd_query_shops(request):
    """
    获取用户所拥有的店铺代码
    :param request (POST):
        'uid', 必选，用户uid
        'name', 可选，店铺名称
        'state', 可选，状态
        'shop_type', 可选，类型
        'province', 可选，省
        'city', 可选，市
        'district', 可选，区
    :return:
        返回店铺code
        {
            "shops": [
                "S1584390",
                "S5234819",
                "S8496051",
                "S9461537"
            ]
        }
    eg. <a href="/tms-api/bd_query_shops">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    if not req.get('uid'):
        return renderutil.report_error(u'错误：缺少必要参数uid！')
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号！')

    uid = req.get('uid')
    if uid:
        if ShopkeeperInfo.objects.filter(uid=uid).exists():
            s = ShopkeeperInfo.objects.get(uid=uid)
            if s.state != ShopkeeperInfo.STATUS_AUDITING_APPLYED:
                return renderutil.report_error(u'错误：此用户的店主申请待审核中或未通过！')
        else:
            return renderutil.report_error(u'错误：此用户还未申请店主！')
    else:
        return renderutil.report_error(u'缺少参数：uid！')

    shops = SaleShop.objects.filter(uid=uid)
    if req.get('province'):
        shops = shops.filter(province=req.get('province'))
    if req.get('city'):
        shops = shops.filter(city=req.get('city'))
    if req.get('district'):
        shops = shops.filter(district=req.get('district'))
    if req.get('state'):
        shops = shops.filter(state=req.get('state'))
    if req.get('name'):
        shops = shops.filter(name=req.get('name'))
    if req.get('shop_type'):
        shops = shops.filter(shop_type=req.get('shop_type'))

    shops_str = []
    for shop in shops:
        shops_str.append(shop.code)

    return renderutil.json_response({'shops': shops_str})


def send_message_for_del_product(productcode):
    import urllib2
    import urllib

    # body = self.body.split(":")
    # credit = body[1].strip()
    # 定义一个要提交的数据数组(字典)
    data = {}
    data['productcode'] = productcode
    # data['integral'] = credit
    # 定义post的地址
    # local test server
    # url = 'http://192.168.10.132:5000/itravelbuy-api/onInformCheckShopkeeper?%s'
    # remote test server
    # url = 'http://test2.itravelbuy.twohou.com/itravelbuy-api/onInformCheckShopkeeper?%s'
    # product server
    url = 'http://abuhome.podinns.com/itravelbuy-api/onInformTmsDelProduct?%s'
    get_data = urllib.urlencode(data)
    # 提交，发送数据
    req = urllib2.urlopen(url % get_data)
    # 获取提交后返回的信息
    content = req.read()

    return
