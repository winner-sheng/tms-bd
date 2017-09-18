# -*- coding: utf-8 -*-
from __future__ import unicode_literals
__author__ = 'winsom'

from django.test import Client, TestCase


class TestVendor(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_supplier(self):
        client = Client()
        client.get('/tms-api/get_supplier', {'code': 'test-sup'})
        print 'done'