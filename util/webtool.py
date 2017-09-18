# -*- coding: utf-8 -*-
import urllib2
import datetime
import os
import re
import hashlib

import requests
from django.core.mail import send_mail

from util.renderutil import logger, random_str
from tms import settings
import urllib
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.files.base import ContentFile

__author__ = 'Winsom'


IMG_REG = re.compile(r'<img[^>]+src\s*=[\'\"]?([^\'\"]+)[\'\"]?', re.I)


def fetch_json(url, params=None, method='GET', headers=None):
    # res = fetch_url(url, params, method, headers)
    # json.loads(res)
    # return json.loads(res)
    if headers and headers.get("CONTENT_TYPE") == "application/json":
        if method == 'GET':
            resp = requests.get(url, json=params, headers=headers)
        else:
            resp = requests.post(url, json=params, headers=headers)
    else:
        if method == 'GET':
            resp = requests.get(url, params, headers=headers)
        else:
            resp = requests.post(url, params, headers=headers)
    resp.close()
    if resp.status_code == 200:
        res = resp.json()
    else:
        reason = 'open url failed: %s (reason: %s)' % (url, resp.reason)
        logger.error(reason)
        logger.error(resp.content)
        raise ValueError(reason)
    return res


def fetch_url(url, params=None, method='GET', headers=None):
    if headers and "application/json" in headers.get("CONTENT_TYPE"):
        if method == 'GET':
            resp = requests.get(url, json=params, headers=headers)
        else:
            resp = requests.post(url, json=params, headers=headers)
    else:
        if method == 'GET':
            resp = requests.get(url, params, headers=headers)
        else:
            resp = requests.post(url, params, headers=headers)

    resp.close()
    if resp.status_code == 200:
        res = resp.content
    else:
        reason = 'open url failed: %s (reason: %s)' % (url, resp.reason)
        logger.error(reason)
        raise ValueError(reason)
    return res

    # params = params or {}
    # headers = headers or {}
    # params_str = urllib.urlencode(params)
    # if 'GET' == method:
    #     if params_str:
    #         url = ('%s&%s' if '?' in url else '%s?%s') % (url, params_str)
    #     req = urllib2.Request(url, headers=headers)
    #
    # else:
    #     req = urllib2.Request(url, params_str, headers=headers)
    # start_time = datetime.datetime.now()
    # resp = urllib2.urlopen(req)
    # res = resp.read()
    # log.debug('fetch url cost(%ss): %s' % ((datetime.datetime.now()-start_time).total_seconds(), url))
    # return res


def download_image(img_url, base=None, timeout=10, override=False):
    """
    保存图片
    :img_url: 图片地址
    :base: 基准路径
    :timeout: 超时时间
    :return:
        (img_url, exists)
        img_url, 图片url
        exists, 是否已经存在
    """
    if not img_url or not img_url.strip():
        return None
    base = base or settings.APP_URL
    img_url = urllib.basejoin(base, img_url)

    exists = False
    try:
        # use str to enclose the url is to fix quote KeyError while the value is unicode
        logger.debug("downloading image: %s" % img_url)
        resp = urllib2.urlopen(img_url, timeout=timeout)
        path, ext = os.path.splitext(img_url)
        # img_path = "%s%s/" % (settings.MEDIA_ROOT, datetime.datetime.now().strftime('%Y/%m/%d'))
        img_path = "%s%s/" % (settings.STATIC_URL, datetime.datetime.now().strftime('%Y/%m/%d'))
        # os.path.exists(img_path) or os.makedirs(img_path, mode=0744)
        img_path = "%s%s%s" % (img_path, random_str(8), ext)
        # local_copy = open(img_path, 'wb')
        # local_copy.write(resp.read())
        img_path = img_path.replace('\\', '/')
        exists = staticfiles_storage.exists(img_path)
        if not exists or override:
            staticfiles_storage.open(img_path, 'wb')
            staticfiles_storage.save(img_path, ContentFile(resp.read()))
            logger.debug("download to: %s" % img_path)
        # return os.path.relpath(img_path, settings.MEDIA_ROOT).replace('\\', '/')
    except IOError, e:
        print 'Failed!'
        img_path = None
    return img_path, exists


def sendmail(subject, message, from_email, recipient_list,
             fail_silently=False, auth_user=None, auth_password=None,
             connection=None, html_message=None):
    # from log.models import UserMailLog
    # for receiver in recipient_list
    # if not settings.FAKE_EMAIL:
        send_mail(subject, message, from_email, recipient_list,
                  fail_silently, auth_user, auth_password,
                  connection, html_message)
    # else:
    #     print 'Fake sending mail to: %s' % ','.join(recipient_list)


def get_signature(sign_dict, alg='sha1'):
    """
    对参数进行签名，签名时先将参数按key值从小到大的排列顺序拼接成一个字符串（用&连接），
    然后排除值为空或空字符串的数据，用SHA1签名。
    :param sign_dict，用于签名的dict对象
    :return: string signature, 返回sha1签名结果，一个字符串

    eg.
    from util.webtool import get_signature
    >>> get_signature({'a': 123, 'c': 'xx@xx.com', 'b': None, 'xx': ''})
    'de5f6bea340a4c7e6491d5f8d4b43ab8de292804'
    >>> get_signature({'a': 123, 'c': 'xx@xx.com'})
    'de5f6bea340a4c7e6491d5f8d4b43ab8de292804'
    """
    if not isinstance(sign_dict, dict):
        raise ValueError('sign_dict is expected to be a dict object.')
    string = '&'.join(['%s=%s' % (key.lower(), sign_dict[key])
                       for key in sorted(sign_dict) if sign_dict[key] is not None and sign_dict[key] != ''])
    algorithm = hashlib.md5 if 'md5' == alg else hashlib.sha1
    sign_dict['signature'] = algorithm(string).hexdigest()
    return sign_dict['signature']


