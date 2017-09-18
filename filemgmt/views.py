# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect

# from django.contrib.auth.decorators import login_required

from models import *
from util.renderutil import json_response, random_str, logger
from util.imageutil import image_type


def get_thumb(request, size, path):
    """
    给定缩略图的url，检查并返回其实际有效的URL，如
    包含路径“/thumb/64/images/logo/test.png”的请求，会转发到该api进行处理，size=64， path="images/logo/test.png"
    api会检查图片是否存在，如果不存在则检查原图是否存在，存在则自动生成相应size宽度的缩略图，并返回有效url
    （如上述的样例中，最终返回的url路径为“/images/thumb/64/logo/test.png”）
    :param request:
    :param size: 期望的缩略图宽度尺寸，高度按等比例缩放
    :param path: 图片路径
    :return:
    """
    image_path = '%s%s' % (settings.MEDIA_ROOT, path)
    #if not os.path.isfile(image_path):
    #    raise IOError('Image file NOT found or unreadable!')
    thumb = check_thumb_url(image_path, int(size), path)
    return HttpResponseRedirect(thumb if thumb else "/image_not_exists/"+path)


def upload_image(request):
    """
    上传图片
    :param request:
    :return:
        返回上传图片的绝对引用路径及图片id
    """
    result = []
    files = request.FILES.getlist('images')
    cur_time = timezone.now() if settings.USE_TZ else datetime.datetime.now()
    path = cur_time.strftime('%Y/%m/%d')
    for f in files:
        image_path = "%sposts/%s/%s_%s" % (settings.MEDIA_ROOT, path, random_str(6), f.name[-12:])
        image_dir, image_name = os.path.split(image_path)
        os.path.exists(image_dir) or os.makedirs(image_dir, mode=0744)

        destination = open(image_path, 'wb+')
        logger.debug(image_path)

        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
        rel_path = image_path[len(settings.MEDIA_ROOT):]
        if image_type(image_path):
            image = BaseImage(origin=rel_path, image_desc='User Post Image')
            image.save()
            logger.debug("id:%s: %s" % (image.id, image.origin.url))
            result.append({'img_id': image.id, "image": image.origin.url})
        else:
            logger.debug("Invalid image: %s" % destination)
    return json_response(result)


def upload_file(request):
    """
    上传文件
    :param request:
    :return:
        返回上传文件的绝对引用路径
    """
    result = []
    files = request.FILES.getlist('files')
    cur_time = timezone.now() if settings.USE_TZ else datetime.datetime.now()
    path = cur_time.strftime('%Y-%m-%d')
    for f in files:
        file_path = "%supload/%s/%s_%s" % (settings.STATIC_ROOT, path, random_str(6), f.name[-12:])
        if not os.path.abspath(file_path).startswith(ABS_MEDIA_ROOT):
            # TODO: invalid path given (out of MEDIA_ROOT) or file not exists, must be log for security audit
            logger.error("Invalid file path: %s" % file_path)
            continue
        file_dir, file_name = os.path.split(file_path)
        os.path.exists(file_dir) or os.makedirs(file_dir, mode=0744)

        destination = open(file_path, 'wb+')
        logger.debug(file_path)

        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
        file_url = "%s%s" % (settings.STATIC_URL, file_path[len(settings.STATIC_ROOT):])
        result.append(file_url)

    return json_response(result)























