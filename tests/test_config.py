__author__ = 'winsom'

import unittest
import requests
from tms import settings


class ApiTestCase(unittest.TestCase):
    api_list = ["add_link",
                "add_ship_addr",
                "add_to_cart",
                "bind_user",
                "del_link",
                "del_order",
                "del_ship_addr",
                "email_to",
                "fetch_coupons",
                "get_accounts_summary",
                "get_categories",
                "get_order",
                "get_product",
                "get_rewards_summary",
                "get_ship_addr",
                "get_shopcart",
                "get_shopcart_pcs",
                "get_supplier",
                "get_user",
                "is_coupon_ok",
                "make_order",
                "mark_wechat_msg",
                "pay_order",
                "query_accounts",
                "query_coupon_rules",
                "query_distributes",
                "query_orders",
                "query_orders_with_reward",
                "query_orgs",
                "query_products",
                "query_rewards",
                "query_ship",
                "query_suppliers",
                "query_users",
                "query_wechat_msg",
                "register_org",
                "remove_cartitem",
                "report/get",
                "report/query",
                "report/feedback",
                "request_refund",
                "review_org",
                "revoke_order",
                "set_invoice",
                "set_order_note",
                "set_org_role",
                "set_shelf",
                "set_ship_addr",
                "thanksgiving",
                "update_cartitem",
                "update_org",
                "update_logistic",
                "update_ship_addr",
                "update_stock_volume",
                "update_user",
                "use_coupon",
                "unuse_coupon",
                "wechat_to"]

    def _test_api(self, base_url):
        fails = []
        for api in self.api_list:
            url = '%s/tms-api/%s' % (base_url, api)
            print "testing api: %s" % api,
            resp = requests.post(url)
            if resp.status_code == 200:
                print "ok"
            else:
                print "failed"
                fails.append((api, resp.reason,))

        url = '%s/callback/update_ship_status' % base_url
        print "testing api: update_ship_status"
        resp = requests.post(url)
        if resp.status_code == 200:
            print "ok"
        else:
            print "failed"
            fails.append(('update_ship_status', resp.reason,))
        self.assertEqual(len(fails), 0, 'Below api failed: \n%s' % '\n'.join(["%s: %s" % (f[0], f[1]) for f in fails]))

        self.assertEqual(resp.status_code, 200, 'Open api(update_ship_status) failed: %s' % resp.reason)

    def test_local_api(self):
        self._test_api(settings.APP_URL)

    # def test_test_api(self):
    #     self._test_api('http://test.tmonkey.cn:8001/')

    # def test_prd_api(self):
    #     self._test_api('http://tms.twohou.com:8001/')


if __name__ == '__main__':
    unittest.main()
