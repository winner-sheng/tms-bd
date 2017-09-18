# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.decorators.cache import cache_page
from django.shortcuts import render_to_response
from django.db.models import Q

from article.models import Article, ArticleCategory
from util.renderutil import now, json_response, report_error, report_ok, get_current_url
from tms import settings, config
from filemgmt.models import BaseImage
import time
import hashlib
from django.core.urlresolvers import reverse


@cache_page(30, key_prefix="tms.api")
def get_article_categories(request):
    """
    获取文章分类列表
    :param request (GET):
        - [id], 可选，类别id，如果不提供此参数，返回所有，否则返回指定类别及其子类别清单
        - [with_children], 是否包含该类别的所有子类对应的文章类别，默认为是，0为不包含，其它为包含
    :return:
        [
            {
                name : "景区介绍",
                list_order : 0,
                memo : null,
                parent_id : 6,
                path : "6,1",
                id : 1
            },
            {
                name : "景点特产",
                list_order : 0,
                memo : null,
                parent_id : 1,
                path : "6,1,4",
                id : 4
            },
            {
                name : "文化典故",
                list_order : 0,
                memo : null,
                parent_id : 1,
                path : "6,1,5",
                id : 5
            },
        ]
        eg. <a href="/tms-api/get_article_categories">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    category_id = req.get('id')
    records = ArticleCategory.objects.all()
    if category_id:
        try:
            category = ArticleCategory.objects.get(id=category_id)
            records = [category]
            if '0' != req.get('with_children'):
                records[1:] = list(category.get_children())
        except ArticleCategory.DoesNotExist:
            return report_error('找不到该类别（id: %s）' % category_id)

    return json_response(records)


@cache_page(30, key_prefix="tms.api")
def get_article(request):
    """
    获取文章列表，或指定id的文章详情 (按list_order及发布时间倒序排列)
    :param request (GET):
        - [id], 可选，文章的id（如果提供id参数，则忽视后面其它参数，并且返回文章的详细信息，如果找不到，返回[]）
        - [category | category_id, [with_children]], 可选，
            * category, 分类名称，如果类目中存在同名的，只返回匹配的第一个分类关联的文章
            * category_id, 分类id
            * with_children, 是否包含该类别的所有子类对应的文章，默认为否，1为包含，其它为不包含
        - [tags]，可选，获取包含指定tag的文章列表，如果多个tag，可用","（需同时包含所有tag）或"|"（只需包含其中一个tag）分隔
        - [pos], 可选，获取的结果可能存在多页时，给定开始选取的位置，默认为0
        - [size], 可选，获取的结果可能存在多页时，确定返回每页记录数，默认为4
        - [detail], 可选，只要带上该参数，则返回"文章"的详细信息（主要是content属性），无需有值。
        - [create_by, [uid]], 可选，根据作者来查询
            * create_by, 作者id，后台管理用户添加的文章，值为管理用户的账号名称，前端普通用户添加的文章，值为用户uid
            * uid，当前访问用户的uid，当uid跟create_by相同时，返回的文章可包含草稿，否则不返回草稿
    :return:
        - 返回数组：
        如果参数不包含detail，则返回简单格式的结果：
        [
            {
                brief: "摘要，简述",
                category_id: 2,     (文章分类id)
                category_txt: "特色美食",   （文章分类名称）
                create_by: "test_12345678",     (创建人，对于后台管理用户值为管理用户的账号名称，对于前端普通用户值为用户uid),
                id: 2,
                is_active: True,    (是否有效)
                list_order: 0,
                product_tags: "名称:TEST",   (见补充说明)
                publish_date: "2015-07-13 07:52:00" （发布日期）,
                subject_image: "http://xxx.qiniucdn.com/static/2016/08/17/ooopic_1426320399.png",
                subject: "测试文章2"
                tags: "test,test3",
                update_time: "2016-10-21 15:27:52",
            }
        ]
        如果参数包含detail，则返回文章详情
        [
            {
                brief: "摘要，简述",
                category_id: 2,     (文章分类id)
                category_txt: "特色美食",   （文章分类名称）
                content: "&lt;p&gt;深沉内敛的父亲也希望得到你的祝福呢&lt;/p&gt;..." (“文章”详情说明，可以是HTML),
                content_image: "" （“文章”详情的主题Banner图片，用于“文章”详情页，默认为空，即与subject_image相同）
                create_by: "test_12345678",     (创建人，对于后台管理用户值为管理用户的账号名称，对于前端普通用户值为用户uid),
                id: 3,
                is_active: True,    (是否有效，无效文章不会返回)
                link_to: "http://test.twohou.com/", （链接目标地址，留空默认是文章详情页，也可能额外指定）,
                product_tags: "名称:TEST",   (见补充说明)
                publish_date: "2015-07-13 07:52:00" （发布日期）,
                subject: "父爱如山，给父亲最好的礼物" （主题）,
                subject_image: "http://xxx.qiniucdn.com/static/images/2015/07/13/father2015.jpg" （“文章”的主题Banner图片，用于“文章”列表）,
                tags: "父亲节,礼物",
                update_time: "2016-10-21 15:27:52",
            }
        ]

        关于product_tags，补充说明：
            用于文章与商品匹配搜索，格式为"<关联属性>:<关联值>"，可以有多个，中间使用英文逗号","分隔。
            关联属性可以是名称、类别、Tag、品牌、产地、供应商中的一种或几种。
            如："名称:月饼,类别:食品,Tag:送礼,品牌:利男居,产地:上海,供应商:TWOHOU-02"

    eg. <a href="/tms-api/get_article">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    # article_id = int(req.get('id', '0'))
    article_id = 0
    aid = req.get('id') or '0'
    article_id = int(aid)
    if article_id > 0:
        detail = True
        articles = Article.objects.filter(id=article_id)
    else:
        # 只有已发布并且有效的文章可以被查询
        articles = Article.objects.order_by('-list_order', '-publish_date')
        category_txt = req.get('category') or req.get('category_txt')
        category_id = req.get('category_id')
        if category_txt or category_id:
            q = Q(id=category_id) if category_id else Q(name=category_txt)
            category = ArticleCategory.objects.filter(q)[:1]
            if len(category) == 0:
                return report_error('无效的类别（%s）' % (("id: %s" % category_id) if category_id else category_txt))
            else:
                category = category[0]
            if '1' == req.get('with_children'):
                category_ids = list(category.get_children().values_list('id', flat=True))
                category_ids.append(category.id)
                articles = articles.filter(category_id__in=category_ids)
            else:
                articles = articles.filter(category_id=category.id)
        tags = req.get('tags')
        if tags:
            use_or = '|' in tags
            tags_list = tags.split('|') if use_or else tags.split(',')
            tags_filter = Q(tags__inset=tags_list[0])
            for tag in tags_list[1:]:
                if use_or:
                    tags_filter |= Q(tags__inset=tag)
                else:
                    tags_filter &= Q(tags__inset=tag)
            articles = articles.filter(tags_filter)

    if req.get('create_by') and req.get('create_by') == req.get('uid'):  # 查看作者自己的文章
        articles = articles.filter(create_by=req.get('create_by'))
    else:
        if 'create_by' in req:  # 按作者查询文章
            articles = articles.filter(create_by=req.get('create_by'))

        cur_time = now(settings.USE_TZ)
        articles = articles.filter(is_active=True, publish_date__lt=cur_time)  # 只返回已发布及有效的文章

    if not article_id > 0:
        start_pos = int(req.get('pos', 0))
        page_size = int(req.get('size', 4))
        # page_size = page_size if 2 < page_size < 20 else 20 if page_size >= 20 else 2
        if req.get('page'):
            start_pos = int(req.get('page')) * page_size
        detail = 'detail' in req
        articles = articles[start_pos:start_pos+page_size]

    results = [a.to_dict(detail) for a in articles]
    return json_response(results)


