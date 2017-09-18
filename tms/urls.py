# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin

from tms.admin import store_site
from filemgmt.views import *


urlpatterns = patterns('',
        url(r'^tms/', include(admin.site.urls)),
        url(r'^stms/', include(store_site.urls)),
    )

if settings.IS_REMOTE_DEV or settings.IS_LOCAL_DEV:
    urlpatterns = patterns('',
        url(r'^tms/doc/', include('django.contrib.admindocs.urls')),
        url(r'^tms/', include(admin.site.urls)),
        url(r'^stms/', include(store_site.urls)),
    )
if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
        url(r'^images/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )

urlpatterns += patterns(
    'ueditor.views',
    url(r'^ueditor/controller/$', 'get_ueditor_controller')
)

urlpatterns += patterns(
    'filemgmt.views',
    url(r'^thumb/(?P<size>\d{1,4})' + settings.MEDIA_URL + '(?P<path>.*)$',
        'get_thumb'),
    url(r'^tms-api/admin/upload_image', upload_image),
)

urlpatterns += patterns(
    'basedata.fileimport',
    url(r'^tms-api/admin/import_product', 'import_product'),
    url(r'^tms-api/admin/import_order_logistic', 'import_order_logistic'),
    url(r'^tms-api/admin/import/order', 'import_order'),
)

urlpatterns += patterns(
    'basedata.views',
    url(r'^tms-api/admin/export/order/(?P<file_format>.*)$', 'export_order'),
    url(r'^tms-api/admin/export/productsalesmap/(?P<file_format>.*)$', 'export_product_sales_map'),
    url(r'^tms-api/admin/export/product/(?P<file_format>.*)$', 'export_product'),
    url(r'^export/order/(?P<file_format>.*)$', 'export_order'),
    url(r'^export/product/(?P<file_format>.*)$', 'export_product'),
    url(r'^tms-api/admin/preview/product/(?P<code>.*)$', 'preview_product'),
    url(r'^preview/product/(?P<code>.*)$', 'preview_product'),
    url(r'^tms-api/get_product', 'get_product'),
    url(r'^tms-api/query_products', 'query_products'),
    url(r'^tms-api/admin/query_multispec', 'query_multispec'),
    url(r'^tms-api/admin/remove_product', 'remove_product'),
    url(r'^tms-api/query_distributes', 'query_distributes'),
    url(r'^tms-api/get_shopcart', 'get_shopcart'),
    # url(r'^tms-api/get_shopcart_pcs', 'get_shopcart_pcs'),
    url(r'^tms-api/add_to_cart', 'add_to_cart'),
    url(r'^tms-api/remove_cartitem', 'remove_cartitem'),
    url(r'^tms-api/clear_cartitem', 'clear_cartitem'),
    url(r'^tms-api/update_cartitem', 'update_cartitem'),
    url(r'^tms-api/get_categories', 'get_categories'),
    url(r'^tms-api/oms/update_logistic', 'update_logistic2'),
    url(r'^tms-api/update_logistic', 'update_logistic'),
    url(r'^tms-api/update_stock_volume', 'update_stock_volume'),
    url(r'^tms-api/set_shelf', 'set_shelf'),
    url(r'^tms-api/update_product_price', 'update_product_price'),
    url(r'^tms-api/create_product_for_ls', 'create_product_for_ls'),
    url(r'^tms-api/make_product', 'make_product'),
    url(r'^tms-api/update_product', 'update_product'),
    url(r'^tms-api/mark_selected_cartitem', 'mark_selected_cartitem'),

)

urlpatterns += patterns('basedata.orderviews',
    url(r'^tms-api/get_order', 'get_order'),
    url(r'^tms-api/query_orders_with_reward', 'query_orders_with_reward'),
    url(r'^tms-api/query_orders', 'query_orders'),
    url(r'^tms-api/pre_order', 'pre_order'),
    url(r'^tms-api/make_order', 'make_order'),
    url(r'^tms-api/update_ship_address_order', 'update_ship_address_order'),
    url(r'^tms-api/set_ship_addr', 'set_ship_addr'),
    url(r'^tms-api/revoke_order', 'revoke_order'),
    url(r'^tms-api/transfer_order', 'transfer_order'),
    url(r'^tms-api/request_refund', 'request_refund'),
    url(r'^tms-api/mark_refunded', 'mark_refunded'),
    url(r'^tms-api/del_order', 'del_order'),
    url(r'^tms-api/use_coupon', 'use_coupon'),
    url(r'^tms-api/unuse_coupon', 'unuse_coupon'),
    url(r'^tms-api/pay_order', 'pay_order'),
    url(r'^tms-api/query_ship', 'query_ship'),
    url(r'^tms-api/ship_signoff', 'ship_signoff'),
    url(r'^tms-api/set_invoice', 'set_invoice'),
    url(r'^tms-api/set_order_note', 'set_order_note'),
    url(r'^callback/update_ship_status', 'update_ship_status'),
)

urlpatterns += patterns('profile.views',
    url(r'^tms-api/get_user', 'get_user'),
    url(r'^tms-api/register_user', 'register_user'),
    url(r'^tms-api/query_users', 'query_users'),
    url(r'^tms-api/update_user', 'update_user'),
    url(r'^tms-api/register_org', 'register_org'),
    url(r'^tms-api/query_orgs', 'query_orgs'),
    url(r'^tms-api/update_org', 'update_org'),
    url(r'^tms-api/review_org', 'review_org'),
    url(r'^tms-api/set_org_role', 'set_org_role'),
    url(r'^tms-api/add_link', 'add_link'),
    url(r'^tms-api/del_link', 'del_link'),
    url(r'^tms-api/bind_user', 'bind_user'),
    url(r'^tms-api/unbind_user', 'unbind_user'),
    url(r'^tms-api/get_ship_addr', 'get_ship_addr'),
    url(r'^tms-api/add_ship_addr', 'add_ship_addr'),
    url(r'^tms-api/del_ship_addr', 'del_ship_addr'),
    url(r'^tms-api/update_ship_addr', 'update_ship_addr'),
    url(r'^tms-api/query_accounts', 'query_accounts'),
    url(r'^tms-api/get_accounts_summary', 'get_accounts_summary'),
    url(r'^tms-api/get_supplier_accounts_summary', 'get_supplier_accounts_summary'),
    url(r'^tms-api/get_capital_accounts', 'get_capital_accounts'),
    url(r'^tms-api/bind_capital_account', 'bind_capital_account'),
    url(r'^tms-api/unbind_capital_account', 'unbind_capital_account'),
    url(r'^tms-api/request_withdraw', 'request_withdraw'),
    url(r'^tms-api/confirm_withdraw', 'confirm_withdraw'),
    url(r'^tms-api/query_withdraw_request', 'query_withdraw_request'),
    url(r'^tms-api/import_account_book', 'import_account_book'),
    url(r'^tms-api/deduct', 'deduct'),
    url(r'^tms-api/thanksgiving', 'thanksgiving'),
    url(r'^tms-api/result_withdraw', 'result_withdraw'),
    url(r'^tms-api/result_audit_withdraw', 'result_audit_withdraw'),
    url(r'^tms-api/bd_get_store_summary', 'bd_get_store_summary'),
    url(r'^tms-api/bd_query_accounts', 'bd_query_accounts'),
    url(r'^tms-api/bd_get_account_summary_all_staff', 'bd_get_account_summary_all_staff'),
)
urlpatterns += patterns('promote.views',
    url(r'^tms-api/query_rewards', 'query_rewards'),
    url(r'^tms-api/transfer_reward', 'transfer_reward'),
    url(r'^tms-api/get_rewards_summary', 'get_rewards_summary'),
    url(r'^tms-api/admin/export/reward_order', 'export_reward_order'),
    url(r'^export/reward_order', 'export_reward_order'),
    url(r'^tms-api/query_coupon_rules', 'query_coupon_rules'),
    url(r'^tms-api/get_coupon_ruleset', 'get_coupon_ruleset'),
    url(r'^tms-api/fetch_coupons', 'fetch_coupons'),
    url(r'^tms-api/query_coupons', 'query_coupons'),
    url(r'^tms-api/admin/export/couponticket', 'export_coupon_tickets'),
    url(r'^export/couponticket', 'export_coupon_tickets'),
    url(r'^tms-api/is_coupon_ok', 'is_coupon_ok'),
    url(r'^tms-api/haoli/use_haoli_coupon', 'use_haoli_coupon'),
    url(r'^tms-api/bd_get_rewards_summary', 'bd_get_rewards_summary'),
    url(r'^tms-api/bd_query_rewards', 'bd_query_rewards'),
)
urlpatterns += patterns('report.views',
    url(r'^tms-api/admin/export/reward', 'export_reward'),
    url(r'^export/reward', 'export_reward'),
    url(r'^tms-api/admin/report', 'report'),
    url(r'^tms-api/report/order_periodical_summary', 'order_periodical_summary'),
    url(r'^tms-api/report/query', 'query'),
    url(r'^tms-api/report/get', 'get'),
    url(r'^tms-api/report/feedback', 'feedback', name='report-views-feedback'),
)
urlpatterns += patterns('article.views',
    url(r'^tms-api/get_article_categories', 'get_article_categories'),
    url(r'^tms-api/get_article', 'get_article'),
    url(r'^tms-api/update_article', 'update_article'),
    url(r'^tms-api/admin/preview/article/(?P<article_id>.*)$', 'preview_article'),
    url(r'^preview/(?P<data_type>.*)/(?P<obj_id>.*)/(?P<timeout>.*)/(?P<token>.*)$', 'preview'),
)

urlpatterns += patterns('config.views',
    url(r'^tms-api/get_district', 'get_district'),
    # url(r'^tms-api/get_home', 'get_home'),  # replaced with get_navilinks
    url(r'^tms-api/get_navilinks', 'get_navilinks'),
    url(r'^/?$', 'index'),
    url(r'^tms-api/?$', 'show_api_helper'),
    url(r'^tms-api/get_appsettings', 'get_appsettings'),
)

urlpatterns += patterns('logistic.views',
    url(r'^tms-api/admin/print/invoice/$', 'print_invoice'),
    url(r'^tms-api/admin/print/express/$', 'print_express'),
    url(r'^tms-api/admin/get_express_template', 'get_express_template'),
    url(r'^tms-api/admin/set_express_template', 'set_express_template'),
    url(r'^tms-api/admin/del_express_template', 'del_express_template'),
)

urlpatterns += patterns('vendor.views',
                        url(r'^tms-api/get_hotel', 'get_hotel'),
                        url(r'^tms-api/query_agents', 'query_agents'),
                        url(r'^tms-api/query_hotels', 'query_hotels'),
                        url(r'^tms-api/admin/preview/hotel/(?P<hotel_id>.*)$', 'preview_hotel'),
                        url(r'^preview/hotel/(?P<hotel_id>.*)$', 'preview_hotel'),
                        url(r'^tms-api/get_notice', 'get_notice'),
                        url(r'^tms-api/update_notice', 'update_notice'),
                        url(r'^tms-api/get_supplier', 'get_supplier'),
                        url(r'^tms-api/query_supplier_incomes', 'query_supplier_incomes'),
                        url(r'^tms-api/query_suppliers', 'query_suppliers'),
                        url(r'^tms-api/create_store', 'create_store'),
                        url(r'^tms-api/query_stores', 'query_stores'),
                        url(r'^tms-api/query_logistic_vendors', 'query_logistic_vendors'),
                        url(r'^tms-api/get_brands', 'get_brands'),
                        )

urlpatterns += patterns('log.views',
    url(r'^tms-api/query_wechat_msg', 'query_wechat_msg'),
    url(r'^tms-api/wechat_to', 'wechat_to'),
    url(r'^tms-api/email_to', 'email_to'),
    url(r'^tms-api/mark_wechat_msg', 'mark_wechat_msg'),
    url(r'^tms-api/admin/export/paylog', 'export_paylog'),
    url(r'^export/paylog', 'export_paylog'),
)

urlpatterns += patterns('credit.views',
    url(r'^tms-api/get_credit_summary', 'get_credit_summary'),
    url(r'^tms-api/query_credits', 'query_credits'),
    url(r'^tms-api/set_credit', 'set_credit'),
    url(r'^tms-api/get_medals', 'get_medals'),
    url(r'^tms-api/set_medal', 'set_medal'),
)

# urlpatterns += patterns('basedata.syncapi',
#     url(r'^tms-api/sync/twohou_product', 'sync_twohou_product_view'),
#     url(r'^tms-api/sync/get_products', 'get_products'),
#     url(r'^tms-api/sync/get_orders', 'get_orders'),
#     url(r'^tms-api/sync/update_order', 'update_order'),
# )

urlpatterns += patterns('buding.views',
                        url(r'^tms-api/bd_register_shopkeeper', 'bd_register_shopkeeper'),
                        url(r'^tms-api/bd_register_shop', 'bd_register_shop'),
                        url(r'^tms-api/bd_get_shopkeeper', 'bd_get_shopkeeper'),
                        url(r'^tms-api/bd_update_shopkeeper', 'bd_update_shopkeeper'),
                        url(r'^tms-api/bd_update_shop', 'bd_update_shop'),
                        url(r'^tms-api/bd_query_shops', 'bd_query_shops'),
                        url(r'^tms-api/bd_query_products', 'bd_query_products'),
                        url(r'^tms-api/bd_get_saleshop', 'bd_get_saleshop'),
                        url(r'^tms-api/bd_register_employee', 'bd_register_employee'),
                        url(r'^tms-api/bd_put_offshelf', 'bd_put_offshelf'),
                        url(r'^tms-api/bd_put_onshelf', 'bd_put_onshelf'),
                        url(r'^tms-api/bd_delete_shopproduct', 'bd_delete_shopproduct'),
                        url(r'^tms-api/bd_get_user', 'bd_get_user'),
                        url(r'^tms-api/bd_getusersfromshop', 'bd_getusersfromshop'),
                        url(r'^tms-api/bd_update_product', 'bd_update_product'),
                        url(r'^tms-api/bd_deleteuserfromshop', 'bd_deleteuserfromshop'),
                        )
