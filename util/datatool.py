# -*- coding: utf-8 -*-
__author__ = 'Winsom'


# def import_agent(file_name):
#     """
#     导入门店及门店前台账号
#     数据文件为csv格式或excel
#     门店编码	门店名称	用户账号	名	姓	邮件地址
#
#     :return:
#     """
#     from django.contrib.auth.models import User
#     from vendor.models import StoreAgent, Store
#     from django.db.utils import IntegrityError
#     import os
#
#     if not os.path.exists(file_name):
#         print 'File %s NOT exists!' % file_name
#         return
#
#     try:
#         open(file_name, 'r')
#     except IOError, e:
#         print 'Read %s FAILED: %s' % (file_name, e.message or e.args[1])
#         return
#
#     accounts = open(file_name)
#     for acct, pwd in accounts:
#         print acct, ' : ', pwd
#         user = User(username=acct, is_staff=True)
#         user.set_password(pwd)
#         try:
#             user.save()
#         except IntegrityError:
#             user = User.objects.get(username=acct)
#
#         try:
#             store = Store.objects.get(coupon=acct)
#             StoreAgent(store=store, user=user).save()
#         except Store.DoesNotExist:
#             print 'Store with coupon %s does NOT exists.'
#
#
# def refresh():
#     # from django.db import connection
#     # cursor = connection.cursor()
#     # cursor.execute('select distinct brand from basedata_product where brand!="" order by convert(brand using gbk)')
#     # rows = cursor.fetchall()
#     # brands = [p[0] for p in rows]
#     from basedata.models import Product
#     from config.models import Brand
#     brands = Product.objects.extra(select={'brand_gbk': 'convert(brand using gbk)'})
#     brands = brands.order_by('brand_gbk').values('brand').distinct()
#     brands = [b['brand'].strip() for b in brands if b['brand']]
#     count = len(brands)
#     for brand in brands:
#         b, created = Brand.objects.update_or_create(name=brand, defaults={'list_order': count})
#         count -= 1
#         b.save()
#
#     return brands
#
#
# if __name__ == '__main__':
#     import os
#     os.environ['DJANGO_SETTINGS_MODULE'] = 'tms.settings'
#     import_agent()