def preview_article(request, article_id):
    """
    商品信息预览
    :param request (GET):
    :param article_id:
    :return:
    """
    if not article_id:
        return render_to_response('admin/article/article/preview.html', {'error': '缺少文章id！'})

    try:
        article = Article.objects.get(id=article_id)
        return render_to_response('admin/article/article/preview.html', {'article': article.to_dict(detail=True)})
    except Article.DoesNotExist:
        return render_to_response('admin/article/article/preview.html', {'error': '文章不存在（id:%s）！' % article_id})


def get_preview_url(data_type, obj_id, timeout=3600):
    preview_url = settings.APP_URL + reverse('article.views.preview',
                                             kwargs={'data_type': data_type,
                                                     'obj_id': obj_id,
                                                     'timeout': timeout+int(time.time()),
                                                     'token': ''})
    token = hashlib.md5(preview_url+config.PREVIEW_KEY).hexdigest()
    return preview_url + token


def preview(request, data_type, obj_id, timeout, token):
    current_url = get_current_url(request)
    token_pos = current_url.rindex('/')
    # token = current_url[token_pos+1:]
    # timeout_pos = current_url[:37].rindex('/')
    # timeout = current_url[timeout_pos+1:token_pos]
    if int(timeout) < time.time():
        return report_error('当前链接已失效，请重新获取！')

    if hashlib.md5(current_url[:token_pos+1] + config.PREVIEW_KEY).hexdigest() != token:
        return report_error('无效的链接，请重新获取！')

    if data_type == 'article':
        # from article.views import preview_article
        return preview_article(request, obj_id)
    elif data_type == 'product':
        from basedata.views import preview_product
        return preview_product(request, obj_id)
    elif data_type == 'hotel':
        from vendor.views import preview_hotel
        return preview_hotel(request, obj_id)
    else:
        return report_error('无效的链接！')


