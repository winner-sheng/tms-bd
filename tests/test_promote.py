# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import unittest
from decimal import Decimal

import requests

from basedata.models import Product, Order
from tests import init
from tms.settings import APP_URL
from util.renderutil import random_str, logger
from util.webtool import fetch_json
import tests
__author__ = 'winsom'


class TestPromote(unittest.TestCase):

    def setUp(self):
        pass

    def test_coupon_rule(self):
        # simply test query_coupon_rules
        url = "%s%s" % (APP_URL, "/tms-api/query_coupon_rules")
        response = fetch_json(url, {'code': ','.join(tests.dummy_data['coupon-rules'])})
        self.assertIsInstance(response, list)
        self.assertEqual(len(response), 2)
        self.assertIn(response[0].get('code'), tests.dummy_data['coupon-rules'])
        self.assertIn(response[1].get('code'), tests.dummy_data['coupon-rules'])

        # simply test query_coupons
        url = "%s%s" % (APP_URL, "/tms-api/query_coupons")
        response = fetch_json(url, {'uid': tests.dummy_data['users'][0], "size": 9999})
        self.assertIsInstance(response, list)
        coupon_cnt = len(response)

        # simply test fetch coupons
        url = "%s%s" % (APP_URL, "/tms-api/fetch_coupons")
        tickets = fetch_json(url, {'uid': tests.dummy_data['users'][0],
                                   'rules': "%s,2|%s,3" % (tests.dummy_data['coupon-rules'][0],
                                                           tests.dummy_data['coupon-rules'][1])})
        self.assertIn('tickets', tickets)
        tickets = tickets.get('tickets')
        self.assertEqual(len(tickets), 5)
        self.assertIn(tickets[0].get('rule').get('code'), tests.dummy_data['coupon-rules'])
        if not tickets[0].get('rule').get('allow_dynamic'):
            self.assertEqual(tickets[0].get('expiry_date'), tickets[0].get('rule').get('end_time'))

        # simply test is_coupon_ok
        url = "%s%s" % (APP_URL, "/tms-api/is_coupon_ok")
        ticket_codes = [t.get('code') for t in tickets]
        response = fetch_json(url, {'uid': tests.dummy_data['users'][0],
                                    'coupon': ','.join(ticket_codes)})
        self.assertTrue(isinstance(response, dict))
        self.assertEqual(len(response), len(ticket_codes))
        for code, res in response.items():
            self.assertIn(code, ticket_codes)
            self.assertTrue(res)

        # simply test query_coupons
        url = "%s%s" % (APP_URL, "/tms-api/query_coupons")
        response = fetch_json(url, {'uid': tests.dummy_data['users'][0],
                                    "size": 9999})
        self.assertIsInstance(response, list)
        if len(response) < 9999 - 5:
            self.assertEqual(len(response), coupon_cnt + 5)

        coupon = response[0].get('code')
        # test pre_order
        url = "%s%s" % (APP_URL, "/tms-api/pre_order")
        buyer = tests.dummy_data['users'][0]
        receiver = buyer
        receiver_mobile = '12345678901'
        ship_address = 'test street'
        buyer_note = 'note for test'
        shop_data = [{'code': tests.dummy_data['products'][0], 'pcs': 1}]
        shop_data = json.dumps(shop_data)
        params = {
            'buyer_id': buyer,
            'shop_data': shop_data,
            'receiver': receiver,
            'receiver_mobile': receiver_mobile,
            'ship_address': ship_address,
            'buyer_note': buyer_note,
            'referrer_id': buyer,
            'coupon': coupon
        }
        logger.debug(params)
        response = fetch_json(url, params, 'POST')
        self.assertNotIn('shop_amount_off', response)
        self.assertNotEqual(response.get('error'), '')

        shop_data = [{'code': tests.dummy_data['products'][0], 'pcs': 10}]
        shop_data = json.dumps(shop_data)
        params['shop_data'] = shop_data
        response = fetch_json(url, params, 'POST')
        self.assertEqual(Decimal(response.get('shop_amount_off')), 10)

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
