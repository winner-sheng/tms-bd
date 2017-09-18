# -*- coding: utf-8 -*-
from django.db import models
from django.http import HttpResponse, HttpResponsePermanentRedirect
from util import jsonall
import json
from lxml.html.clean import Cleaner
from lxml import html
import random
import string
import time
from datetime import datetime, date
import datetime as dt
from django.utils import timezone
import csv
import logging
try:
    frozenset
except NameError:
    from sets import Set as frozenset

__author__ = 'Winsom'

# ERROR code definition
LOGIN_REQUIRED_ERR = 'E00001'   # 未登录
PASSWORD_MISMATCH_ERR = 'E00003'    # 密码不匹配
DUPLICATE_ACCOUNT_BINDING_ERR = 'E00004'    # 重复绑定账号
INVALID_ACCOUNT_ERR = 'E00005'  # 无效的账号
INVALID_PARAMETERS_ERR = 'E00400'   # 错误请求，无效参数
AUTH_REQUIRED_ERR = 'E00401'    # 未授权
ALLOW_TAGS = frozenset(['div', 'span', 'img', 'p', 'br', 'pre', 'table', 'tr', 'td', 'thead', 'tbody',
                        'strong', 'em', 'ul', 'ol', 'li', 'sub', 'sup', 'hr', 'audio', 'video', 'source', ])
SAFE_ATTRS = frozenset(['src', 'class', 'style', 'alt', 'title', 'colspan', 'rowspan',
                        'type', 'charset', 'lang', 'disabled', 'readonly', ])


logger = logging.getLogger('django.tms')
tracker = logging.getLogger('django.tracker')


def translate_special_char(s, chars='、，;；', delimiter=','):
    """
    将给定字符串中特殊字符删除，并把chars中指定的字符转为delimiter指定的特殊字符
    :param s:
    :param chars:
    :param delimiter:
    :return:
    """
    if not s:
        return s
    trans = string.maketrans(chars, delimiter * len(chars))
    delete_chars = '~!@#$%^&*()_+-=`[]\;\'./{}|:\"><?【】、。，￥'
    delete_chars = delete_chars.replace(delimiter, '')
    return str(s).translate(trans, delete_chars)


def now(use_tz=False, delta=None):
    """
    返回当前时间或与当前时间指定差值的时间
    :param use_tz:
    :param delta:
    :return:
    """
    d = timezone.now() if use_tz else datetime.now()
    return d + delta if delta else d


def one_date_later(use_tz=False):
    return now(use_tz) + dt.timedelta(days=1)


def get_dts(a_date=None):
    """
    用3个字符表示年月日，用于特定情形的编码
    :param a_date:
    :return:
    """
    a_date = a_date if isinstance(a_date, datetime) else now()
    s = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    return s[a_date.year % 100] + s[a_date.month] + s[a_date.day]


def day_str(a_date=None, use_tz=False, str_format="%y%m%d"):
    """
    输出指定格式的日期字符串
    :param a_date:
    :param use_tz:
    :param str_format:
    :return:
    """
    a_date = a_date or now(use_tz)
    return a_date.strftime(str_format)


def random_str(size=6):
    return ''.join(random.sample(string.ascii_letters+string.digits, size or 8))


def random_code(size=6):
    return ''.join(random.sample('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', size or 6))


def random_num(size=6):
    return ''.join(random.sample('0123456789', size or 6))


def random_letter(size=6):
    return "".join(random.sample('ABCDEFGHJKLMNPQRSTUVWXYZ', size or 6))


def render_request(request, force_post=False):
    """
    确保request可以处理content type为json的请求
    对于可以接受GET参数的请求，也支持使用POST方法提交数据（但每次提交数据时，仅限一种方式，不接受混合传参的方式）
    :param request:
    :param force_post:
    :return:
    """
    if "application/json" in request.META.get("CONTENT_TYPE"):
        return json.loads(request.body)
    else:
        return request.POST if request.method == 'POST' or force_post else request.GET