def update_article(request):
    """
    创建/更新文章
    :param request (POST):
        - uid, 用户uid
        - [id], 文章id，用于更新，如果没有提供该参数，则创建一篇新的文章，如果提供了，但找不到对应的，则返回错误
        - [subject], 文章标题，如果是添加新的文章，标题必须提供
        - [category_id], 文章类别id（来自get_article_categories）
        - [brief], 简介
        - [tags], 文章标签
        - [subject_image], 标题图片url
        - [content], 文章正文，html格式（不安全的标签及属性会被过滤）或纯文本格式
        - [publish], 是否立即发布，为0时表示暂不发布（作为草稿），默认为立即发布即设置publish_date为当前时间

    :return:
        成功返回{"id": 1, "result": "ok"} id为文章的id
        失败返回{"error": msg}

    eg. <a href="/tms-api/update_article">查看样例</a>
    """
    from profile.views import get_user_by_uid
    user = get_user_by_uid(request)
    if not user:
        return report_error('无效的用户账号！')

    req = request.POST
    if 'id' in req:
        try:
            article = Article.objects.get(id=req.get('id'))
            if article.create_by != user.uid:
                return report_error('没有操作权限')
            if 'subject' in req and not req.get('subject'):
                return report_error('文章标题不能为空')

            article.update_by = user.uid  # 仅当非文档创建人可修改时有意义
        except Article.DoesNotExist:
            return report_error('文章不存在（id:%s）' % req.get('id'))
    else:
        article = Article()
        if not req.get('subject'):
            return report_error('必须提供文章标题')
        article.create_by = article.update_by = user.uid

    if 'category_id' in req:
        try:
            category = ArticleCategory.objects.get(id=req.get('category_id'))
            article.category_id = category.pk
        except ArticleCategory.DoesNotExist:
            return report_error('无效的文章分类（id:%s）' % req.get('category_id'))

    if 'subject_image' in req:
        if req.get('subject_image'):
            sub_image, created = BaseImage.objects.get_or_create(origin=req.get('subject_image'))
            article.subject_image_id = sub_image.id
        else:
            # remove image from article
            article.subject_image = None

    for attr in ['subject', 'category_id', 'brief', 'tags', 'content']:
        setattr(article, attr, req.get(attr))

    if '0' == req.get('publish'):
        article.publish_date = None
        article.is_active = False
    else:
        article.is_active = True
        article.publish_date = now(settings.USE_TZ)

    article.save()
    return report_ok(data={'id': article.id})
