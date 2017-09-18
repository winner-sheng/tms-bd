# -*- coding: utf-8 -*-
from django.contrib.admin import AdminSite
from django.contrib import admin
from settings import STORE_NAME
__author__ = 'Winsom'


class StoreSite(AdminSite):
    site_header = site_title = index_title = STORE_NAME


store_site = StoreSite(name='tms')
admin.site.site_header = admin.site.site_title = admin.site.index_title = STORE_NAME
