# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
from tms.settings import APP_URL
from django.test import Client, TestCase
from util.webtool import fetch_json, fetch_url
from util.renderutil import random_str, day_str
import tests
__author__ = 'winsom'


class TestProfile(unittest.TestCase):
    def test_manage_ship_addr(self):
        # add an address
        url_add = "%s%s" % (APP_URL, "/tms-api/add_ship_addr")
        params = {'uid': tests.dummy_data['users'][0],
                  'receiver': tests.dummy_data['users'][0],
                  'mobile': '12345678901',
                  'address': 'test street',
                  'ship_province': '上海',
                  'zipcode': '123456'}
        response = fetch_json(url_add, params, 'POST')
        self.assertEqual('ok', response.get('result'), 'Error unexpected: %s' % response.get('error'))
        self.assertIsNotNone(response.get('id'))
        addr_id = response.get('id')

        # add another address
        url_add = "%s%s" % (APP_URL, "/tms-api/add_ship_addr")
        params = {'uid': tests.dummy_data['users'][0],
                  'receiver': tests.dummy_data['users'][0],
                  'mobile': '12345678901',
                  'address': 'test to del street',
                  'ship_province': '上海',
                  'zipcode': '123456'}
        response = fetch_json(url_add, params, 'POST')
        addr_del_id = response.get('id')

        # get addresses, at least two
        url_get = "%s%s" % (APP_URL, "/tms-api/get_ship_addr")
        response = fetch_json(url_get, {'uid': tests.dummy_data['users'][0]})
        self.assertIsInstance(response, list, 'get_ship_addr is expected to returned a list result')
        self.assertTrue(len(response) >= 2, 'At least two addresses supposed there, after two additions')
        self.assertIn(addr_id, [addr.get('id') for addr in response], 'New address is expected to be in the reslut list')

        # delete the latter address
        url_del = "%s%s" % (APP_URL, "/tms-api/del_ship_addr")
        response = fetch_json(url_del, {'uid': tests.dummy_data['users'][0], 'addr_id': addr_del_id}, 'POST')
        self.assertTrue(response.get('result') == 'ok', 'Delete failed')

        # query again, and ensure one deleted and one remained
        response = fetch_json(url_get, {'uid': tests.dummy_data['users'][0]})
        self.assertIsInstance(response, list, 'get_ship_addr is expected to returned a list result')
        addr_ids = [addr.get('id') for addr in response]
        self.assertIn(addr_id, addr_ids, 'New address is supposed to be retained after another one deleted')
        self.assertNotIn(addr_del_id, addr_ids, 'Deleted address is supposed not existing any more')

    def test_capital_account(self):
        # bind user account
        print 'binding user capital account'
        user = tests.dummy_data['users'][0]
        url = "%s%s" % (APP_URL, "/tms-api/bind_capital_account")
        ca_no = user
        response = fetch_json(url, {'uid': user, "ca_no": ca_no, 'ca_name': user}, method='POST')
        self.assertEqual('ok', response.get('result'))
        # self.assertEqual(user, response.get('ca_name'))
        # self.assertEqual(ca_no, response.get('ca_no'))
        account_id = response.get('id')

        url = "%s%s" % (APP_URL, "/tms-api/get_capital_accounts")
        response = fetch_json(url, {'uid': user})
        self.assertIsInstance(response, list)
        self.assertTrue(len(response) > 0)
        self.assertIn(account_id, [item.get('id') for item in response])

        # unbind user account
        print 'unbinding user capital account'
        url = "%s%s" % (APP_URL, "/tms-api/unbind_capital_accounts")
        response = fetch_json(url, {'uid': user, 'account_id': account_id}, method='POST')
        self.assertEqual('ok', response.get('result'))

        url = "%s%s" % (APP_URL, "/tms-api/get_capital_accounts")
        response = fetch_json(url, {'uid': user})
        self.assertIsInstance(response, list)
        self.assertNotIn(account_id, [item.get('id') for item in response])

        # bind user with a specific supplier
        url = "%s%s" % (APP_URL, "/tms-api/bind_user")
        supplier = tests.dummy_data['tms-user'][1]
        params = {
            "uid": user,
            "account": supplier,
            "passwd": '123456',
            "override": 1
        }
        resp = fetch_json(url, params, method='POST')
        self.assertIn('suppliers', resp)
        self.assertIsInstance(resp.get('suppliers'), list)
        supplier_id = resp.get('suppliers')[0].get('id')
        print "binded user: %s with supplier: %s" % (user, resp.get('suppliers')[0].get('name'))

        # bind supplier account
        print 'binding supplier capital account'
        url = "%s%s" % (APP_URL, "/tms-api/bind_capital_account")
        ca_no = tests.dummy_data['users'][0]
        params = {'uid': user,
                  "supplier_id": supplier_id,
                  "ca_name": tests.dummy_data['users'][0]+"-1",
                  "ca_mobile": '123456789',
                  "ca_type": 'deposit',
                  "ca_no": ca_no,
                  "open_bank": "徐家汇分行",
                  "bank_code": "THB",
                  "bank_name": "土猴银行"}

        response = fetch_json(url, params, method='POST')
        print response
        self.assertIn('id', response)
        account_id = response.get('id')

        # unbind supplier account
        print 'unbinding supplier capital account'
        url = "%s%s" % (APP_URL, "/tms-api/unbind_capital_accounts")
        params = {'uid': user,
                  "supplier_id": supplier_id,
                  "account_id": account_id
                  }

        response = fetch_json(url, params, method='POST')
        self.assertEqual('ok', response.get('result'))

        # unbind supplier account
        print 'unbinding supplier capital account'
        url = "%s%s" % (APP_URL, "/tms-api/unbind_capital_accounts")
        params = {'uid': user,
                  "account_id": account_id
                  }

        response = fetch_json(url, params, method='POST')
        self.assertTrue(response.get('error'))

    def test_register_user(self):
        time_str = day_str(str_format='%y%m%d%H%M%f')[1:]
        url = "%s%s" % (APP_URL, "/tms-api/register_user")
        params = {'mobile': time_str,
                  'ex_nick_name': 'ex_nick_name',
                  'ex_avatar': 'ex_avatar',
                  'nick_name': 'nick_name',
                  'avatar': 'avatar.png',
                  'real_name': 'real_name',
                  'id_card': None,
                  'intro': 'test intro',
                  'entry_uid': 'test_12345678',
                  'referrer': 'test_12345678',
                  'org_uid': None}
        resp = fetch_json(url, params, method='POST')
        self.assertIn('uid', resp)
        user_uid = resp.get('uid')

        time_str = day_str(str_format='%y%m%d%H%M%f')[1:]
        url = "%s%s" % (APP_URL, "/tms-api/register_org")
        params = {'uid': user_uid,
                  'name': 'org%s' % time_str,
                  'id_card_image': 'test_id_card.png',
                  'license_image': 'test_license_image.png',
                  'intro': 'test intro',
                  'logo': 'test_logo.png',
                  'contact_name': 'contact_name'
                  }

        resp = fetch_json(url, params, method='POST')
        self.assertIn('uid', resp)
        org_uid = resp.get('uid')

        time_str = day_str(str_format='%y%m%d%H%M%f')[1:]
        url = "%s%s" % (APP_URL, "/tms-api/register_user")
        params = {'mobile': time_str,
                  'ex_nick_name': 'ex_nick_name',
                  'ex_avatar': 'ex_avatar',
                  'nick_name': 'nick_name',
                  'avatar': 'avatar.png',
                  'real_name': 'real_name',
                  'id_card': None,
                  'intro': 'test intro',
                  'entry_uid': 'test_12345678',
                  'referrer': 'test_12345678',
                  'org_uid': org_uid}
        resp = fetch_json(url, params, method='POST')
        self.assertEqual('无效的归属企业', resp.get('error'))
        # self.assertIn('uid', resp)
        params = {'mobile': time_str,
                  'ex_nick_name': 'ex_nick_name',
                  'ex_avatar': 'ex_avatar',
                  'nick_name': 'nick_name',
                  'avatar': 'avatar.png',
                  'real_name': 'real_name',
                  'id_card': None,
                  'intro': 'test intro',
                  'entry_uid': 'test_12345678',
                  'referrer': 'test_12345678',
                  'org_uid': tests.dummy_data['orgs'][1]}
        resp = fetch_json(url, params, method='POST')
        user_uid2 = resp.get('uid')

        time_str = day_str(str_format='%y%m%d%H%M%f')[1:]
        url = "%s%s" % (APP_URL, "/tms-api/register_org")
        params = {'uid': user_uid2,
                  'name': 'org%s' % time_str,
                  'is_group': 1,
                  'id_card_image': 'test_id_card.png',
                  'license_image': 'test_license_image.png',
                  'intro': 'test intro',
                  'logo': 'test_logo.png',
                  'contact_name': 'contact_name'
                  }

        resp = fetch_json(url, params, method='POST')
        self.assertIn('uid', resp)
        group_uid = resp.get('uid')

        url = "%s%s" % (APP_URL, "/tms-api/update_org")
        params = {'uid': user_uid2,
                  'org_uid': org_uid,
                  'group_uid': group_uid}
        resp = fetch_json(url, params, method='POST')
        self.assertTrue(len(resp.get('error')) > 0)  # 没权限
        params = {'uid': user_uid,
                  'org_uid': org_uid,
                  'group_uid': group_uid}
        resp = fetch_json(url, params, method='POST')
        self.assertTrue('ok', resp.get('result'))

        url = "%s%s" % (APP_URL, "/tms-api/add_link")
        params = {'uid': user_uid,
                  'org_uid': group_uid,
                  'link_type': 'website',
                  'link': 'http://test.link/'}
        resp = fetch_json(url, params, method='POST')
        self.assertTrue(len(resp.get('error')) > 0)  # 没权限

        url = "%s%s" % (APP_URL, "/tms-api/add_link")
        params = {'uid': tests.dummy_data['users'][0],
                  'org_uid': tests.dummy_data['orgs'][1],
                  'link_type': 'website',
                  'link': 'http://test.link/'}
        resp = fetch_json(url, params, method='POST')
        self.assertTrue('ok', resp.get('result'))
        self.assertIn('id', resp)
        link_id = resp.get('id')

        url = "%s%s" % (APP_URL, "/tms-api/query_orgs")
        params = {'uid': ",".join([org_uid, group_uid])}
        resp = fetch_json(url, params, method='POST')
        self.assertTrue(len(resp) == 0)
        self.assertIsInstance(resp, list)

        url = "%s%s" % (APP_URL, "/tms-api/query_orgs")
        params = {'uid': ",".join([org_uid, group_uid]),
                  "review_status": 'pending',
                  "status": 'all',
                  "with_links": 1}
        resp = fetch_json(url, params, method='POST')
        self.assertTrue(len(resp) > 0)
        self.assertIsInstance(resp, list)

        # url = "%s%s" % (APP_URL, "/tms-api/del_link")
        # params = {'uid': user_uid2,
        #           'link_id': link_id}
        # resp = fetch_json(url, params, method='POST')
        # self.assertTrue('ok', resp.get('result'))

    def test_bind_user(self):
        url = "%s%s" % (APP_URL, "/tms-api/bind_user")
        params = {
            "uid": tests.dummy_data['users'][0],
            "account": tests.dummy_data['tms-user'][0],
            "passwd": '123456',
            "override": 1
        }
        resp = fetch_json(url, params, method='POST')
        print resp
        self.assertNotIn('error', resp)
        self.assertEqual(tests.dummy_data['users'][0], resp.get('uid'))
        self.assertEqual(tests.dummy_data['tms-user'][0], resp.get('username'))

        del params['override']
        resp = fetch_json(url, params, method='POST')
        self.assertIn('error', resp)

        url = "%s%s" % (APP_URL, "/tms-api/unbind_user")
        resp = fetch_json(url, params, method='POST')
        self.assertTrue(not resp.get('error'))
        self.assertEqual('ok', resp.get('result'))

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