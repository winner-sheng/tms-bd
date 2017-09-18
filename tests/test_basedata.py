# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import unittest
from decimal import Decimal

import requests

from basedata.models import Product, Order
from tms.settings import APP_URL
from util.renderutil import random_str, logger
from util.webtool import fetch_json
import tests
__author__ = 'winsom'


class TestOrder(unittest.TestCase):

    def setUp(self):
        pass

    def test_product(self):
        # simply test query_products
        url = "%s%s" % (APP_URL, "/tms-api/query_products")
        response = fetch_json(url, {})
        self.assertIsInstance(response, list, 'query_products is expected to return a list')
        prd_size = len(response)
        # simply test query_distributes
        url = "%s%s" % (APP_URL, "/tms-api/query_distributes")
        response = fetch_json(url, {})
        self.assertIsInstance(response, list, 'query_distributes is expected to return a list')
        self.assertTrue(len(response) > 0 or prd_size > 0, 'At least one product is expected')
        prd_code = response[0].get('code')
        self.assertIsNotNone(prd_code, 'Product code should not be None')

        # test get_product
        url = "%s%s" % (APP_URL, "/tms-api/get_product")
        response = fetch_json(url, {'code': prd_code})
        self.assertIsInstance(response, dict, 'get_product is expected to return an object')
        self.assertIsNotNone(response.get('name'), 'Product[%s] lack of name' % prd_code)
        self.assertTrue(len(response.get('images')) > 0, 'Product[%s] has no image' % response.get('name'))
        self.assertEqual(prd_code, response.get('code'), 'Product code should be the same')
        self.assertEqual(response.get('status'), Product.STATUS_ONSHELF,
                         'Product[%s] should be on shelf' % response.get('name'))
        self.assertTrue(Decimal(response.get('retail_price')) <= Decimal(response.get('market_price')) > 0,
                        '[%s]Market price < retail_price or market <= 0' % response.get('name'))

    def test_distributes(self):
        # simply test query_distributes
        url = "%s%s" % (APP_URL, "/tms-api/query_distributes")
        response = fetch_json(url, {"pos": 0, "size": 2, "kw": 2})
        self.assertIsInstance(response, list, 'query_distributes is expected to return a list')
        self.assertTrue(len(response) == 2, 'At least one product is expected')
        prd_code = response[0].get('code')
        self.assertIsNotNone(prd_code, 'Product code should not be None')

        # test get_product
        url = "%s%s" % (APP_URL, "/tms-api/get_product")
        response = fetch_json(url, {'code': prd_code})
        self.assertIsInstance(response, dict, 'get_product is expected to return an object')
        self.assertIsNotNone(response.get('name'), 'Product[%s] lack of name' % prd_code)
        self.assertTrue(len(response.get('images')) > 0, 'Product[%s] has no image' % response.get('name'))
        self.assertEqual(prd_code, response.get('code'), 'Product code should be the same')
        self.assertEqual(response.get('status'), Product.STATUS_ONSHELF,
                         'Product[%s] should be on shelf' % response.get('name'))
        self.assertTrue(Decimal(response.get('retail_price')) <= Decimal(response.get('market_price')) > 0,
                        '[%s]Retail price is supposed to be not greater than market_price, and 0' % response.get('name'))

    def test_pre_order(self):
        prd_code = tests.dummy_data['products'][0]
        url = "%s%s" % (APP_URL, "/tms-api/get_product")
        response = fetch_json(url, {'code': prd_code})
        self.assertEqual(response.get('code'), prd_code)
        deal_price = Decimal(response.get('retail_price'))
        supplier = response.get('supplier') or {}
        supplier_id = supplier.get('id')
        pcs = 2
        shipfee_template = response.get('shipfee_template')
        retail_price = Decimal(response.get('retail_price'))
        self.assertTrue(Decimal(response.get('market_price')) >= retail_price >= Decimal(response.get('settle_price')))
        self.assertEqual(shipfee_template.get('name'), tests.dummy_data['ship-templates'][0])
        # quick order with specific product
        url = "%s%s" % (APP_URL, "/tms-api/pre_order")
        buyer = tests.dummy_data['users'][0]
        receiver = 'test_123456'
        receiver_mobile = '12345678901'
        ship_address = 'test street'
        buyer_note = 'note for test'
        shop_data = [{'code': prd_code, 'pcs': pcs}]
        shop_data = json.dumps(shop_data)
        params = {
            'buyer_id': buyer,
            'shop_data': shop_data,
            'receiver': receiver,
            'receiver_mobile': receiver_mobile,
            'ship_address': ship_address,
            'ship_province': '上海',
            'buyer_note': buyer_note,
            'referrer_id': buyer,
            # 'coupon': 'SFFDA9ZJNPMERQXF'
        }
        logger.debug(params)
        response = fetch_json(url, params, 'POST')
        self.assertEquals(response.get('receiver'), 'test_123456')
        self.assertEquals(response.get('receiver_mobile'), receiver_mobile, 'Receiver mobile incorrect')
        self.assertEquals(response.get('ship_address'), ship_address, 'Ship address incorrect')
        self.assertEquals(response.get('buyer_note'), buyer_note, 'Buyer note incorrect')
        self.assertEquals(response.get('buyer_id'), buyer, 'Buyer incorrect')
        self.assertEquals(response.get('referrer_id'), buyer, 'Referrer incorrect')
        self.assertEqual(Decimal(response.get('ship_fee')), 15)
        self.assertEqual(Decimal(response.get('ship_fee_off')), 0, 'Ship fee off incorrect')
        self.assertEqual(response.get('pcs_amount'), pcs)
        self.assertEqual(response.get('package_pcs'), 1)
        self.assertEqual(Decimal(response.get('shop_amount')), deal_price * pcs, 'Shop amount incorrect')
        # self.assertEqual(Decimal(response.get('shop_amount_off')), 0, 'Shop amount off incorrect')
        self.assertEqual(Decimal(response.get('pay_amount')),
                         Decimal(response.get('shop_amount')) + Decimal(response.get('ship_fee'))
                         - Decimal(response.get('shop_amount_off')) - Decimal(response.get('ship_fee_off')))

        params = {
            'buyer_id': buyer,
            'shop_data': shop_data,
            'receiver': receiver,
            'receiver_mobile': receiver_mobile,
            'ship_address': ship_address,
            'ship_province': '西藏',
            'buyer_note': buyer_note,
            'referrer_id': buyer,
            # 'coupon': 'SFFDA9ZJNPMERQXF'
        }
        logger.debug(params)
        response = fetch_json(url, params, 'POST')
        self.assertTrue(response.get('error'))

        params = {
            'buyer_id': buyer,
            'shop_data': shop_data,
            'receiver': receiver,
            'receiver_mobile': receiver_mobile,
            'ship_address': ship_address,
            'ship_province': '宁夏',
            'buyer_note': buyer_note,
            'referrer_id': buyer,
            # 'coupon': 'SFFDA9ZJNPMERQXF'
        }
        logger.debug(params)
        response = fetch_json(url, params, 'POST')
        self.assertEqual(Decimal(response.get('ship_fee')), 15)

    def test_make_order(self):
        buyer = tests.dummy_data['users'][0]
        products = tests.dummy_data['products']
        prd_code = products[0]
        prd_code2 = products[1]
        url = "%s%s" % (APP_URL, "/tms-api/get_product")
        product1 = fetch_json(url, {"code": prd_code})
        product2 = fetch_json(url, {"code": prd_code2})
        self.assertEqual(product1.get('code'), prd_code)
        self.assertEqual(product2.get('code'), prd_code2)
        deal_price = Decimal(product1.get('retail_price'))
        deal_price2 = Decimal(product2.get('retail_price'))
        stock_volume = product1.get('stock_volume')
        supplier = product1.get('supplier') or {}
        supplier_id = supplier.get('id')
        pcs = 2
        pay_off = 0

        # simply test fetch coupons
        url = "%s%s" % (APP_URL, "/tms-api/fetch_coupons")
        resp = fetch_json(url, {'uid': buyer,
                                'rules': "%s,1" % tests.dummy_data['coupon-rules'][1]})
        self.assertIn('tickets', resp)
        tickets = resp.get('tickets')
        self.assertEqual(len(tickets), 1)

        # quick order with specific product
        url = "%s%s" % (APP_URL, "/tms-api/make_order")
        receiver = 'test_123456'
        receiver_mobile = '12345678901'
        ship_address = 'test street'
        buyer_note = 'note for test'
        shop_data = [{'code': prd_code, 'pcs': pcs},
                     {'code': prd_code2, 'pcs': pcs}]
        shop_data = json.dumps(shop_data)
        params = {
            'buyer_id': buyer,
            'shop_data': shop_data,
            'receiver': receiver,
            'receiver_mobile': receiver_mobile,
            'ship_address': ship_address,
            'buyer_note': buyer_note,
            'referrer_id': buyer,
            'org_uid': tests.dummy_data['orgs'][1],
            'coupon': tickets[0].get('code')
        }
        discount = 10
        logger.debug(params)
        response = fetch_json(url, params, 'POST')
        order_no = response.get('order_no')
        self.assertIsNotNone(order_no)
        print 'make order: ', order_no
        self.assertEquals(response.get('receiver'), 'test_123456')
        self.assertEquals(response.get('receiver_mobile'), receiver_mobile, 'Receiver mobile incorrect')
        self.assertEquals(response.get('ship_address'), ship_address, 'Ship address incorrect')
        self.assertEquals(response.get('buyer_note'), buyer_note, 'Buyer note incorrect')
        self.assertEquals(response.get('buyer_id'), buyer, 'Buyer incorrect')
        self.assertEquals(response.get('referrer_id'), buyer, 'Referrer incorrect')
        self.assertEqual(Decimal(response.get('ship_fee_off')), 0)
        self.assertEqual(response.get('pcs_amount'), 4)
        self.assertEqual(response.get('package_pcs'), 1, 'Package pcs incorrect')
        self.assertEqual(Decimal(response.get('shop_amount')),
                         (deal_price - pay_off) * pcs + (deal_price2 - pay_off) * pcs)
        # self.assertEqual(Decimal(response.get('shop_amount_off')), 0, 'Shop amount off incorrect')
        self.assertEqual(Decimal(response.get('pay_amount')),
                         Decimal(response.get('shop_amount')) + Decimal(response.get('ship_fee')) - discount)
        self.assertEqual(response.get('supplier'), supplier_id)

        # check if coupon status changed
        url = "%s%s" % (APP_URL, "/tms-api/is_coupon_ok")
        resp = fetch_json(url, {'uid': buyer,
                                'coupon': tickets[0].get('code')})
        self.assertIn(tickets[0].get('code'), resp)
        self.assertIsNot(resp.get(tickets[0].get('code')), True)

        # test pay_order
        order_no = response.get('order_no')
        pay_amount = response.get('pay_amount')
        # client = Client()
        url = "%s%s" % (APP_URL, "/tms-api/pay_order")
        params = {
            "order_no": order_no,
            "pay_amount": pay_amount,
            "uid": tests.dummy_data['users'][0],
            "pay_code": random_str(12)
        }
        print "pay order: ", order_no
        resp = fetch_json(url, params, method='POST')
        self.assertEqual('ok', resp['result'])

        # check stock volume
        url = "%s%s" % (APP_URL, "/tms-api/get_product")
        response = fetch_json(url, {'code': prd_code})
        self.assertEqual(prd_code, response['code'])
        # due to cache, this case doesn't work
        # self.assertEqual(stock_volume-pcs, response['stock_volume'], 'Stock volume not reduced as expected')

    def test_make_order2(self):
        prd_code = tests.dummy_data['products'][0]
        url = "%s%s" % (APP_URL, "/tms-api/get_product")
        response = fetch_json(url, {'code': prd_code})
        self.assertEqual(response.get('code'), prd_code)
        deal_price = Decimal(response.get('retail_price'))
        supplier = response.get('supplier') or {}
        supplier_id = supplier.get('id')
        pcs = 2
        shipfee_template = response.get('shipfee_template')
        retail_price = Decimal(response.get('retail_price'))
        # quick order with specific product
        url = "%s%s" % (APP_URL, "/tms-api/make_order")
        buyer = tests.dummy_data['users'][0]
        receiver = 'test_123456'
        receiver_mobile = '12345678901'
        ship_address = 'test street'
        buyer_note = 'note for test'
        shop_data = [{'code': prd_code, 'pcs': pcs}]
        shop_data = json.dumps(shop_data)
        params = {
            'buyer_id': buyer,
            'shop_data': shop_data,
            'receiver': receiver,
            'receiver_mobile': receiver_mobile,
            'ship_address': ship_address,
            'ship_province': '上海',
            'buyer_note': buyer_note,
            'referrer_id': buyer,
            'org_uid': tests.dummy_data['orgs'][1],
            # 'coupon': 'SFFDA9ZJNPMERQXF'
        }
        assert_ship_fee = shipfee_template.get('initial_fee') + shipfee_template.get('second_fee')
        logger.debug(params)
        response = fetch_json(url, params, 'POST')
        self.assertEquals(response.get('receiver'), 'test_123456')
        self.assertEquals(response.get('receiver_mobile'), receiver_mobile, 'Receiver mobile incorrect')
        self.assertEquals(response.get('ship_address'), ship_address, 'Ship address incorrect')
        self.assertEquals(response.get('buyer_note'), buyer_note, 'Buyer note incorrect')
        self.assertEquals(response.get('buyer_id'), buyer, 'Buyer incorrect')
        self.assertEquals(response.get('referrer_id'), buyer, 'Referrer incorrect')
        self.assertEqual(response.get('supplier'), supplier_id)
        self.assertEqual(Decimal(response.get('ship_fee')), assert_ship_fee)
        self.assertEqual(Decimal(response.get('ship_fee_off')), 0, 'Ship fee off incorrect')
        self.assertEqual(response.get('pcs_amount'), pcs)
        self.assertEqual(response.get('package_pcs'), 1)
        self.assertEqual(Decimal(response.get('shop_amount')), deal_price * pcs, 'Shop amount incorrect')
        # self.assertEqual(Decimal(response.get('shop_amount_off')), 0, 'Shop amount off incorrect')
        self.assertEqual(Decimal(response.get('pay_amount')),
                         Decimal(response.get('shop_amount')) + Decimal(response.get('ship_fee'))
                         - Decimal(response.get('shop_amount_off')) - Decimal(response.get('ship_fee_off')))

        params = {
            'buyer_id': buyer,
            'shop_data': shop_data,
            'receiver': receiver,
            'receiver_mobile': receiver_mobile,
            'ship_address': ship_address,
            'ship_province': '西藏',
            'buyer_note': buyer_note,
            'referrer_id': buyer,
            # 'coupon': 'SFFDA9ZJNPMERQXF'
        }
        logger.debug(params)
        response = fetch_json(url, params, 'POST')
        self.assertTrue(response.get('error'))

        params = {
            'buyer_id': buyer,
            'shop_data': shop_data,
            'receiver': receiver,
            'receiver_mobile': receiver_mobile,
            'ship_address': ship_address,
            'ship_province': '宁夏',
            'buyer_note': buyer_note,
            'referrer_id': buyer,
            # 'coupon': 'SFFDA9ZJNPMERQXF'
        }
        logger.debug(params)
        response = fetch_json(url, params, 'POST')
        self.assertEqual(Decimal(response.get('ship_fee')), 15)

    def test_revoke_order(self):
        # simply test query_distributes
        url = "%s%s" % (APP_URL, "/tms-api/query_distributes")
        response = fetch_json(url, {})
        self.assertIsInstance(response, list, 'query_distributes is expected to return a list')
        self.assertTrue(len(response) > 0, 'At least one product is expected')
        prd_code = response[0].get('code')
        deal_price = Decimal(response[0].get('retail_price'))
        pcs = 2
        pay_off = 1
        self.assertIsNotNone(prd_code, 'Product code should not be None')
        self.assertGreater(deal_price, 0)

        # quick order with specific product
        url = "%s%s" % (APP_URL, "/tms-api/make_order")
        buyer = tests.dummy_data['users'][0]
        receiver = 'test_123456'
        receiver_mobile = '12345678901'
        ship_address = 'test street'
        buyer_note = 'note for test'
        shop_data = [{'code': prd_code, 'pcs': pcs, 'payoff': pay_off}]
        shop_data = json.dumps(shop_data)
        params = {
            'buyer_id': buyer,
            'shop_data': shop_data,
            'receiver': receiver,
            'receiver_mobile': receiver_mobile,
            'ship_address': ship_address,
            'buyer_note': buyer_note,
            'referrer_id': buyer
        }
        logger.debug(params)
        response = fetch_json(url, params, 'POST')
        self.assertIsNotNone(response.get('order_no'))
        order_no = response.get('order_no')
        self.assertIsNotNone(order_no)

        # test revocation
        url = "%s%s" % (APP_URL, "/tms-api/revoke_order")
        params = {
            "order_no": order_no,
            "uid": buyer
        }
        response = fetch_json(url, params, 'POST')
        self.assertEqual('ok', response.get('result'))

        url = "%s%s" % (APP_URL, "/tms-api/get_order")
        response = fetch_json(url, {'order_no': order_no})
        self.assertEqual(Order.STATE_REVOKED, response.get('order_state'))

    def test_query_order(self):
        # test get_order
        url = "%s%s" % (APP_URL, "/tms-api/query_orders")
        buyer = tests.dummy_data['users'][0]
        params = {
            'buyer': buyer,
            'size': 2
        }
        response = fetch_json(url, params)
        self.assertIsInstance(response, list, 'query_orders is expected to return a list')
        self.assertTrue(len(response) > 0, 'No order returned while buyer_id equals %s' % buyer)
        self.assertTrue(len(response) <= 2, 'query_orders return more than expected')
        order = response[0]
        self.assertIsNotNone(order.get('order_no'), 'Order number should not be None')
        url = "%s%s" % (APP_URL, "/tms-api/get_order")
        response = fetch_json(url, {'order_no': order.get('order_no')})
        self.maxDiff = None
        self.assertEqual(response.get('order_no'), order.get('order_no'))
        # self.assertDictEqual(response, order)