def render_post(request):
    """
    Used o fix the possible issue brought by Angular js' $http.post, which tends to send request data in json format.
    :param request:
    :return:
    """
    if "application/json" in request.META.get("CONTENT_TYPE"):
        return json.loads(request.body)
    else:
        return request.POST


def get_client(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META['REMOTE_ADDR']
    http_agent = request.META.get('HTTP_USER_AGENT', '')[:100]
    return {"ip": ip, "http_agent": http_agent}


def get_current_url(request):
    return "%s://%s%s" % (request.scheme, request.get_host(), request.path) if request else ''


def allow_cross_domain(response):
    response['Access-Control-Allow-Origin'] = '*'  # http://localhost:63343
    response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'uidtoken, Access-Control-Allow-Origin, Authorization, Origin, ' \
                                               'x-requested-with, Content-Type,x-csrf-token'  #,Origin, Access-Control-Allow-Origin, Accept, X-Requested-With,  X-Access-Token
    response['Access-Control-Allow-Credentials'] = 'true'
    response['Access-Control-Max-Age'] = 3600*24*7  # keep 7 days


def feed_options():
    response = HttpResponse('Respond to OPTIONS')
    allow_cross_domain(response)
    return response


#@csrf_protect
def report_error(message, code='0', cross_domain=True, data=None):
    """
    输出json格式的错误信息
    :param
        message: 错误消息
        code: 错误编码
        data: 追加数据
    :return:
    """
    logger.error(message)
    if isinstance(message, list):
        message = ';\n'.join(message)
    elif isinstance(message, dict):
        message = ';\n'.join(["%s: %s" % (k, v) for k,v in message.items()])
    res = {'error': message, 'err_code': code, 'result': ''}
    if data:
        logger.error(data)
        res.update(data)
    response = HttpResponse(jsonall.json_encode(res),
                            content_type="application/json;charset=utf-8",)
    cross_domain and allow_cross_domain(response)
    return response


def report_ok(data=None):
    """
    输出json格式的错误信息
    :param
        data: 追加数据
    :return:
    """
    res = {'result': 'ok', 'error': ''}
    if data:
        res.update(data)
    response = HttpResponse(jsonall.json_encode(res),
                            content_type="application/json;charset=utf-8",)
    return response


REQUIRE_LOGIN = HttpResponse(jsonall.json_encode({'error': u"用户身份未验证或验证已失效，请重新登录！",
                                                  'err_code': LOGIN_REQUIRED_ERR,
                                                  'result': ''}),
                             content_type="application/json;charset=utf-8")
REQUIRE_AUTH = HttpResponse(jsonall.json_encode({'error': u"对不起，访问未授权，请与系统管理员联系。",
                                                 'err_code': AUTH_REQUIRED_ERR,
                                                 'result': ''}),
                            content_type="application/json;charset=utf-8")


#@csrf_protect
def json_response(output_objects, cross_domain=True):
    """
    以json格式输出，使用utf-8编码
    :param output_objects:  任意类型对象
    :return:
    """
    response = HttpResponse(jsonall.json_encode(output_objects),
                            content_type="application/json;charset=utf-8",)
    cross_domain and allow_cross_domain(response)
    return response


def js_response(output, cross_domain=True):
    """
    以js格式输出，使用utf-8编码
    :param output:  要输出的字符串
    :return:
    """
    response = HttpResponse(output,
                            content_type="text/javascript;charset=utf-8", )
    cross_domain and allow_cross_domain(response)
    return response


def css_response(output_objects, cross_domain=True, cache=False):
    """
    以json格式输出，使用utf-8编码
    :param output_objects:  任意类型对象
    :return:
    """
    txt = output_objects
    if not isinstance(output_objects, basestring):
        txt = "/*%s*/" % jsonall.json_encode(output_objects)
    response = HttpResponse(txt, content_type="text/css")
    if not cache:
        response["Expires"] = 0
        response["Cache-Control"] = "no-cache"
        response["Pragma"] = "No-cache"
        response["Cache-Control"] = "no-store"

    cross_domain and allow_cross_domain(response)
    return response


def redirect(url):
    return HttpResponsePermanentRedirect(url)


def purify_html(html_str, base_url=None, allow_tags=ALLOW_TAGS, safe_attrs=SAFE_ATTRS):
    """
    HTML代码清理
    :param html_str: 要清理的HTML字符串
    :param base_url: HTML字符串所属的基本URL，用于HTML中涉及的图片等资源的路径转换
    :param allow_tags: 指定保留的HTML TAG
    :param safe_attrs: 指定要保留的属性
    :return:
    """
    cleaner = Cleaner()
    cleaner.allow_tags = allow_tags
    cleaner.safe_attrs = safe_attrs
    cleaner.safe_attrs_only = (len(safe_attrs) > 0)
    cleaner.remove_unknown_tags = False
    html_res = cleaner.clean_html(html_str) if html_str else ''
    return html_res


def to_absolute_links(html_str, base_url):
    html_str = unicode(html_str)
    root = html.fromstring(html_str, base_url)
    root.make_links_absolute(base_url)
    return html.tostring(root, pretty_print=True, encoding='utf8')


def midnight():
    now = time.time()
    start = now - (now % 86400)
    return datetime.fromtimestamp(start)


def export_csv(file_name, data):
    response = HttpResponse(content_type='text/csv;charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="%s"' % file_name
    writer = csv.writer(response, dialect='excel')
    # writer = csv.writer(response)
    import codecs
    response.write(codecs.BOM_UTF8)
    for rows in data:
        writer.writerow([cell for cell in rows])

    return response


def export_excel(file_name, data):
    import xlwt
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=%s' % file_name
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet(u'data')
    row_no = 0
    for row in data:
        col_no = 0
        for col in row:
            sheet.write(row_no, col_no, col)
            col_no += 1

        row_no += 1

    wb.save(response)
    return response


def export(file_name, data, file_type='excel'):
    return export_excel(file_name, data) if file_type == 'excel' else export_csv(file_name, data)


def render_date(data):
    ret = data
    if not data:
        return ret
    elif isinstance(data, datetime):
        t = data if timezone.is_naive(data) else timezone.localtime(data)
        ret = t.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(data, date):
        t = data if timezone.is_naive(data) else timezone.localtime(data)
        ret = t.strftime('%Y-%m-%d')

    return ret


def get_value_by_path(data, key, default=None):
    if not isinstance(data, dict):
        raise ValueError(u'data参数必须是dict类型')

    if key in data:
        return data.get(key, default)
    elif '.' in key:
        keys = key.split('.', 1)
        v = data.get(keys[0])
        if v and isinstance(v, dict):
            return get_value_by_path(v, keys[1], default)
        else:
            return default
    else:
        return default


def get_fields_list(model, with_verbose=False):
    """
    获取指定Model的field列表，如['code', 'name']，
    如果指定with_verbose，连字段的显示名称一并返回，如[('code', '编码'), ('name', '名称')]
    :param model:
    :param with_verbose:
    :return:
    """
    result = []
    if isinstance(model, models.base.ModelBase):
        for f in model._meta.fields:
            if with_verbose:
                result.append((f.name, f.verbose_name))
            else:
                result.append(f.name)

    return result


def print_model_fields(model):
    from django.db.models import base
    if isinstance(model, base.ModelBase):
        field_names = model._meta.get_all_field_names()
        print field_names
        print '[',
        for fn in field_names:
            print 'u"%s",' % model._meta.get_field(fn).verbose_name,
        print ']'

        print '{',
        for f in model._meta.fields:
            print '"%s":' % f.name, 'u"%s",' % f.verbose_name,
        print '}'
    else:
        print model