# def load_agent(excel_file):
#     """
#     导入门店及门店前台账号
#     数据文件为csv格式或excel
#     # NC, 酒店简称, 用户名, Hotel ID, 密码, 酒店法定名称, 酒店地址, 邮编
#     # 店长姓名, 联系电话, 邮箱, 城市
#     :return:
#     """
#     from django.contrib.auth.models import User
#     from vendor.models import StoreAgent, Store, Contact
#     from django.db.utils import IntegrityError
#     import os
#
#     import xlrd
#     # excel_file = "f:/twohou/pilot_accounts.xls"
#     result = {"success": [], "error": [], "warning": []}
#     try:
#         print "Reading excel file: %s" % os.path.abspath(excel_file)
#         book = xlrd.open_workbook(excel_file)
#         data_sheet = book.sheet_by_index(0)
#     except Exception, e:
#         raise IOError("解析Excel失败：%s" % e.message)
#
#     # read data sheet and save to DB
#     # NC, 酒店简称, 用户名, Hotel ID, 密码, 酒店法定名称, 酒店地址, 邮编
#     # 店长姓名, 联系电话, 邮箱, 城市, 优惠码
#     # stores = {}
#     counter = {'user': 0, 'contact': 0, 'store': 0, 'store_agent': 0}
#     for x in range(1, data_sheet.nrows):  # ignore header
#         try:
#             row = data_sheet.row_values(x)
#             contact_name = row[8]
#             contact_mobile = _to_str(row[9])  # due to xlrd always convert int to float
#             contact_email = row[10]
#             contact = None
#             if contact_name:
#                 contact, created = Contact.objects.get_or_create(name=contact_name)
#                 if created:
#                     print "creating contact: %s" % contact_name
#                     contact.mobile = contact_mobile
#                     contact.email = contact_email
#                     contact.save()  # add new contact
#                     counter['contact'] += 1
#
#             store_name = row[1]
#             store_intro = row[5]
#             store_code = _to_str(row[3])
#             store_address = row[6]
#             store_postcode = _to_str(row[7])
#             store_city = row[11]
#             store_coupon = row[12]
#             # store = stores.get('store_code')
#             # if not store:
#             store = None
#             if store_code or store_name:
#                 try:
#                     store = Store.objects.get(Q(code=store_code) | Q(name=store_name))
#                 except Store.DoesNotExist:
#                     print "creating store [%s]%s" % (store_code, store_name)
#                     store = Store(code=store_code, name=store_name)
#                     store.intro = store_intro
#                     store.address = store_address
#                     store.post_code = store_postcode
#                     store.city = store_city
#                     store.coupon = store_coupon
#                     if contact:
#                         store.contact = contact
#                     store.save()  # add new store
#                     counter['store'] += 1
#                 except Exception, e:
#                     msg = "Failed to get store [%s]%s: %s" % (store_code, store_name, e.message or e.args[1])
#                     print msg
#                     result['error'].append(msg)
#
#             user = None
#             username = _to_str(row[2])
#             password = row[4]
#             if username:
#                 user, created = User.objects.get_or_create(username=username)
#                 if created:
#                     print "creating user: %s" % username
#                     user.is_staff = True
#                     user.set_password(password or store_code)  # use store_code as default password
#                     user.first_name = contact_name[1:]
#                     user.last_name = contact_name[0:1]
#                     user.email = contact_email
#                     user.save()  # add new user
#                     counter['user'] += 1
#
#             if user and store:
#                 sa, created = StoreAgent.objects.get_or_create(store=store, user=user)
#                 if created:
#                     counter['store_agent'] += 1
#                     print "binded user [%s] with store [%s]" % (username, store_name)
#         except Exception, e:
#             msg = "Load some data failed: %s" % (e.message or e.args[1])
#             result['error'].append(msg)
#     result['counter'] = counter
#     return result
#
#
# def import_agent_acount(request):
#     """
#     导入前台账号
#     :param request:
#     :return:
#         返回上传文件的绝对引用路径
#     """
#     if not request.user.is_superuser:
#         return render_to_response('admin/import.html', {"auth_error": "对不起，没有操作权限！"})
#
#     time_generator = timezone if settings.USE_TZ else datetime.datetime
#     start_time = time_generator.now()
#     files = request.FILES.getlist('files')
#     res = {"initiated_by": request.user.username}
#     file_path = ''
#     if not files or len(files) == 0:
#         return render_to_response('admin/import.html')
#     else:
#         path = timezone.now().strftime('%Y-%m-%d')
#         for f in files:
#             file_path = "%supload/data/%s_%s_%s" % (settings.STATIC_ROOT, path, random_str(32), f.name[-12:])
#             if not os.path.abspath(file_path).startswith(ABS_STATIC_ROOT):
#                 # TODO: invalid path given (out of ABS_STATIC_ROOT) or file not exists, must be log for security audit
#                 res["error"] = "无效的文件路径: %s" % file_path
#                 break
#             file_dir, file_name = os.path.split(file_path)
#             os.path.exists(file_dir) or os.makedirs(file_dir, mode=0744)
#
#             destination = open(file_path, 'wb+')
#             # print file_path
#
#             for chunk in f.chunks():
#                 destination.write(chunk)
#             destination.close()
#
#             try:
#                 res['save_as'] = file_path  # parse and save to DB
#                 res.update(load_agent(file_path))
#             except Exception, e:
#                 logger.exception(e)
#                 res["error"].append(e.message or e.args[1])
#
#             break  # process single file so far
#             # file_url = "%s%s" % (settings.STATIC_URL, file_path[len(settings.STATIC_ROOT):])
#             # result.append(file_url)
#
#     try:
#         from log.models import TaskLog
#         TaskLog.objects.create(
#             name=u'导入门店前台账号信息',
#             start_time=start_time,
#             end_time=time_generator.now(),
#             exec_result=jsonall.json_encode(res),
#             is_ok=not res.get('error'),
#             result_file=file_path
#         )
#     except Exception, e:
#         log.error('Save import agent accounts log error: %s' % e.message)
#
#     return render_to_response('admin/import.html', res)