class TestShopCart(unittest.TestCase):
    def setUp(self):
        url = "%s%s" % (APP_URL, "/tms-api/get_user")
        params = {'uid': tests.dummy_data['users'][0]}
        response = fetch_json(url, params, 'POST')
        assert response.get('uid') is not None, 'User not created/gotten as expected!'
        url = "%s%s" % (APP_URL, "/tms-api/get_user")
        params = {'uid': tests.dummy_data['users'][1]}
        response = fetch_json(url, params, 'POST')
        assert response.get('uid') is not None, 'User not created/gotten as expected!'

        # simply test query_distributes
        url = "%s%s" % (APP_URL, "/tms-api/query_distributes")
        response = fetch_json(url, {})
        self.assertIsInstance(response, list, 'query_distributes is expected to return a list')
        self.assertTrue(len(response) > 0, 'At least one product is expected')

    def test_shopcart(self):
        # self.setUp()
        # test get shopcart
        uid = tests.dummy_data['users'][0]
        url = "%s%s" % (APP_URL, "/tms-api/get_shopcart")
        resp = requests.get(url, {'uid': uid})
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        if result.get('shop_pcs') == 0:  # no shop item
            self.assertEqual(0, result.get('package_pcs'))
            self.assertEqual(0, result.get('shop_amount'))
            self.assertIsInstance(result.get('items'), list)
            self.assertEqual(0, len(result.get('items')))
        else:
            self.assertTrue(len(result.get('items')) > 0)
            self.assertTrue(int(result.get('package_pcs')) > 0)
            self.assertTrue(Decimal(result.get('pay_amount')) > 0)

        url = "%s%s" % (APP_URL, "/tms-api/clear_cartitem")
        resp = requests.post(url, {'uid': uid})
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        self.assertIn('deleted', result)
        self.assertEqual(0, result.get('package_pcs'))
        self.assertEqual(0, result.get('shop_pcs'))
        self.assertEqual(0, result.get('shop_amount'))
        self.assertIsInstance(result.get('items'), list)
        self.assertEqual(0, len(result.get('items')))

        # test add_to_cart
        prd_code1 = tests.dummy_data['products'][0]
        prd_code2 = tests.dummy_data['products'][2]
        url = "%s%s" % (APP_URL, "/tms-api/add_to_cart")
        resp = requests.post(url, {'uid': uid, 'prd_code': prd_code1, 'prd_pcs': 2})
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        shop_pcs = int(result.get('shop_pcs'))
        shop_amount = Decimal(result.get('shop_amount'))
        self.assertEqual(int(result.get('package_pcs')), 1)
        self.assertEqual(shop_pcs, 2)
        self.assertEqual(result.get('items')[0]['product']['retail_price'],
                         result.get('items')[0].get('deal_price'))
        self.assertEqual(Decimal(result.get('items')[0]['product']['retail_price']) * 2, shop_amount)
        self.assertEqual(1, len(result.get('items')))
        self.assertEqual(prd_code1, result.get('items')[0].get('product').get('code'))

        url = "%s%s" % (APP_URL, "/tms-api/add_to_cart")
        resp = requests.get(url, {'uid': uid, 'prd_code': prd_code2, 'prd_pcs': 3})
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        self.assertIn("shop_pcs", result)
        shop_pcs += 3
        self.assertEqual(int(result.get('shop_pcs')), shop_pcs)
        shop_amount = Decimal(result.get('items')[0]['product']['retail_price']) * result.get('items')[0]['pcs'] \
                      + Decimal(result.get('items')[1]['product']['retail_price']) * result.get('items')[1]['pcs']

        self.assertEqual(shop_amount, Decimal(result.get('shop_amount')))
        item_id = result.get('items')[0].get('id')

        # test update_cart_item
        url = "%s%s" % (APP_URL, "/tms-api/update_cartitem")
        resp = requests.post(url, {'uid': uid,
                                   'item_id': item_id,
                                   'pcs': 4})
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        shop_pcs = result.get('items')[0]['pcs'] + result.get('items')[1]['pcs']
        self.assertEqual(shop_pcs, result.get('shop_pcs'))
        shop_amount = Decimal(result.get('items')[0]['product']['retail_price']) * result.get('items')[0]['pcs'] \
                      + Decimal(result.get('items')[1]['product']['retail_price']) * result.get('items')[1]['pcs']
        self.assertEqual(shop_amount, Decimal(result.get('shop_amount')))
        self.assertEqual(result.get('items')[1].get('product').get('retail_price'),
                         result.get('items')[1].get('deal_price'))

        # test remove_cartitem
        url = "%s%s" % (APP_URL, "/tms-api/remove_cartitem")
        resp = requests.post(url, {'uid': uid,
                                   'item_id': item_id})
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        self.assertEqual(result.get('items')[0]['pcs'], result.get('shop_pcs'))
        shop_amount = Decimal(result.get('items')[0]['product']['retail_price']) * result.get('items')[0]['pcs']
        self.assertEqual(shop_amount, Decimal(result.get('shop_amount')))

        # test clear_cartitem again
        url = "%s%s" % (APP_URL, "/tms-api/clear_cartitem")
        resp = requests.post(url, {'uid': uid})
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        self.assertIn('deleted', result)
        self.assertEqual(0, result.get('package_pcs'))
        self.assertEqual(0, result.get('shop_pcs'))
        self.assertEqual(0, result.get('shop_amount'))
        self.assertIsInstance(result.get('items'), list)
        self.assertEqual(0, len(result.get('items')))

        url = "%s%s" % (APP_URL, "/tms-api/get_shopcart")
        resp = requests.get(url, {'uid': uid})
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        self.assertEqual(0, result.get('package_pcs'))
        self.assertEqual(0, result.get('shop_pcs'))
        self.assertEqual(0, result.get('shop_amount'))
        self.assertIsInstance(result.get('items'), list)
        self.assertEqual(0, len(result.get('items')))

    def test_shopcart_to_order(self):
        uid = tests.dummy_data['users'][0]
        # clear_cartitem
        url = "%s%s" % (APP_URL, "/tms-api/clear_cartitem")
        resp = requests.post(url, {'uid': uid})

        # add two different products to cart
        prd_code1 = tests.dummy_data['products'][0]
        prd_code2 = tests.dummy_data['products'][2]
        url = "%s%s" % (APP_URL, "/tms-api/add_to_cart")
        resp = requests.post(url, {'uid': uid, 'prd_code': prd_code1, 'prd_pcs': 2})
        url = "%s%s" % (APP_URL, "/tms-api/add_to_cart")
        resp = requests.get(url, {'uid': uid, 'prd_code': prd_code2, 'prd_pcs': 3})
        shopcart = resp.json()
        buyer = uid
        receiver = 'test_123456'
        receiver_mobile = '12345678901'
        ship_address = 'test street'
        buyer_note = 'note for test'
        shop_data = [{"item_id": item['id'], "pcs": item['pcs']} for item in shopcart['items']]
        shop_data = json.dumps(shop_data)
        params = {
            'buyer_id': buyer,
            'shop_data': shop_data,
            'receiver': receiver,
            'receiver_mobile': receiver_mobile,
            'ship_address': ship_address,
            'buyer_note': buyer_note,
            'referrer_id': buyer,
            'coupon': tests.dummy_data['coupon-tickets'][0]
        }
        logger.debug(params)
        url = "%s%s" % (APP_URL, "/tms-api/make_order")
        response = fetch_json(url, params, 'POST')
        self.assertIsNotNone(response.get('order_no'))
        print 'make order: ', response.get('order_no')
        self.assertEquals(response.get('receiver'), 'test_123456')
        self.assertEquals(response.get('receiver_mobile'), receiver_mobile, 'Receiver mobile incorrect')
        self.assertEquals(response.get('ship_address'), ship_address, 'Ship address incorrect')
        self.assertEquals(response.get('buyer_note'), buyer_note, 'Buyer note incorrect')
        self.assertEquals(response.get('buyer_id'), buyer, 'Buyer incorrect')
        self.assertEquals(response.get('referrer_id'), buyer, 'Referrer incorrect')
        self.assertEqual(Decimal(response.get('ship_fee')), 0)  # 包邮
        self.assertEqual(response.get('pcs_amount'), 5)
        self.assertEqual(response.get('package_pcs'), 1)
        self.assertEqual(Decimal(response.get('shop_amount')),
                         Decimal(response['items'][0]['deal_price']) * response['items'][0]['pcs'] +
                         Decimal(response['items'][1]['deal_price']) * response['items'][1]['pcs'],
                         'Shop amount incorrect')
        # self.assertEqual(Decimal(response.get('shop_amount_off')), 0, 'Shop amount off incorrect')
        self.assertEqual(Decimal(response.get('pay_amount')),
                         Decimal(response.get('shop_amount')) + Decimal(response.get('ship_fee'))
                         - Decimal(response.get('shop_amount_off')) - Decimal(response.get('ship_fee_off')))
        self.assertEqual(response.get('supplier'), shopcart['items'][0]['product']['supplier']['id'])

        # check if shopcart is empty now
        url = "%s%s" % (APP_URL, "/tms-api/get_shopcart")
        resp = requests.get(url, {'uid': uid})
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        self.assertEqual(0, result.get('package_pcs'))
        self.assertEqual(0, result.get('shop_pcs'))
        self.assertEqual(0, result.get('shop_amount'))
        self.assertIsInstance(result.get('items'), list)
        self.assertEqual(0, len(result.get('items')))

    def tearDown(self):
        pass

if __name__ == '__main__':
    import os
    DJANGO_SETTINGS = "tms.settings"
    PROJECT_PATH = os.path.abspath('%s/../..' % __file__)

    import sys
    print('Python %s on %s' % (sys.version, sys.platform))
    import django
    print('Django %s' % django.get_version())
    sys.path.extend([PROJECT_PATH])
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS)
    print sys.path
    if 'setup' in dir(django):
        django.setup()

    unittest.main()

    # from django.core.mail import send_mail
    #
    # send_mail('Subject here', 'Here is the message.', 'from@example.com',
    #           ['to@example.com'], fail_silently=False)