# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from decimal import Decimal
from datetime import datetime

dummy_data = {
    'users': ['test_12345678', 'test_123456789', 'test_supplier', 'test_inactive', 'test_sp'],
    'orgs': ['test-group', 'test-org-passed', 'test-org-pending'],
    'products': ['TEST-001', 'TEST-002', 'TEST-003', 'TEST-004', 'TEST-005', ],
    'suppliers': ['TWOHOU-test', ],
    'coupon-rules': ['TEST-160601', 'TEST-160602'],
    'coupon-tickets': [''],
    'tms-user': ['test-sp', 'test-supplier', ],
    'ship-templates': ['test-shipfee-by-unit', 'test-shipfee-by-weight', 'test-global'],
}

def init():
    # initial TMS-user
    from django.contrib.auth.models import User
    password = 'pbkdf2_sha256$20000$IiPIPePTqE3c$tXy+bguBcxAg4+hsNHZ2VpW4JArVC5bNCb30+kXZzvU='  # hashers.make_password('123456')
    User.objects.update_or_create(username=dummy_data['tms-user'][0],
                                  defaults={
                                      "first_name": dummy_data['tms-user'][0],
                                      "email": 'winsom@sh-anze.com',
                                      "password": password,
                                      "is_superuser": True,
                                      "is_staff": True}
    )
    tms_user, created = User.objects.get_or_create(username=dummy_data['tms-user'][1],
                                                   defaults={
                                                       "first_name": dummy_data['tms-user'][1],
                                                       "email": 'winsom@sh-anze.com',
                                                       "password": password,
                                                       "is_staff": True}
                                                   )
    tms_user.groups.add(1)  # 设为供应商
    tms_user.save()
    # tms_user.permissions

    # initial user
    tester1 = dummy_data['users'][0]
    tester2 = dummy_data['users'][1]
    tester3 = dummy_data['users'][2]
    tester4 = dummy_data['users'][3]
    tester5 = dummy_data['users'][4]
    from profile.models import EndUser, EndUserExt, EndUserEnterprise, UserOrgSnapShot, EndUserRole
    EndUserEnterprise.objects.update_or_create(uid=dummy_data['orgs'][0],
                                               defaults={'review_status': EndUserEnterprise.REVIEW_PASSED,
                                                         'user_type': EndUserEnterprise.USER_GROUP,
                                                         'real_name': dummy_data['orgs'][0]})
    EndUserEnterprise.objects.update_or_create(uid=dummy_data['orgs'][1],
                                               defaults={'review_status': EndUserEnterprise.REVIEW_PASSED,
                                                         'org_uid': dummy_data['orgs'][0],
                                                         'real_name': dummy_data['orgs'][1]})
    EndUserEnterprise.objects.update_or_create(uid=dummy_data['orgs'][2],
                                               defaults={'review_status': EndUserEnterprise.REVIEW_PENDING,
                                                         'org_uid': dummy_data['orgs'][0],
                                                         'real_name': dummy_data['orgs'][2],
                                                         'created_by': dummy_data['users'][1]})
    EndUser.objects.update_or_create(uid=tester1, defaults={'real_name': tester1, 'org_uid': dummy_data['orgs'][1]})
    EndUser.objects.update_or_create(uid=tester2, defaults={'real_name': tester2,
                                                            'referrer': tester1,
                                                            'org_uid': dummy_data['orgs'][1]})
    EndUser.objects.update_or_create(uid=tester3, defaults={'real_name': tester3,
                                                            'referrer': tester1})
    EndUser.objects.update_or_create(uid=tester4, defaults={'real_name': tester4,
                                                            'referrer': tester1,
                                                            'status': EndUser.STATUS_INACTIVE})
    EndUser.objects.update_or_create(uid=tester5, defaults={'real_name': tester5,
                                                            'referrer': tester1})
    EndUserExt.objects.update_or_create(uid=tester3,
                                        ex_id_type=EndUserExt.ID_TYPE_INTERNAL,
                                        ex_id=dummy_data['tms-user'][1])
    EndUserExt.objects.update_or_create(uid=tester5,
                                        ex_id_type=EndUserExt.ID_TYPE_INTERNAL,
                                        ex_id=dummy_data['tms-user'][0])
    # initial contact
    contact = {
        'name': 'Winsom',
        'mobile': '12345678123',
        'email': 'winsom.huang@sh-anze.com'
    }
    from vendor.models import Contact, Supplier, Manufacturer, SupplierManager, Brand
    brand, created = Brand.objects.get_or_create(name='测试品牌')
    contact, created = Contact.objects.update_or_create(name=contact['name'], defaults=contact)
    # inital supplier
    supplier = {
        'province': u'海南',
        'city': u'海口',
        'code': dummy_data['suppliers'][0],
        'name': u'供货商（测试）',
        'address': u'',
        'primary_contact': contact
    }
    # inital supplier
    manufacture = {
        'province': u'海南',
        'city': u'海口',
        'code': u'test-mfg',
        'name': u'生产商（测试）',
        'address': u'',
        'primary_contact': contact
    }
    supplier, created = Supplier.objects.update_or_create(code=supplier['code'], defaults=supplier)
    manufacture, created = Manufacturer.objects.update_or_create(code=manufacture['code'], defaults=manufacture)
    SupplierManager.objects.get_or_create(supplier=supplier, user=tms_user)

    category = {
        'code': 'testa',
        'name': '测试'
    }

    from basedata.models import ProductCategory, Product, ProductImage, ShipFeeTemplate, ShipFeeTemplateItem
    category, created = ProductCategory.objects.update_or_create(code=category['code'], defaults=category)
    tmpl_by_unit, created = ShipFeeTemplate.objects.update_or_create(name=dummy_data['ship-templates'][0],
                                                                     bill_type=ShipFeeTemplate.BILL_PER_QUANTITY,
                                                                     supplier=supplier,
                                                                     defaults={
                                                                         'apply_to': ShipFeeTemplate.APPLY_TO_PRODUCT,
                                                                         'initial_units': 1,
                                                                         'initial_fee': 10,
                                                                         'second_units': 1,
                                                                         'second_fee': 5,
                                                                         'no_ship_areas': "甘肃,青海,新疆,西藏",
                                                                         'free_ship_cnt': 5,
                                                                         'is_public': True,
                                                                         'free_ship_amount': 0,
                                                                     })
    ShipFeeTemplateItem.objects.update_or_create(template_id=tmpl_by_unit.pk,
                                                 areas="宁夏,内蒙古",
                                                 defaults={
                                                     'initial_units': 1,
                                                     'initial_fee': 20,
                                                     'second_units': 1,
                                                     'second_fee': 10,
                                                 })
    tmpl_by_weight, created = ShipFeeTemplate.objects.update_or_create(name=dummy_data['ship-templates'][1],
                                                                       bill_type=ShipFeeTemplate.BILL_PER_WEIGHT,

                                                                       supplier=supplier,
                                                                       defaults={
                                                                           'apply_to': ShipFeeTemplate.APPLY_TO_PRODUCT,
                                                                           'initial_units': 1,
                                                                           'initial_fee': 10,
                                                                           'second_units': 1,
                                                                           'second_fee': 5,
                                                                           'no_ship_areas': "甘肃,青海,新疆,西藏",
                                                                           'free_ship_cnt': 5,
                                                                           'is_public': True,
                                                                           'free_ship_amount': 0,
                                                                       })
    ShipFeeTemplateItem.objects.update_or_create(template_id=tmpl_by_weight.pk,
                                                 areas="宁夏,内蒙古",
                                                 defaults={
                                                     'initial_units': 1,
                                                     'initial_fee': 20,
                                                     'second_units': 1,
                                                     'second_fee': 10,
                                                 })

    tmpl_global, created = ShipFeeTemplate.objects.update_or_create(name=dummy_data['ship-templates'][2],
                                                                    supplier=supplier,
                                                                    defaults={
                                                                        'apply_to': ShipFeeTemplate.APPLY_TO_SUPPLIER,
                                                                        'initial_units': 1,
                                                                        'initial_fee': 10,
                                                                        'second_units': 1,
                                                                        'second_fee': 5,
                                                                        'no_ship_areas': "甘肃,青海,新疆,西藏",
                                                                        'free_ship_cnt': 5,
                                                                        'is_public': True,
                                                                        'free_ship_amount': 0,
                                                                        })
    # inital products
    prds = [
        {
            'allow_local_ship': False,
            'allow_pay_offline': False,
            'allow_self_pick': False,
            'barcode': None,
            'brand_id': '测试品牌',
            'brief': u'',
            'category_id': category.code,
            'code': u'TEST-001',
            'color': u'',
            'cost': Decimal('10.00'),
            'settle_price': Decimal('20.00'),
            'market_price': Decimal('40.00'),
            'retail_price': Decimal('30.00'),
            'initial_ship_fee': Decimal('10.00'),
            'second_ship_fee': Decimal('0.00'),
            'upper_limit': 0,
            'lower_limit': 0,
            'expiration': None,
            'intro': u'<p>test products intro</p>',
            'is_distributed': True,
            'is_hot': False,
            'is_multispec': True,
            'spec_group': 'TEST-001',
            'spec_tag1': '五斤装',
            'is_nationwide': True,
            'is_new': False,
            'is_package': False,
            'is_special': 0,
            'is_virtual': False,
            'list_order': 0L,
            'local_ship_desc': u'',
            'manufacturer': manufacture,
            'name': 'test-product-1',
            'offline_only': False,
            'origin_city': '海口',
            'origin_country_id': 1L,
            'origin_province': '海南',
            'product_comment': u'',
            'production_date': None,
            'qualification': u'',
            's_code': u'',
            's_status': 0,
            'self_pick_desc': u'',
            'size': u'',
            'spec': u'30*25*5',
            'status': 1,
            'stock_volume': 998L,
            'stock_volume_threshold': 10L,
            'supplier': supplier,
            'tags': '测试,test',
            'texture': u'',
            'unit': '个',
            'warranty': u'',
            'weight': 400L,
            'shipfee_template': tmpl_by_unit
        },
        {
            'allow_local_ship': False,
            'allow_pay_offline': False,
            'allow_self_pick': False,
            'barcode': None,
            'brand_id': '测试品牌',
            'brief': u'',
            'category_id': category.code,
            'code': u'TEST-002',
            'color': u'',
            'cost': Decimal('100.00'),
            'settle_price': Decimal('200.00'),
            'market_price': Decimal('400.00'),
            'retail_price': Decimal('300.00'),
            'initial_ship_fee': Decimal('20.00'),
            'second_ship_fee': Decimal('10.00'),
            'upper_limit': 0,
            'lower_limit': 0,
            'expiration': None,
            'intro': u'<p>test products intro</p>',
            'is_distributed': True,
            'is_hot': False,
            'is_nationwide': True,
            'is_new': False,
            'is_package': False,
            'is_special': 1,
            'is_virtual': False,
            'list_order': 0L,
            'local_ship_desc': u'',
            'manufacturer': manufacture,
            'name': 'test-product-2',
            'offline_only': False,
            'origin_city': '海口',
            'origin_country_id': 1L,
            'origin_province': '海南',
            'product_comment': u'',
            'production_date': None,
            'qualification': u'',
            's_code': u'',
            's_status': 0,
            'self_pick_desc': u'',
            'size': u'',
            'spec': u'30*25*5',
            'status': 1,
            'stock_volume': 998L,
            'stock_volume_threshold': 10L,
            'supplier': supplier,
            'tags': '测试,test',
            'texture': u'',
            'unit': '个',
            'warranty': u'',
            'weight': 400L,
            'shipfee_template': tmpl_by_weight
        },
        {
            'allow_local_ship': False,
            'allow_pay_offline': False,
            'allow_self_pick': False,
            'barcode': None,
            'brand_id': '测试品牌',
            'brief': u'',
            'category_id': category.code,
            'code': u'TEST-003',
            'color': u'',
            'cost': Decimal('11.00'),
            'settle_price': Decimal('21.00'),
            'market_price': Decimal('41.00'),
            'retail_price': Decimal('31.00'),
            'initial_ship_fee': Decimal('11.00'),
            'second_ship_fee': Decimal('0.00'),
            'upper_limit': 0,
            'lower_limit': 0,
            'expiration': None,
            'intro': u'<p>test products intro</p>',
            'is_distributed': False,
            'is_hot': False,
            'is_multispec': False,
            'spec_group': 'TEST-001',
            'spec_tag1': '十斤装',
            'is_nationwide': True,
            'is_new': False,
            'is_package': False,
            'is_special': 0,
            'is_virtual': False,
            'list_order': 0L,
            'local_ship_desc': u'',
            'manufacturer': manufacture,
            'name': 'test-product-3',
            'offline_only': False,
            'origin_city': '海口',
            'origin_country_id': 1L,
            'origin_province': '海南',
            'product_comment': u'',
            'production_date': None,
            'qualification': u'',
            's_code': u'',
            's_status': 0,
            'self_pick_desc': u'',
            'size': u'',
            'spec': u'30*25*5',
            'status': 1,
            'stock_volume': 998L,
            'stock_volume_threshold': 10L,
            'supplier': supplier,
            'tags': '测试,test',
            'texture': u'',
            'unit': '个',
            'warranty': u'',
            'weight': 400L,
        },
        {
            'allow_local_ship': False,
            'allow_pay_offline': False,
            'allow_self_pick': False,
            'barcode': None,
            'brand_id': '测试品牌',
            'brief': u'',
            'category_id': category.code,
            'code': u'TEST-004',
            'color': u'',
            'cost': Decimal('10.00'),
            'settle_price': Decimal('20.00'),
            'market_price': Decimal('40.00'),
            'retail_price': Decimal('30.00'),
            'initial_ship_fee': Decimal('10.00'),
            'second_ship_fee': Decimal('0.00'),
            'upper_limit': 0,
            'lower_limit': 0,
            'expiration': None,
            'intro': u'<p>test products intro</p>',
            'is_distributed': False,
            'is_hot': False,
            'is_nationwide': True,
            'is_new': False,
            'is_package': False,
            'is_special': 0,
            'is_virtual': False,
            'list_order': 0L,
            'local_ship_desc': u'',
            'manufacturer': manufacture,
            'name': 'test-product-4',
            'offline_only': False,
            'origin_city': '海口',
            'origin_country_id': 1L,
            'origin_province': '海南',
            'product_comment': u'',
            'production_date': None,
            'qualification': u'',
            's_code': u'',
            's_status': 0,
            'self_pick_desc': u'',
            'size': u'',
            'spec': u'30*25*5',
            'status': 1,
            'stock_volume': 998L,
            'stock_volume_threshold': 10L,
            'supplier': supplier,
            'tags': '测试,test',
            'texture': u'',
            'unit': '个',
            'warranty': u'',
            'weight': 400L,
        },
        {
            'allow_local_ship': False,
            'allow_pay_offline': False,
            'allow_self_pick': False,
            'barcode': None,
            'brand_id': '测试品牌',
            'brief': u'',
            'category_id': category.code,
            'code': u'TEST-005',
            'color': u'',
            'cost': Decimal('10.00'),
            'settle_price': Decimal('20.00'),
            'market_price': Decimal('40.00'),
            'retail_price': Decimal('30.00'),
            'initial_ship_fee': Decimal('10.00'),
            'second_ship_fee': Decimal('0.00'),
            'upper_limit': 0,
            'lower_limit': 0,
            'expiration': None,
            'intro': u'<p>test products intro</p>',
            'is_distributed': False,
            'is_hot': False,
            'is_nationwide': True,
            'is_new': False,
            'is_package': False,
            'is_special': 0,
            'is_virtual': False,
            'list_order': 0L,
            'local_ship_desc': u'',
            'manufacturer': manufacture,
            'name': 'test-product-5',
            'offline_only': False,
            'origin_city': '海口',
            'origin_country_id': 1L,
            'origin_province': '海南',
            'product_comment': u'',
            'production_date': None,
            'qualification': u'',
            's_code': u'',
            's_status': 0,
            'self_pick_desc': u'',
            'size': u'',
            'spec': u'30*25*5',
            'status': 1,
            'stock_volume': 998L,
            'stock_volume_threshold': 10L,
            'supplier': supplier,
            'tags': '测试,test',
            'texture': u'',
            'unit': '个',
            'warranty': u'',
            'weight': 400L,
        },
    ]
    products = []
    for prd in prds:
        p, created = Product.objects.update_or_create(code=prd['code'], defaults=prd)
        prd_img, created = ProductImage.objects.get_or_create(product=p, origin='test/test.png')
        products.append(p.to_dict())

    coupon_rules = [
        {
            'code': 'TEST-160601',
            'threshold': 100L,
            'applied_to_first_order': False,
            'allow_addon': False,
            'applied_to_stores': '',
            'description': '<p>满100减10元券</p>',
            'format': '',
            'start_time': datetime.strptime('2016-06-01', '%Y-%m-%d'),
            'most_tickets': 10,
            'is_active': True,
            'discount': 10L,
            'repeatable': False,
            'coupon_image_id': 229L,  # TODO: initialize an image
            'name': '满100减10元',
            'pub_number': 1000L,
            'tickets_onetime': 1,
            'applied_to_suppliers': '',
            'allow_dynamic': False,
            'dynamic_days': 0,
            'end_time': datetime.strptime('2030-06-01', '%Y-%m-%d'),
            'applied_to_products': products[0]['code']
        },
        {
            'code': 'TEST-160602',
            'threshold': 50L,
            'applied_to_first_order': False,
            'allow_addon': False,
            'applied_to_stores': '',
            'description': '<p>满50减10元券</p>',
            'format': '',
            'start_time': datetime.strptime('2016-06-01', '%Y-%m-%d'),
            'most_tickets': 10,
            'is_active': True,
            'discount': 10L,
            'repeatable': False,
            'coupon_image_id': 229L,  # TODO: initialize an image
            'name': '满50减10元',
            'pub_number': 1000L,
            'tickets_onetime': 1,
            'applied_to_suppliers': '',
            'allow_dynamic': True,
            'dynamic_days': 30,
            'end_time': datetime.strptime('2030-06-01', '%Y-%m-%d'),
            'applied_to_products': products[0]['code']
        }
    ]
    from promote.models import CouponRule, CouponTicket
    for r in coupon_rules:
        coupon_rule, created = CouponRule.objects.update_or_create(code=r['code'], defaults=r)
        coupon_tickets = coupon_rule.fetch_coupons(tester1, 5)

    # dummy_data = {
    #     "user": [tester1, tester2],
    #     "contact": [contact],
    #     "supplier": [supplier],
    #     "manufacture": [manufacture],
    #     "products": products,
    #     "category": [category],
    #     "coupon_rule": [coupon_rule],
    #     "coupon_tickets": coupon_tickets
    # }


if __name__ == '__main__':
    import os
    PROJECT_PATH = os.path.abspath('%s/../..' % __file__)
    DJANGO_SETTINGS = "tms.settings"

    import sys
    print(u'Python %s on %s' % (sys.version, sys.platform))
    import django
    print(u'Django %s' % django.get_version())
    sys.path.insert(0, PROJECT_PATH)
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS)
    print sys.path
    if 'setup' in dir(django):
        django.setup()

    init()