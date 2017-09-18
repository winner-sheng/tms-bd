# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.decorators.cache import cache_page
from .models import Supplier, LogisticsVendor, Store, SupplierSalesIncome, Hotel, HotelImage, \
    SupplierNotice, SalesAgent
from util.renderutil import json_response, report_error, report_ok, logger, now
from profile.views import get_user_by_uid
from django.db.models import F
from tms import Convert, settings
from django.db.models import Q
from django.shortcuts import render_to_response


# @login_required
# def agent(request):
#     store_agent = request.session.get('agent')
#     code = req.get('shopCode', '')
#     result = {'shop_code': code, 'agent': store_agent}
#     if not store_agent:
#         if not request.user.is_staff:
#             return render_to_response('403.html', {'error': '对不起，您未得到访问授权！请联系系统管理员。'})
#
#         if request.user.is_superuser:
#             store_agent = {'fullname': request.user.get_full_name() or request.user.username,
#                            'store': '总店',
#                            'store_code': '',
#                            'coupon': '无'}
#         else:
#             try:
#                 sa = StoreAgent.objects.get(user=request.user)
#                 store_agent = {'fullname': sa.user.get_full_name() or sa.user.username,
#                                'store': sa.store.name,
#                                'store_code': sa.store.code,
#                                'coupon': sa.store.coupon}
#             except ObjectDoesNotExist:
#                 return render_to_response('403.html', {'error': '对不起，您未得到访问授权！请联系系统管理员。'})
#
#         request.session['agent'] = result['agent'] = store_agent
#
#     return render_to_response('admin/agent.html', result)
from vendor.models import Brand


def create_store(request):
    """
    创建一个新店铺
    :param request (POST):
        - uid, 店主uid
        - name, 店名，唯一
        - [code], 可选，唯一，店铺编码
        - [intro, homepage, province, city, address, post_code, lng, lat, ]
    :return:
    """
    user = get_user_by_uid(request)
    if not user:
        return report_error(u'无效的用户账号')

    name = request.POST.get('name')
    if not name:
        return report_error(u'请提供店名！')

    try:
        Store.objects.get(name=name)
        return report_error(u'店名【%s】已被注册！' % name)
    except Store.DoesNotExist:
        data = {'owner_id': user.uid, "name": name}
        for attr in ['intro', 'homepage', 'province', 'city', 'address', 'post_code', 'lng', 'lat', ]:
            if attr in request.POST:
                data[attr] = request.POST.get(attr)
        try:
            return json_response(Store.objects.create(data))
        except Exception, e:
            logger.exception(e)
            return report_error(u'店铺创建失败！')


