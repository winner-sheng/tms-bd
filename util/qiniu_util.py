# -*- coding: utf-8 -*-
import urllib
import os

from qiniu import Auth, put_file, put_data
import requests

from tms.settings import MEDIA_URL, APP_URL, QINIU_ACCESS_KEY, QINIU_SECRET_KEY, QINIU_BUCKET_NAME, QINIU_URL
from util.webtool import IMG_REG
from util import renderutil
import datetime

import qiniu
__author__ = 'winsom'

# 构建鉴权对象
qn_auth = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)


def get_upload_to(instance=None):
    """
    自定义图片上传路径
    :param instance:
        model instance
    :return:
    """
    return "%s%s" % (MEDIA_URL, datetime.datetime.now().strftime('%Y/%m/%d'))


def put_file2qiniu(key, localfile, bucket=QINIU_BUCKET_NAME, qiniu_url=QINIU_URL):
    """
    上传图片文件到七牛云存储
    :param key: 上传到七牛后保存的文件名
    :param localfile: 本地文件路径
    :return:
    """
    # 生成上传 Token，可以指定过期时间等
    token = qn_auth.upload_token(bucket, key, 3600)
    ret, info = put_file(token, key, localfile)
    if info.status_code == 200:
        return urllib.basejoin(qiniu_url, key)
    else:
        raise ValueError(info.exception)


def put_data2qiniu(key, data, bucket=QINIU_BUCKET_NAME, qiniu_url=QINIU_URL):
    """
    上传图片文件到七牛云存储
    :param key: 上传到七牛后保存的文件名
    :return:
    """
    # 生成上传 Token，可以指定过期时间等
    token = qn_auth.upload_token(bucket, key, 3600)
    ret, info = put_data(token, key, data)
    if info.status_code == 200:
        return "%s/%s" % (qiniu_url, key)
    else:
        raise ValueError(info.exception)


def convert_intro2qiniu(intro, base_url=None):
    """
    处理商品详情，及其中涉及的图片
    :intro: 包含图片等html格式数据的商品详情
    :return:
    """
    imgs = {}
    base_url = base_url or APP_URL
    img_urls = IMG_REG.findall(intro)
    urlset = set()
    for img_url in img_urls:
        if img_url in imgs:
            continue
        url = urllib.basejoin(base_url, img_url)
        if QINIU_URL in url or url in urlset:
            continue
        try:
            name_ext = os.path.basename(url).split('.')
            ext = name_ext[1] if len(name_ext) == 2 else 'png'
            name = "%s.%s" % (renderutil.random_str(16), ext)
            path = "%s/%s" % (get_upload_to(), name)
            resp = requests.get(url)
            if resp.status_code == 200:
                target = put_data2qiniu(path, resp.content)
                imgs[img_url] = target
                urlset.add(url)
            else:
                print "Get image failed: %s" % url
        except ValueError, e:
            print e.message or e.args[1]

    res = intro
    for old_url, new_url in imgs.items():
        print 'convert %s to: ' % old_url
        print new_url
        res = res.replace(old_url, new_url)

    # print res
    return res, len(imgs)


def get_private_url(url, expires=3600):
    if not url:
        return url
    q = qiniu.Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
    return q.private_download_url(url, expires)
# if __name__ == 'main':
#     from basedata.models import Product
#     prd = Product.objects.get(code='P160316ZJ8AXS')
#     convert_intro2qiniu(prd.intro, 'http://test.tmonkey.cn:8001')

