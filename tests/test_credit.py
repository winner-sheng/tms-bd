# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
from tms.settings import APP_URL
from django.test import Client, TestCase
from util.webtool import fetch_json, fetch_url
from util.renderutil import random_str, day_str
import tests
__author__ = 'winsom'


class TestCredit(unittest.TestCase):
    def test_medal(self):
        user = tests.dummy_data['users'][0]
        url = "%s%s" % (APP_URL, "/tms-api/get_medals")
        params = {}
        resp = fetch_json(url, params)
        self.assertIsInstance(resp, list)
        self.assertTrue(len(resp) > 0)

        url = "%s%s" % (APP_URL, "/tms-api/set_medal")
        params = {'uid': user,
                  'medal': resp[0].get('code')}
        resp = fetch_json(url, params, 'POST')
        self.assertEqual('ok', resp.get('result'))

    def test_credit(self):
        user = tests.dummy_data['users'][0]
        url = "%s%s" % (APP_URL, "/tms-api/set_credit")
        params = {'uid': user,
                  'figure': 10,
                  'source': 'test',
                  'scenario': 'test scenario',
                  'extra_type': 'test.type',
                  'extra_data': 'test.data'}
        resp = fetch_json(url, params, 'POST')
        self.assertEqual(user, resp.get('uid'))
        total = resp.get('total')
        expense = resp.get('expense')
        income = resp.get('income')

        url = "%s%s" % (APP_URL, "/tms-api/get_credit_summary")
        params = {'uid': user}
        resp = fetch_json(url, params, 'POST')
        self.assertEqual(user, resp.get('uid'))
        self.assertEqual(total, resp.get('total'))
        self.assertEqual(income, resp.get('income'))
        self.assertEqual(expense, resp.get('expense'))

        url = "%s%s" % (APP_URL, "/tms-api/set_credit")
        params = {'uid': user,
                  'figure': 10,
                  'is_income': '0',
                  'source': 'test',
                  'scenario': 'test.scenario',
                  'extra_type': 'test.type',
                  'extra_data': 'test.data'}
        resp = fetch_json(url, params, 'POST')
        self.assertEqual(total - 10, resp.get('total'))
        self.assertEqual(income, resp.get('income'))
        self.assertEqual(expense + 10, resp.get('expense'))

        url = "%s%s" % (APP_URL, "/tms-api/query_credits")
        params = {'uid': user}
        resp = fetch_json(url, params)
        self.assertIsInstance(resp, list)
        self.assertTrue(len(resp) > 0)
        self.assertEqual(user, resp[0].get('uid'))
        self.assertEqual(False, resp[0].get('is_income'))
        self.assertEqual('test', resp[0].get('source'))
        self.assertEqual(10, resp[0].get('figure'))
        self.assertEqual('test.scenario', resp[0].get('scenario'))
        self.assertEqual('test.type', resp[0].get('extra_type'))
        self.assertEqual('test.data', resp[0].get('extra_data'))


if __name__ == '__main__':
    # DJANGO_SETTINGS = "tms.settings"
    # PROJECT_PATH = os.path.abspath('%s/../..' % __file__)
    #
    # import sys
    # print('Python %s on %s' % (sys.version, sys.platform))
    # import django
    # print('Django %s' % django.get_version())
    # sys.path.extend([PROJECT_PATH])
    # import os
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS)
    # print sys.path
    # if 'setup' in dir(django):
    #     django.setup()

    unittest.main()

    # from django.core.mail import send_mail
    #
    # send_mail('Subject here', 'Here is the message.', 'from@example.com',
    #           ['to@example.com'], fail_silently=False)