def query_stores(request):
    """
    查询店铺信息
    :param request:
        - [owner_uid], 可选，店主uid，可能一人开多店
        - [name], 可选，店名，如有多个，可用英文逗号分隔
        - [code], 可选，店铺编码，如有多个，可用英文逗号分隔
        - [province], 可选，所在省份
        - [city], 可选，所在市
        - [pos], 可选，起始偏移量，默认为0
        - [size]，可选，一次获取多少条数据，默认为10，取值范围2~20
        - [is_active], 可选，默认为1，即有效的，0为无效，all为全部
        - [since], 可选，日期时间，获取指定时间之后更新的记录
    :return:
        成功返回店铺数组,如：
            [{
                province: "",
                city: "",
                code: "7kvfNYxwergadfadsfwerq2afsf",
                name: "一羽小店",
                address: "",
                owner_uid: "7kvfNYxwergadfadsfwerq2afsf",
                id: 1
            },]
        失败返回{'error': msg}

    eg. <a href="/tms-api/query_stores">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    records = _query_business(Store, request)
    if 'owner_uid' in req:
        records = records.filter(owner_uid=req.get('owner_uid'))

    res = []
    for r in records:
        res.append(r.to_dict())
    return json_response(res)


def get_supplier(request):
    """
    根据编码获取供应商信息
    :param request:
        - id | code | name, 编码 | 名称
    :return:
        成功返回供应商对象
        {
            province: "",
            city: "",
            code: "7kvfNY",
            name: "黄凌燕",
            backup_contact: null,
            is_active: true,
            settlement: 0, 1, 2   线上结算，线下结算，其他
            lng: 0,
            homepage: "",
            lat: 0,
            intro: "",
            post_code: "",
            address: "",
            notices: [
                "供应商消息通告",
            ],
            primary_contact: {
                mobile: "12345678901",
                email: "",
                name: "黄玲燕",
                id: 1
            },
            logo: "",
            is_verified: true,
            id: 1
            capital_account: {
                bank_name: "",  （开户银行名称）
                uid: "7kvfNY",  （用户uid）
                bank_code: "",  （银行编码，一般是银行的英文缩写）
                is_default: true, （是否默认账号）
                is_valid: true,  （是否有效）
                open_bank: "",  （开户行）
                ca_desc: "",    （账户说明）
                ca_type: "wechat",  （账户类型）
                ca_no: "0ljqweLUHEWowelknfwLIJlkn",  (资金账号，微信对应的资金账号是用户的openid)
                id: 1
            },
            shipfee_desc: [
                "满88元包邮"
            ],
            shipfee_template: {`   (运费模板，当设置运费模板后，运费以此为准，否则按商品的其它设置计算)
                bill_type: 0,       （运费计费类型，0为按数量计费，1为按重量计费）
                bill_type_txt: "按数量",   （计费类型）
                free_ship_amount: 0,  （满x元包邮，0为不包邮）
                free_ship_cnt: 5,   （满x件包邮，0为不包邮，1为包邮）
                id: 1,      （模板id）
                initial_fee: 10,    （首件/首重运费）
                initial_units: 1    （首件/首重数量，即以第一个x件商品/x斤（500克）的商品计算首件/首重费用）
                is_public: true,     （是否公共模板，由系统管理员提供常见的设置作为公共模板，可用于快速克隆后修改）
                items: [    （模板配置项目）
                    {
                        areas: "浙江,江苏,上海"   （配送区域，即当前计费项设置是针对指定配送区域的）
                        free_ship_cnt: 0,    (满X件免邮)
                        free_ship_amount: 0, (满X元免邮)
                        max_freight: 50,     (邮费最高X元)
                        initial_fee: 6,     （首件/首重运费）
                        initial_units: 1,   （首件/首重数量，即以第一个x件商品/x斤（500克）的商品计算首件/首重费用）
                        second_fee: 2,      （次件/次重运费）
                        second_units: 1,    （续件/续重数量，即每x件商品/x斤（500克）为邮费计算单位）
                        ship_vendors: null,  （物流服务商编码，多个用逗号分隔，暂时保留）
                    }
                ],
                max_freight: 50,     (邮费最高X元)
                name: "计件运费",  （模板名称）
                no_ship_areas: "西藏,新疆,青海,内蒙古",  （不支持配送区域，暂只支持到省）
                second_fee: 2,      （次件/次重运费）
                second_units: 1,    （续件/续重数量，即每x件商品/x斤（500克）为邮费计算单位）
                supplier: null,     （模板所属供应商）
            },
        }
        失败返回{'error': msg}

    eg. <a href="/tms-api/get_supplier">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    code = req.get('code')
    name = req.get('name')
    sup_id = req.get('id')
    try:
        supplier = Supplier.objects
        if code:
            supplier = supplier.get(code=code)
        elif name:
            supplier = supplier.get(name=name)
        elif sup_id:
            supplier = supplier.get(id=sup_id)
        else:
            return report_error('缺少参数！')
        result = supplier.to_dict(True)
        from basedata.models import ShipFeeTemplate
        try:
            tmpl = ShipFeeTemplate.objects.get(supplier_id=supplier.id,
                                               apply_to=ShipFeeTemplate.APPLY_TO_SUPPLIER,
                                               is_active=True)
            result['shipfee_desc'] = tmpl.get_shipfee_desc()
            result['shipfee_template'] = tmpl.to_dict()
        except Exception, e:
            logger.exception(e)

        return json_response(result)
    except Supplier.DoesNotExist:
        return report_error('找不到供应商[%s]' % code or name or sup_id)


def _query_business(model, request):
    """
    获取供应商列表
    :param request:
        - [name], 可选，店名，如有多个，可用英文逗号分隔
        - [code], 可选，店铺编码，如有多个，可用英文逗号分隔
        - [province], 可选，所在省份
        - [city], 可选，所在市
        - [pos], 可选，起始偏移量，默认为0
        - [size]，可选，一次获取多少条数据，默认为10，取值范围2~20
        - [is_active], 可选，默认为1，即有效的，0为无效，all为全部
        - [since], 可选，日期时间，获取指定时间之后更新的记录
    :return:
        成功返回供应商对象,如：
            {
                province: "",
                city: "",
                code: "7kvfNY",
                name: "黄凌燕",
                address: "",
                primary_contact: "黄玲燕",
                id: 1
            },
        失败返回{'error': msg}

    eg. <a href="/tms-api/query_suppliers">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    records = model.objects.all()
    province = req.get('province')
    if 'code' in req:
        if ',' in req.get('code'):
            records = records.filter(code__in=req.get('code').split(','))
        else:
            records = records.filter(code=req.get('code'))
    if 'name' in req:
        if ',' in req.get('name'):
            records = records.filter(name__in=req.get('name').split(','))
        else:
            records = records.filter(name=req.get('name'))

    if province:
        records = records.filter(province=province)

    city = req.get('city')
    if city:
        records = records.filter(city=city)

    is_active = req.get('is_active')
    if '1' == is_active:
        records = records.filter(is_active=True)
    elif '0' == is_active:
        records = records.filter(is_active=False)

    # [since], 更新时间下限（不包含）,获取在给定时间之后修改的记录
    if req.get('since'):
        records = records.filter(update_time__gt=req.get('since'))

    start_pos = int(req.get('pos', 0))
    page_size = int(req.get('size', 10))
    # page_size = page_size if 2 < page_size < 20 else 20 if page_size >= 20 else 2
    if req.get('page'):
        start_pos = int(req.get('page')) * page_size
    records = records[start_pos:start_pos+page_size]
    return records


def query_suppliers(request):
    """
    获取供应商列表
    :param request:
        - [name], 可选，店名，如有多个，可用英文逗号分隔
        - [code], 可选，店铺编码，如有多个，可用英文逗号分隔
        - [province], 可选，所在省份
        - [city], 可选，所在市
        - [pos], 可选，起始偏移量，默认为0
        - [size]，可选，一次获取多少条数据，默认为10，取值范围2~20
        - [is_active], 可选，默认为1，即有效的，0为无效，all为全部
        - [since], 可选，日期时间，获取指定时间之后更新的记录
    :return:
        成功返回供应商对象列表,如：
        [{
            province: "",
            city: "",
            code: "7kvfNY",
            name: "黄凌燕",
            backup_contact: null,
            is_active: true,
            lng: 0,
            homepage: "",
            lat: 0,
            intro: "",
            post_code: "",
            address: "",
            notices: [
                "供应商消息通告",
            ],
            primary_contact: {
                mobile: "12345678901",
                email: "",
                name: "黄玲燕",
                id: 1
            },
            logo: "",
            is_verified: true,
            id: 1
            capital_account: {
                bank_name: "",  （开户银行名称）
                uid: "7kvfNY",  （用户uid）
                bank_code: "",  （银行编码，一般是银行的英文缩写）
                is_default: true, （是否默认账号）
                is_valid: true,  （是否有效）
                open_bank: "",  （开户行）
                ca_desc: "",    （账户说明）
                ca_type: "wechat",  （账户类型）
                ca_no: "0ljqweLUHEWowelknfwLIJlkn",  (资金账号，微信对应的资金账号是用户的openid)
                id: 1
            },
            shipfee_desc: [
                "满88元包邮"
            ]
        }]
        失败返回{'error': msg}

    eg. <a href="/tms-api/query_suppliers">查看样例</a>
    """
    records = _query_business(Supplier, request)
    res = []
    from basedata.models import ShipFeeTemplate
    for r in records:
        sup = r.to_dict(True)
        try:
            tmpl = ShipFeeTemplate.objects.get(supplier_id=r.id,
                                               apply_to=ShipFeeTemplate.APPLY_TO_SUPPLIER,
                                               is_active=True)
            sup['shipfee_desc'] = tmpl.get_shipfee_desc()
            # sup['shipfee_template'] = tmpl.to_dict()
        except Exception, e:
            # logger.exception(e)
            pass

        res.append(sup)
    return json_response(res)


def get_hotel(request):
    """
    根据编码获取酒店/民宿信息
    :param request:
        - code | name, 编码 | 名称
    :return:
        成功返回酒店对象
        {
            address : "徐汇区南丹东路",
            backup_contact : null,
            city : "上海",
            code : "TEST-hotel",    （编码）
            fax : "02187654321",
            homepage : "http://test.twohou.com",
            id : 1,
            images: [       (酒店头图)
                "http://xxx.qiniucdn.com/static/2016/10/19/94ad5624349a651.jpg",
                "http://xxx.qiniucdn.com/static/2016/10/19/u504034840376738.jpg"
            ],
            intro : "&lt;p&gt;介绍一下该酒店，可图文&lt;/p&gt;",   （酒店介绍，HTML文本）
            is_active : true,
            is_verified : true
            lat : 0,    (纬度)
            link_to_book1 : "http://www.ctrip.com/hotel/x",     (订房链接1)
            link_to_book2 : "http://www.qunar.com/hotel/x",     (订房链接2)
            lng : 0,    （经度）
            logo : "http://xxx.qiniucdn.com/static/2016/08/17/Cii9EFdEH8aIAFaZAAA.png",
            name : "测试酒店",
            phone : "021 12345678",
            post_code : "200030",
            primary_contact :
            {
                email : "winsom.huang@sh-anze.com",
                id : 71
                mobile : "12345678123",
                name : "Winsom",
            },
            province : "上海",
            tags : "test,free",     （多个标签用英文逗号分隔，如“超值,免费wifi,交通方便”）
        }

        失败返回{'error': msg}

    eg. <a href="/tms-api/get_hotel">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    code = req.get('code')
    name = req.get('name')
    try:
        hotel = Hotel.objects
        if code:
            hotel = hotel.get(code=code)
        elif name:
            hotel = hotel.get(name=name)
        else:
            return report_error('缺少参数！')
        result = hotel.to_dict(True)
        return json_response(result)
    except Supplier.DoesNotExist:
        return report_error('找不到酒店/民宿[%s]' % code or name)


def query_hotels(request):
    """
    获取供应商列表
    :param request:
        - [name], 可选，酒店名称，如有多个，可用英文逗号分隔
        - [code], 可选，酒店编码，如有多个，可用英文逗号分隔
        - [province], 可选，所在省份
        - [city], 可选，所在市
        - [tags], 可选，酒店tags，如果多个tag，可用","（需同时包含所有tag）或"|"（只需包含其中一个tag）分隔
        - [pos], 可选，起始偏移量，默认为0
        - [size]，可选，一次获取多少条数据，默认为10，取值范围2~20
        - [is_active], 可选，默认为1，即有效的，0为无效，all为全部
        - [since], 可选，日期时间，获取指定时间之后更新的记录
    :return:
        成功返回酒店对象列表,如：
            [
                {
                    address: "徐汇区南丹东路",
                    city: "上海",
                    code: "TEST-hotel",
                    id: 1
                    image: "http://xxx.qiniucdn.com/static/2016/10/19/94ad5624349a651.jpg",
                    logo: "http://xxx.qiniucdn.com/static/2016/08/17/Cii9EFdEegawe33.png",
                    name: "测试酒店",
                    primary_contact: "Winsom",
                    province: "上海",
                    tags: "test,free",
                }
            ]
        失败返回{'error': msg}

    eg. <a href="/tms-api/query_hotels">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    records = _query_business(Hotel, request)
    tags = req.get('tags')
    if tags:
        use_or = '|' in tags
        tags_list = tags.split('|') if use_or else tags.split(',')
        tags_filter = Q(tags__inset=tags_list[0])
        for tag in tags_list[1:]:
            if use_or:
                tags_filter |= Q(tags__inset=tag)
            else:
                tags_filter &= Q(tags__inset=tag)
        records = records.filter(tags_filter)

    return json_response([r.to_dict() for r in records])


def query_agents(request):
    """
    获取销售渠道列表
    :param request:
        - [name], 可选，渠道名称，如有多个，可用英文逗号分隔
        - [code], 可选，编码，如有多个，可用英文逗号分隔
        - [province], 可选，所在省份
        - [city], 可选，所在市
        - [tags], 可选，渠道tags，如果多个tag，可用","（需同时包含所有tag）或"|"（只需包含其中一个tag）分隔
        - [pos], 可选，起始偏移量，默认为0
        - [size]，可选，一次获取多少条数据，默认为10，取值范围2~20
        - [is_active], 可选，默认为1，即有效的，0为无效，all为全部
        - [since], 可选，日期时间，获取指定时间之后更新的记录
    :return:
        成功返回销售渠道对象列表,如：
            [
                {
                    address: "徐汇区南丹东路",
                    city: "上海",
                    code: "RJ",
                    id: 1
                    image: "http://xxx.qiniucdn.com/static/2016/10/19/94ad5624349a651.jpg",
                    logo: "http://xxx.qiniucdn.com/static/2016/08/17/Cii9EFdEegawe33.png",
                    name: "如家",
                    primary_contact: "Winsom",
                    province: "上海",
                    tags: "test,free",
                }
            ]
        失败返回{'error': msg}

    eg. <a href="/tms-api/query_agents">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    records = _query_business(SalesAgent, request)
    tags = req.get('tags')
    if tags:
        use_or = '|' in tags
        tags_list = tags.split('|') if use_or else tags.split(',')
        tags_filter = Q(tags__inset=tags_list[0])
        for tag in tags_list[1:]:
            if use_or:
                tags_filter |= Q(tags__inset=tag)
            else:
                tags_filter &= Q(tags__inset=tag)
        records = records.filter(tags_filter)

    return json_response([r.to_dict() for r in records])


def preview_hotel(request, hotel_id):
    """
    商品信息预览
    :param request:
    :param hotel_id:
    :return:
    """
    if not hotel_id:
        return render_to_response('admin/vendor/hotel/preview.html', {'error': '缺少酒店id！'})

    try:
        hotel = Hotel.objects.get(id=hotel_id)
        return render_to_response('admin/vendor/hotel/preview.html', {'original': hotel.to_dict(detail=True)})
    except Hotel.DoesNotExist:
        return render_to_response('admin/vendor/hotel/preview.html', {'error': '酒店不存在（id:%s）！' % hotel_id})


def query_logistic_vendors(request):
    """
    获取物流服务提供商列表
    :param request:
        - [name], 可选，店名，如有多个，可用英文逗号分隔
        - [code], 可选，店铺编码，如有多个，可用英文逗号分隔
        - [province], 可选，所在省份
        - [city], 可选，所在市
        - [pos], 可选，起始偏移量，默认为0
        - [size]，可选，一次获取多少条数据，默认为10，取值范围2~20
        - [is_active], 可选，默认为1，即有效的，0为无效，all为全部
        - [since], 可选，日期时间，获取指定时间之后更新的记录
    :return:
        成功返回供应商对象列表,如：
            [{
                province: null,
                city: null,
                code: "shentong",
                name: "申通",
                address: null,
                primary_contact: "",
                id: 58
            },]
        失败返回{'error': msg}

    eg. <a href="/tms-api/query_logistic_vendors">查看样例</a>
    """
    records = _query_business(LogisticsVendor, request)
    res = []
    for r in records:
        res.append(r.to_dict())
    return json_response(res)


def query_supplier_incomes(request):
    """
    获取供应商收入明细(非资金流水，资金流水请用query_accounts接口)
    :param request(GET):
        - uid, 必填，用户uid，用于验证该用户是否有权查看
        - supplier_id, 必填，供货商ID
        - [status], 可选，收益状态，有如下几种情形：
            * 0  - 待确认
            * 1  - 待结算
            * 2  - 已结算
            * 3  - 已取消，即订单已取消或退款
        - [has_doubt], 可选，是否存在疑问
            * 0 - 否
            * 1 - 是
        - [activity_code], 可选，活动代码
        - [order_no], 可选，订单号
        - [account_no], 可选，账户流水号
        - [since], 可选，日期时间型，记录时间（非实际到账）下限（不包含）
        - [before], 可选，日期时间型，记录时间（非实际到账）上限（不包含）
        - [update_since], 可选，日期时间型，更新时间（非实际到账）下限（不包含）
        - [pos], 可选，获取的结果可能存在多页时，给定开始选取的位置，默认为0
        - [size], 可选，获取的结果可能存在多页时，确定返回每页记录数，默认为10
    :return:
        成功返回收益记录列表，如：
            [
                {
                    status: 0,
                    update_time: null,
                    activity_code: null,
                    order_no: "D160411KMSQWV",
                    achieved: "0.00",  （到账数额）
                    achieved_time: null,  （到账时间，为空表示未到账）
                    create_time: "2016-04-11 18:11:59",
                    referrer_id: "184813c81d2540e68f80ac19210c6413",
                    reward: "0.00" , （预期收益金额）
                    reward_type: 0,  （收益类型）
                },
            ]
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/query_supplier_incomes">查看样例</a>
    """
    from profile.views import validate_user_and_supplier
    uid, supplier_id, err = validate_user_and_supplier(request)
    if err:
        return report_error(err)

    req = request.POST if 'POST' == request.method else request.GET
    records = SupplierSalesIncome.objects.filter(supplier_id=supplier_id)
    status = req.get('status')
    if status and status.isdigit():
        records = records.filter(status=int(status))

    has_doubt = req.get('has_doubt')
    if has_doubt in [0, '0']:
        records = records.filter(has_doubt=False)
    elif has_doubt in [1, '1']:
        records = records.filter(has_doubt=True)

    if req.get('activity_code'):
        records = records.filter(activity_code=req.get('activity_code'))

    if req.get('order_no'):
        records = records.filter(order_no=req.get('order_no'))

    if req.get('account_no'):
        records = records.filter(account_no=req.get('account_no'))

    # [since], 记录时间（非实际到账）下限（不包含）
    if req.get('since'):
        records = records.filter(create_time__gt=req.get('since'))
    # [before], 记录时间（非实际到账）上限（不包含）
    if req.get('before'):
        records = records.filter(create_time__lt=req.get('before'))

    # [before], 记录时间（非实际到账）下限（不包含）
    if req.get('update_since'):
        records = records.filter(update_time__gt=req.get('update_since'))

    start_pos = int(req.get('pos', 0))
    page_size = int(req.get('size', 10))
    # page_size = page_size if 2 < page_size < 20 else 20 if page_size >= 20 else 2
    if req.get('page'):
        start_pos = int(req.get('page')) * page_size

    records = records[start_pos:start_pos + page_size]

    return json_response(records)


@cache_page(30, key_prefix="tms.api")
def get_brands(request):
    """
    获取品牌列表，用于筛选功能
    :param request (GET):
        - [pos], 可选，获取的结果可能存在多页时，给定开始选取的位置，默认为0
        - [size], 可选，获取的结果可能存在多页时，确定返回每页记录数，默认为100
    :return:

    eg. <a href="/tms-api/get_brands">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    records = Brand.objects.order_by('-list_order').order_by(Convert(F('name')))
    if 'force_refresh' in req:
        Brand.initialize()

    start_pos = int(req.get('pos', 0))
    page_size = int(req.get('size', 10))
    # page_size = page_size if 2 < page_size < 20 else 20 if page_size >= 20 else 2
    if req.get('page'):
        start_pos = int(req.get('page')) * page_size
    records = records[start_pos:start_pos+page_size]
    return json_response(records)


def get_notice(request):
    """
    获取指定供应商的消息清单
    :param request (GET):
        - supplier_id， 供应商id
        - is_valid, 是否有效，默认为1，表示有效（有效期内），2表示全部，0表示无效
    :return:

    eg. <a href="/tms-api/get_notice">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    if not req.get('supplier_id'):
        return report_error('缺少供应商id参数')

    records = SupplierNotice.objects.filter(supplier_id=req.get('supplier_id'))
    cur_time = now(settings.USE_TZ)
    if '1' == req.get('is_valid'):
        records = records.filter(effective_time__lte=cur_time, expire_time__gt=cur_time)
    elif '0' == req.get('is_valid'):
        records = records.filter(Q(effective_time__gt=cur_time) | Q(expire_time__lte=cur_time))

    return json_response(records)


def update_notice(request):
    """
    更新指定的供应商的消息
    :param request:
        - uid, 用户uid
        - supplier_id, 供应商id
        - [id], 消息id，如果没有，则添加一条新的消息
        - content, 消息正文 （长度：1024）
        - [effective_time], 生效时间，默认为当前时间
        - [expire_time], 失效时间，默认为当前时间7天后失效
    :return:
        成功返回{"result": "ok"， "id": 1}

    eg. <a href="/tms-api/update_notice">查看样例</a>
    """
    from profile.views import validate_user_and_supplier

    uid, supplier_id, err = validate_user_and_supplier(request)
    if err:
        return report_error(err)

    req = request.POST if 'POST' == request.method else request.GET
    if req.get('id'):
        try:
            notice = SupplierNotice.objects.get(id=req.get('id'))
        except SupplierNotice.DoesNotExist:
            return report_error('消息(id: %s)不存在' % req.get('id'))
    else:
        notice = SupplierNotice()

    notice.supplier_id = supplier_id
    notice.content = req.get('content')
    if 'effective_time' in req:
        notice.effective_time = req.get('effective_time')
    if 'expire_time' in req:
        notice.effective_time = req.get('expire_time')
    notice.save()
    return report_ok({"id": notice.pk})