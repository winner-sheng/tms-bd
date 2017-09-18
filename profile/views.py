# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from decimal import Decimal
import datetime

from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.core.cache import cache
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response
from django.utils import timezone
from django.contrib.auth import hashers
from profile.models import ShipAddress, EndUser, EndUserExt, EndUserEnterprise, UserOrgSnapShot, EndUserLink, EndUserRole, \
    UserFavorite, UserAccountBook, UserHistory, UserCapitalAccount, WithdrawRequest
from tms import settings
from util import renderutil, geoutil
from util.renderutil import report_error, report_ok, json_response, now, random_str, \
    INVALID_ACCOUNT_ERR, REQUIRE_LOGIN, PASSWORD_MISMATCH_ERR, DUPLICATE_ACCOUNT_BINDING_ERR, INVALID_PARAMETERS_ERR, logger
from datetime import timedelta
from config.models import AppSetting
from django.contrib.admin.models import LogEntry
from tms.config import REWARD_DEFERRED_DAYS
from django.db.models import Q
from buding.models import *


ABS_STATIC_ROOT = os.path.abspath(settings.STATIC_ROOT)
ACCOUNT_TYPES_REVERT_DICT = dict([(item, key) for key, item in UserAccountBook.ACCOUNT_TYPES])


def get_user_by_uid(request, as_internal=False, attr='uid', with_org=False):
    """
    根据uid获取用户对象，仅供内部调用
    :param request (POST/GET):
        - uid， 用户uid
    :return:
        成功返回EndUser对象，否则返回None
    """
    try:
        REQ = renderutil.render_request(request)
        attr_value = REQ.get(attr)
        end_user = EndUser.objects.get(uid=attr_value,
                                       status=EndUser.STATUS_ACTIVE)
    except EndUser.DoesNotExist:
        end_user = None
    else:
        if as_internal:
            try:
                end_user_ex = EndUserExt.objects.get(uid=attr_value, ex_id_type=EndUserExt.ID_TYPE_INTERNAL)
            except EndUserExt.DoesNotExist:
                end_user.internal_user = None
            else:
                try:
                    user = User.objects.get(username=end_user_ex.ex_id)
                    end_user.internal_user = user
                except User.DoesNotExist:
                    logger.error('管理账号[%s]不存在' % end_user_ex.ex_id)

        if with_org and end_user.org_uid:
            try:
                org = EndUserEnterprise.objects.get(uid=end_user.org_uid)
                end_user.org = org
            except EndUserEnterprise.DoesNotExist:
                end_user.org = None

    return end_user


def get_user(request):
    """
    获取用户信息，如果用户不存在，则创建一个新用户
    :param request (POST):
        - uid | ex_id, ex_id_type | mobile
            uid，用户id（uuid），可直接识别一个唯一用户 （仅用于查询，如果不存在，返回错误提示）
            ex_id，第三方id，字符串，如微信的openid，unionid等 （可用于注册或查询，如果查询不存在则自动注册新账号）
            ex_id_type，第三方id类型，整数，定义如下：
                0, 微信openID(默认值)
                1， 微信unionID
                2， QQ开放账号ID
                3， 支付宝开放账号ID
                4， 微博开放账号ID
                5， 普通浏览器uuid（匿名用户）
                99, 内部管理账号
            mobile, 手机号，可直接识别一个唯一用户（可用于注册或查询，如果查询不存在则自动用此信息注册新账号）

        以下参数，仅当用户不存在或首次登录时有效，作为补充注册信息之用
        - [ex_nick_name], 可选，第三方昵称，字符串，用于更新
        - [ex_avatar], 可选，第三方头像，字符串，用于更新
        - [gender], 可选，性别（X-不告诉你，M-男，F-女）
        - [ip], 可选，用于记录新用户的注册ip
        - [entry_uid], 可选，入口用户uid，即用户首次扫码进入，成为新用户时入口用户的uid
        - [referrer], 可选，推荐人uid，即用户被推荐成为导游时推荐人的uid

        以下参数，仅当用户已经存在时有效
        - [with_internal]，可选，可以没有值，返回包含内部管理账号相关信息
        - [with_org]，可选，可以没有值
            如果提供该参数，则返回的org属性为关联的组织详情（Json对象，如旅行社），否则返回的org为组织账号的uid
        - [with_credit], 可选，可以没有值, 返回用户积分信息
            返回结果中包含
            { "credits": <见get_credit_summary>}
        - [with_medal], 可选，可以没有值, 返回用户持有的勋章信息
            返回结果中包含
            { "medals": <见get_medals>}
    :return:
        验证成功，返回用户对象，如果是新用户，则返回的对象中包含属性is_new。如：
        {
            avatar: "avatar.png",   （头像）
            entry_uid: "test_12345678", （用户首次登录时入口用户的uid）
            ex_avatar: "ex_avatar",  （第三方头像）
            ex_nick_name: "ex_nick_name",   （第三方昵称）
            gender: "X",    （性别，X-不告诉你，M-男，F-女）
            intro: "test intro",    （简介）
            is_org_staff: true,     (是否企业的管理者或职员，对企业信息具有全部或部分管理权限)
            last_login: null,
            mobile: "13800000000",
            nick_name: "nick_name",  (昵称)
            org_uid: "62f8c368b0cd44aca5720356e803a3df",    （所属组织的uid）
            real_name: "xxx",   （真实姓名）
            referrer: "62f8c368bsdfgeaca5720356e803a3df",  （当用户成为导游时的推荐人uid）
            status: 0,  （状态，0-有效，1-无效，99-黑名单）
            uid: "9e409d57e88c46a39d22a69b6540645b",
            user_type: "P",     （用户类型，P为普通用户，E为普通企业，G为集团企业）
            org: {  (仅当提供with_org参数时返回)
                avatar: "test_logo.png",
                contact_email: null,
                contact_mobile: null,
                contact_name: "contact_name",
                contact_phone: null
                enduser_ptr: "62f8c368b0cd44aca5720356e803a3df",
                intro: "test intro",
                last_login: null,
                license_image: "test_license_image.png",
                org_uid: null,
                real_name: "xxxx",
                referrer: null,
                review_note: null,
                review_status: "pending",
                status: 0,
                uid: "62f8c368b0cd44aca5720356e803a3df",
                user_type: "E",
            },
            "internal_user": {      （如果参数包含with_internal，则返回内部管理账号信息）
                "username": "kangchen",
                "suppliers": [      （该用户账号所管理的供应商信息）
                    {
                        "province": "海南",
                        "city": "三亚市",
                        "code": "kangchenshuiguo",
                        "name": "康晨水果",
                        "address": "",
                        "primary_contact": "xxx",
                        "id": 9
                    }
                ],
                "is_active": true,
                "is_superuser": false,
                "fullname": "xxxx",
                "email": "123456@qq.com"
            },
        }
    失败返回错误提示{"error": msg}

    eg. <a href="/tms-api/get_user">查看样例</a>
    """
    is_new = False
    has_change = False
    ex_id_type = EndUserExt.ID_TYPE_WECHAT_OPENID
    if request.POST.get('uid'):
        try:
            end_user = EndUser.objects.get(uid=request.POST.get('uid'))
            if end_user.status != EndUser.STATUS_ACTIVE:
                return report_error('无效的用户！', code=INVALID_ACCOUNT_ERR)
        except EndUser.DoesNotExist:
            return report_error('用户不存在！', code=INVALID_ACCOUNT_ERR)
            # end_user = EndUser.objects.create(uid=request.POST.get('uid'))
        except ValueError:
            return report_error('无效的uid参数')

    elif request.POST.get('mobile'):
        try:
            end_user = EndUser.objects.get(mobile=request.POST.get('mobile'))
            if end_user.status != EndUser.STATUS_ACTIVE:
                return report_error('无效的用户！', code=INVALID_ACCOUNT_ERR)
        except EndUser.DoesNotExist:
            end_user = EndUser(mobile=request.POST.get('mobile'))
            is_new = True

    elif request.POST.get('ex_id'):
        ex_id_type = int(request.POST.get('ex_id_type') or ex_id_type)
        if ex_id_type not in [k for k, v in EndUserExt.ID_TYPES]:
            return report_error('无效的账号类型！')

        try:
            end_user_ext = EndUserExt.objects.get(ex_id=request.POST.get('ex_id'), ex_id_type=ex_id_type)
            end_user = EndUser.objects.get(uid=end_user_ext.uid)
        except EndUserExt.DoesNotExist:
            if ex_id_type == EndUserExt.ID_TYPE_INTERNAL:
                return report_error('账号[%s]未绑定！' % request.POST.get('ex_id'))

            end_user = EndUser()
            is_new = True
    else:
        return report_error('缺少参数！')

    # r = end_user.referrer
    # e = end_user.entry_uid
    # g = end_user.gender

    attributes = {'ex_nick_name': 'ex_nick_name', 'ex_avatar': 'ex_avatar',
                  'ip': 'register_ip', 'gender': 'gender', 'entry_uid': 'entry_uid',
                  'referrer': 'referrer'}
    # TODO: should verify entry_uid and referrer validity
    for k, attr in attributes.items():
        if not is_new and k in['gender', 'entry_uid', 'referrer']:
            continue  # 如果不是新用户，这几项属性不允许再修改
        if k in request.POST and request.POST.get(k) != getattr(end_user, attr):
            has_change = True
            setattr(end_user, attr, request.POST.get(k))

    # setattr(end_user, 'referrer', r)
    # setattr(end_user, 'entry_uid', e)
    # setattr(end_user, 'gender', g)

    (is_new or has_change) and end_user.save()
    if request.POST.get('ex_id') and is_new:
        EndUserExt(uid=end_user.uid, ex_id=request.POST.get('ex_id'), ex_id_type=ex_id_type).save()

    end_user = model_to_dict(end_user, exclude=['password', 'id_card'])

    if is_new:
        end_user['is_new'] = True
    else:
        if 'with_internal' in request.POST:
            try:
                end_user_ex = EndUserExt.objects.get(uid=end_user['uid'], ex_id_type=EndUserExt.ID_TYPE_INTERNAL)
                user = User.objects.get(username=end_user_ex.ex_id)
                internal_user = {'username': user.username,
                                 'is_active': user.is_active,
                                 'is_superuser': user.is_superuser,
                                 'email': user.email,
                                 'fullname': user.get_full_name(),
                                 'suppliers': []}
                supplier_mgrs = user.suppliermanager_set.all()
                for sup in supplier_mgrs:
                    internal_user['suppliers'].append(sup.supplier.to_dict())

                end_user['internal_user'] = internal_user
            except (EndUserExt.DoesNotExist, User.DoesNotExist):
                pass
            except Exception, e:
                logger.exception(e)

        if 'with_org' in request.POST and end_user.get('org'):
            try:
                org = EndUserEnterprise.objects.get(uid=end_user['uid'])
                end_user['org_obj'] = org.to_dict()
            except EndUserEnterprise.DoesNotExist:
                pass
            except Exception, e:
                logger.exception(e)

        if 'with_credit' in request.POST:
            from credit.views import fetch_credit_summary
            end_user['credits'] = fetch_credit_summary(end_user['uid'])

        if 'with_medal' in request.POST:
            from credit.views import get_user_medals
            end_user['medals'] = get_user_medals(end_user['uid'])

    return renderutil.json_response(end_user)


# def _save_change(obj_name, obj_id, attr, old_value, new_value):
#     LogEntry

def register_user(request):
    """
    注册新用户
    :param request (POST):
        - mobile|ex_id, ex_id_type
            mobile，用户手机，必须唯一（必须通过短信验证码验证有效）
            ex_id，第三方id，字符串，如微信的openid，unionid等
            ex_id_type，第三方id类型，整数，定义如下：
                0, 微信openID(默认值)
                1， 微信unionID
                2， QQ开放账号ID
                3， 支付宝开放账号ID
                4， 微博开放账号ID
                99, 内部管理账号
        - [ex_nick_name], 可选，第三方昵称，字符串，用于更新
        - [ex_avatar], 可选，第三方头像，字符串，用于更新
        - [nick_name], 可选，昵称
        - [avatar], 可选，头像
        - [real_name], 可选，真实姓名
        - [gender], 可选，性别，单字母，M-男，F-女，X-不告诉你
        - [id_card], 可选，身份证号，待实现
        - [intro], 可选，简介
        - [entry_uid], 可选，入口用户uid，即用户首次扫码进入，成为新用户时入口用户的uid
        - [referrer], 可选，推荐人uid，即用户被推荐成为导游时推荐人的uid
        - [org_uid], 可选，归属组织uid
        - [register_ip], 可选，用于记录新用户的注册ip
    :return:
        创建成功，返回用户uid
        {
            "uid" : "7533c0d05140a47d29154d625b94cbdd",
        }
        失败返回错误提示{"error": "msg"}

    eg. <a href="/tms-api/register_user">查看样例</a>
    """
    end_user = EndUser()
    if request.POST.get('mobile'):
        if EndUser.objects.filter(mobile=request.POST.get('mobile')).exists():
            return report_error('手机号[%s]已注册' % request.POST.get('mobile'))
        else:
            end_user.mobile = request.POST.get('mobile')

    ex_id_type = int(request.POST.get('ex_id_type', EndUserExt.ID_TYPE_WECHAT_OPENID))
    if request.POST.get('ex_id'):
        if ex_id_type not in dict(EndUserExt.ID_TYPES).keys():
            return report_error('无效的账号类型！')

        if EndUserExt.objects.filter(ex_id=request.POST.get('ex_id'), ex_id_type=ex_id_type).exists():
            return report_error('该第三方账号已绑定用户，不可重复注册新用户')

    attributes = ['ex_nick_name', 'ex_avatar', 'nick_name', 'avatar', 'real_name', 'gender', 'mobile', 'id_card',
                  'entry_uid', 'referrer', 'register_ip', 'intro']
    for attr in attributes:
        if request.POST.get(attr):
            setattr(end_user, attr, request.POST.get(attr))
    end_user.last_login = now(settings.USE_TZ)
    org = None
    if request.POST.get('org_uid'):
        try:
            org = EndUserEnterprise.objects.get(uid=request.POST.get('org_uid'),
                                                user_type=EndUserEnterprise.USER_ENTERPRISE,
                                                status=EndUserEnterprise.STATUS_ACTIVE)
        except EndUserEnterprise.DoesNotExist:
            return report_error('无效的归属企业')
        else:
            end_user.org_uid = org.uid

    end_user.save()
    if org:
        # 保存关系快照
        UserOrgSnapShot.objects.create(uid=end_user.uid, org_uid=end_user.org_uid, overhead_rate=org.overhead_rate)

    if request.POST.get('ex_id'):
        EndUserExt(uid=end_user.uid, ex_id_type=ex_id_type, ex_id=request.POST.get('ex_id')).save()

    return json_response({'uid': end_user.uid})


def register_org(request):
    """
    注册组织信息（可以是企业或集团企业）
    :param request (POST):
        - uid, 用户uid，默认会变成新注册企业的管理员
        - name, 企业名称
        - [ent_type]，企业类型，默认为0-旅行社，可选：
            * 0, 旅行社
            * 1, 酒店
            * 2, 民宿
            * 3, 景区
            * 999, 其它
        - id_card_image, 责任人身份证照（私密图片）
        - license_image, 执照/资质证照（私密图片）
        - [user_type]，可选，G表示集团企业，E表示为非集团企业（默认）
        - [avatar]，可选，企业LOGO的URL地址
        - [address, intro, contact_name, contact_mobile, contact_phone, contact_email, register_ip],
            可选，要注册的企业地址，简介，联系人，联系人手机，联系人电话，联系人email地址及注册ip
    :return:
        成功返回{uid: "uid"} 失败返回{error: 'msg'}
        注意：当创建的不是集团企业时，如果用户无归属企业，则自动设置其归属企业为新注册的企业。否则忽略。

    eg. <a href="/tms-api/register_org">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return report_error('无效的用户账号！')

    # if user.is_org_staff:
    #     return report_error('同一用户只能从属于一家企业')

    if not request.POST.get('name'):
        return report_error('请提供企业名称')
    if not request.POST.get('id_card_image'):
        return report_error('请提供责任人身份证照')
    if not request.POST.get('license_image'):
        return report_error('请提供企业执照或旅游经营许可证照片')
    ent_type = request.POST.get('ent_type', '0')
    if int(ent_type) not in [x for x, name in EndUserEnterprise.ENTERPRISE_TYPES]:
        return report_error('无效的企业类型')

    if EndUserEnterprise.objects.filter(real_name=request.POST.get('name')).exists():
        return report_error('企业名称[%s]已被注册' % request.POST.get('name'))

    org = EndUserEnterprise(real_name=request.POST.get('name'),
                            status=EndUserEnterprise.STATUS_INACTIVE,
                            ent_type=ent_type,
                            id_card_image=request.POST.get('id_card_image'),
                            license_image=request.POST.get('license_image'),
                            created_by=user.uid)
    is_group = 'G' == request.POST.get('user_type')
    if is_group:
        org.user_type = EndUserEnterprise.USER_GROUP
    else:
        org.user_type = EndUserEnterprise.USER_ENTERPRISE

    # if request.POST.get('avatar'):
    #     org.avatar = request.POST.get('avatar')
    attributes = ['address', 'avatar', 'register_ip', 'intro',
                  'contact_name', 'contact_mobile', 'contact_phone', 'contact_email']
    for attr in attributes:
        if attr in request.POST:
            setattr(org, attr, request.POST.get(attr))
    org.save()
    if not user.is_org_staff or (not is_group and not user.org_uid):
        user.is_org_staff = True
        if not is_group:
            # 用户创建企业后，如果该用户尚无归属企业则自动将用户加入企业
            user.org_uid = user.org_uid or org.uid
        user.save(update_fields=['is_org_staff', 'org_uid'])

    EndUserRole.objects.create(user_uid=user.uid, org_uid=org.uid, role=EndUserRole.ROLE_SP)
    return json_response({"uid": org.uid})


def add_link(request):
    """
    为指定企业用户添加链接
    :param request (POST):
        - org_uid, 企业用户uid
        - link_type, 链接类型，可以是website-企业网站, weibo-微博, wechat-微信公众号
        - link, url地址或者名称

    :return:
        成功返回{"result": "ok", "id": link_id}
        失败返回{"error": msg}

    eg. <a href="/tms-api/add_link">查看样例</a>
    """
    # user = get_user_by_uid(request)
    # if not user:
    #     return report_error('无效的用户账号！')
    org = get_user_by_uid(request, attr='org_uid')
    if not org or org.user_type == EndUser.USER_PERSON:
        return report_error('无效的企业用户账号！')

    # if not EndUserRole.objects.filter(user_uid=user.uid, org_uid=org.uid,
    #                                   role__in=(EndUserRole.ROLE_ADMIN, EndUserRole.ROLE_SP)).exists():
    #     return report_error('没有操作权限！')

    if not request.POST.get('link') or \
            not request.POST.get('link_type') in [link_type for link_type, link_display in EndUserLink.LINK_TYPES]:
        return report_error('请提供链接地址及有效的链接类型')

    link = EndUserLink(uid=org.uid, link_type=request.POST.get('link_type'), link=request.POST.get('link'))
    link.save()
    return report_ok({'id': link.id})


def del_link(request):
    """
    删除企业用户相关链接
    :param request (POST):
        - org_uid，企业用户UID，用于检查用户是否有权限修改链接信息
        - link_id，链接id
    :return:
        成功返回{"result": "ok", "id": link_id}
        失败返回{"error": msg}

    eg. <a href="/tms-api/del_link">查看样例</a>
    """
    # user = get_user_by_uid(request)
    # if not user:
    #     return report_error('无效的用户账号！')
    try:
        link = EndUserLink.objects.get(id=request.POST.get('link_id'))
        org = EndUser.objects.get(uid=link.uid)
        if org.user_type == EndUser.USER_PERSON:
            return report_error('无效的企业账号')
        elif link.uid != org.uid:
            return report_error('没有操作权限')
            # if not EndUserRole.objects.filter(user_uid=user.uid, org_uid=org.uid,
            #                                   role__in=(EndUserRole.ROLE_ADMIN, EndUserRole.ROLE_SP)).exists():
            #     return report_error('没有操作权限！')
        link.delete()
        return report_ok()
    except EndUserLink.DoesNotExist:
        return report_error('找不到链接(id:%s)' % request.POST.get('link_id'))


def update_org(request):
    """
    更新企业用户信息
    :param request (POST):
        - uid，用户UID，用于检查用户是否有权限修改组织信息 （必须是当前组织的管理员）
        - org_uid，要更改信息的企业用户uid
        - [name, id_card_image, license_image, avatar]，可选， 要变更的名称，责任人身份证照，营业证照，企业LOGO
            注意：上述几项如果有修改，该企业信息需要重新审核
        - [parent_uid], 可选，用于调整组织从属关系
        - [intro, contact_name, contact_mobile, contact_phone, contact_email], 可选，要变更的企业简介，联系人，联系人手机，联系人电话及联系人email地址
            上述信息变更不影响企业审核状态
    :return:
        成功返回{result: 'ok'} 失败返回{error: 'msg'}

    eg. <a href="/tms-api/update_org">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return report_error('无效的用户账号！')
    if not request.POST.get('org_uid'):
        return report_error('请提供企业用户uid')

    try:
        org = EndUserEnterprise.objects.get(uid=request.POST.get('org_uid'))
        if org.status == EndUserEnterprise.STATUS_BANNED:
            return report_error('当前企业账号(uid: %s)无效，请与系统管理员或客服联系' % org.uid)
        # 只有企业账号管理员可以操作
        if not EndUserRole.objects.filter(user_uid=user.uid, org_uid=org.uid,
                                          role__in=(EndUserRole.ROLE_ADMIN, EndUserRole.ROLE_SP)).exists():
            return report_error('没有操作权限')
    except EndUserEnterprise.DoesNotExist:
        return report_error('找不到uid（%s）对应的企业信息' % request.POST.get('org_uid'))
    else:
        if request.POST.get('name') or request.POST.get('id_card_image') \
                or request.POST.get('license_image') or request.POST.get('avatar'):
            org.review_status = EndUserEnterprise.REVIEW_PENDING
            if request.POST.get('name'):
                org.name = request.POST.get('name')
            if request.POST.get('id_card_image'):
                org.id_card_image = request.POST.get('id_card_image')
            if request.POST.get('license_image'):
                org.license_image = request.POST.get('license_image')
            if request.POST.get('avatar'):
                org.avatar = request.POST.get('avatar')
        if request.POST.get('intro'):
            org.intro = request.POST.get('intro')
        if request.POST.get('contact_name'):
            org.contact_name = request.POST.get('contact_name')
        if request.POST.get('mobile'):
            org.mobile = request.POST.get('mobile')
        if request.POST.get('phone'):
            org.phone = request.POST.get('phone')
        if request.POST.get('email'):
            org.email = request.POST.get('email')
        if 'parent_uid' in request.POST:
            if org.user_type == EndUserEnterprise.USER_GROUP:
                return report_error('集团企业不可再设上级')
            elif request.POST.get('parent_uid'):
                if org.uid == request.POST.get('parent_uid'):
                    return report_error('不可将自身设为上级')
                try:
                    group = EndUserEnterprise.objects.get(uid=request.POST.get('parent_uid'),
                                                          user_type=EndUserEnterprise.USER_GROUP,
                                                          status=EndUserEnterprise.STATUS_ACTIVE)

                    org.org_uid = group.uid
                    # 保存关系快照
                    UserOrgSnapShot.objects.create(uid=org.uid, org_uid=group.uid, overhead_rate=group.overhead_rate)
                except EndUserEnterprise.DoesNotExist:
                    return report_error('无效的上级企业')
            else:
                org.org_uid = None

        org.save()
        return report_ok()


def review_org(request):
    """
    为企业用户申请提供审核意见和结论
    :param request （POST）:
        - uid, 用于验证是否有审核的权限
        - org_uid，审核对象企业的uid
        - review_status, 审核结论
            * "passed", 表示审核通过
            * "rejected", 审核被拒绝
            * "hold"， 暂时搁置
        - [review_note], 可选(当结论不是"passed"时必填)，审核意见，主要用于提示用户审核未通过的理由

    :return:
        成功返回{result: ok} 失败返回{error: msg}

    """
    user = get_user_by_uid(request)
    if not user:
        return report_error('无效的用户账号！')
    if user.uid not in AppSetting.get('app.enterprise_reviewer', '').split(','):
        return report_error('没有权限')

    if not request.POST.get('org_uid'):
        return report_error('请提供企业用户uid')
    try:
        org = EndUserEnterprise.objects.get(uid=request.POST.get('org_uid'))
        review_status = request.POST.get('review_status')
        if review_status not in [s for s, txt in EndUserEnterprise.REVIEW_STATUSES]:
            return report_error('无效的审核结论：%s' % review_status)
        else:
            if review_status != 'passed' and not request.POST.get('review_note'):
                return report_error('请提供审核不通过的理由')
            org.review_status = review_status
            org.status = EndUserEnterprise.STATUS_ACTIVE \
                if review_status == 'passed' \
                else EndUserEnterprise.STATUS_INACTIVE
            org.review_note = request.POST.get('review_note') or org.review_note
            org.save()
            return report_ok()
    except EndUserEnterprise.DoesNotExist:
        return report_error('企业不存在')


def query_orgs(request):
    """
    查询组织用户信息
    :param request (GET):
        - [uid],可选, 企业用户uid，如有多个，可用英文逗号分隔
        - [name], 可选，组织名称，模糊匹配
        - [status], 可选，账号状态，默认只返回有效的组织列表，可选值如下
            * 0, 有效
            * 1, 无效
            * 99, 黑名单
            * 'all', 全部
        - [review_status]，可选，审核状态，默认只返回审核通过的组织列表，可选值如下：
            * 'pending', 待审核
            * 'passed', 已通过
            * 'rejected', 已拒绝
            * 'hold', 暂时搁置
            * 'all', 全部
        - [parent_uid], 可选，上级企业的uid，即返回指定企业名下的所有归属企业
        - [is_group], 可选，默认返回所有，包含集团企业和非集团企业，1为集团企业，0为非集团企业
        - [with_links], 可选，提供该参数后（无需值）返回关联的链接如微信公众号，微博，企业网站等，默认不返回
        - [pos], 可选，获取的结果可能存在多页时，给定开始选取的位置，默认为0
        - [size], 可选，获取的结果可能存在多页时，确定返回每页记录数，默认为10

    :return:
        成功返回
        [
            {
                address: "地址"
                avatar: "test_logo.png",    （企业LOGO）
                contact_email: null,
                contact_mobile: null,
                contact_name: "contact_name",
                contact_phone: null
                enduser_ptr: "3f499cacdfc8444dab29166975bdba5b", （同组织uid）
                id_card_image: "test_id_image.png",    （责任人身份证照）
                intro: "test intro",    （简介）
                last_login: null,
                license_image: "test_license_image.png",    （企业执照/资质证照）
                org_uid: null,      （所属集团企业uid，仅当为普通企业时可能有）
                real_name: "org608250844260000",  （组织名称）
                referrer: null,
                review_note: null,  （审核意见）
                review_status: "pending",   （审核状态， 'pending'-待审核，'passed'-已通过，'rejected'-已拒绝，'hold'-暂时搁置）
                status: 0,  （状态，0-有效，1-无效，99-黑名单）
                uid: "3f499cacdfc8444dab29166975bdba5b",    （组织uid）
                user_type: "G",     （组织类型，G-集团企业，E-普通企业）
                links: [    (仅当提供with_links参数时返回)
                    {
                        link: "http://test.link/",
                        id: 4,
                        link_type: "website",
                        uid: "d89e46d6bd1349e1b844ce3208150ed0"
                    }
                ],
            },
        ]
        失败返回{error: msg}

    eg. <a href="/tms-api/query_orgs">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    orgs = EndUserEnterprise.objects.all()
    if req.get('status'):
        if 'all' != req.get('status'):
            orgs = orgs.filter(status=req.get('status'))
    else:
        orgs = orgs.filter(status=EndUserEnterprise.STATUS_ACTIVE)

    if req.get('uid'):
        orgs = orgs.filter(uid__in=req.get('uid').split(','))

    if req.get('name'):
        orgs = orgs.filter(real_name__istartswith=req.get('name'))

    if req.get('review_status'):
        if 'all' != req.get('review_status'):
            orgs = orgs.filter(review_status=req.get('review_status'))
    else:
        orgs = orgs.filter(review_status=EndUserEnterprise.REVIEW_PASSED)

    if req.get('parent_uid'):
        orgs = orgs.filter(org_uid=req.get('parent_uid'))

    if '1' == req.get('is_group'):
        orgs = orgs.filter(user_type=EndUserEnterprise.USER_GROUP)
    elif '0' == req.get('is_group'):
        orgs = orgs.filter(user_type=EndUserEnterprise.USER_ENTERPRISE)

    start_pos = int(req.get('pos', 0))
    page_size = int(req.get('size', 4))
    # page_size = page_size if 2 < page_size < 20 else 20 if page_size >= 20 else 2
    if req.get('page'):
        start_pos = int(req.get('page')) * page_size
    orgs = orgs[start_pos:start_pos+page_size]

    orgs = [org.to_dict() for org in orgs]
    if 'with_links' in req:
        org_uids = [org['uid'] for org in orgs]
        org_dict = dict([(org['uid'], org) for org in orgs])
        links = EndUserLink.objects.filter(uid__in=org_uids)
        for link in links:
            org_dict[link.uid]['links'] = link if 'links' in org_dict[link.uid] else [link]
    return renderutil.json_response(orgs)


def query_users(request):
    """
    查询用户信息
    :param request (GET):
        - [uid]
            uid，用户uid，如有多个，可用英文逗号分隔
        - [status], 可选，账号状态，默认只返回有效的组织列表，可选值如下
            * 0, 有效
            * 1, 无效
            * 99, 黑名单
            * 'all', 全部
        - [entry_uid], 可选，首次进入入口用户uid
        - [referrer], 可选，推荐人
        - [org_uid], 可选，所属企业的uid，即返回指定企业名下的所有用户
        - [group_uid], 可选，所属集团企业的uid，即返回指定企业名下的所有用户，包含集团旗下所有企业名下的用户
        - [pos], 可选，获取的结果可能存在多页时，给定开始选取的位置，默认为0
        - [size], 可选，获取的结果可能存在多页时，确定返回每页记录数，默认为10
        - [with_internal]，可选，可以没有值，返回包含内部管理账号相关信息，参见get_user
        - [with_org]，可选，可以没有值
            如果提供该参数，则返回的org属性为关联的组织详情（Json对象，如旅行社），否则返回的org为组织账号的uid，参见get_user
        - [with_managed], 可选，可以没有值
            如果提供该参数，则返回用户管理的组织列表

    :return:
        成功返回：
        [
            {
                avatar: "avatar.png",
                entry_uid: "test_12345678",
                ex_avatar: "ex_avatar",
                ex_nick_name: "ex_nick_name",
                gender: "X",
                intro: "test intro",
                is_org_staff: true,     (是否企业的管理者或职员，对企业信息具有全部或部分管理权限)
                last_login: null,
                mobile: "608250902602000",
                nick_name: "nick_name",
                org_uid: "62f8c368b0cd44aca5720356e803a3df",
                real_name: "real_name",
                referrer: "test_12345678",
                status: 0,
                uid: "9e409d57e88c46a39d22a69b6540645b",
                user_type: "P",     （用户类型，P为普通用户，E为普通企业，G为集团企业，本接口只返回普通用户，查询企业请用query_orgs）
                managed_org: [  （仅当提供with_managed参数时返回）
                    {
                        org_uid: "db94fce6f9b445ff8b0cb9753449b57b",    (管理的组织uid)
                        user_uid: "9e409d57e88c46a39d22a69b6540645b",   （用户的uid）
                        role: "admin",  (用户在组织中的角色)
                        id: 6
                    }
                ],
            }
        ]

        失败返回{error: msg}

    eg. <a href="/tms-api/query_users">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    users = EndUser.objects.filter(user_type=EndUser.USER_PERSON)
    if req.get('status'):
        if 'all' != req.get('status'):
            users = users.filter(status=req.get('status'))
    else:
        users = users.filter(status=EndUser.STATUS_ACTIVE)

    if req.get('uid'):
        users = users.filter(uid__in=req.get('uid').split(','))

    if req.get('entry_uid'):
        users = users.filter(entry_uid=req.get('entry_uid'))

    if req.get('referrer'):
        users = users.filter(referrer=req.get('referrer'))

    if req.get('org_uid'):
        users = users.filter(org_uid=req.get('org_uid'))

    if req.get('group_uid'):
        groups = EndUser.objects.filter(org_uid=req.get('group_uid'),
                                        user_type=EndUser.USER_ENTERPRISE).values_list('uid', flat=True)
        users = users.filter(org_uid__in=groups)

    start_pos = int(req.get('pos', 0))
    page_size = int(req.get('size', 4))
    # page_size = page_size if 2 < page_size < 20 else 20 if page_size >= 20 else 2
    if req.get('page'):
        start_pos = int(req.get('page')) * page_size
    users = users[start_pos:start_pos+page_size]

    users = [user.to_dict() for user in users]
    users_dict = dict([(user['uid'], user) for user in users])
    if 'with_internal' in req:
        try:
            usernames = EndUserExt.objects.filter(uid__in=users_dict.keys(),
                                                  ex_id_type=EndUserExt.ID_TYPE_INTERNAL).values_list('ex_id', 'uid')
            if len(usernames) > 0:
                usernames_dict = dict(usernames)
                internal_users = User.objects.filter(username__in=[n[0] for n in usernames])
                for iu in internal_users:
                    internal_user = {'username': iu.username,
                                     'is_active': iu.is_active,
                                     'is_superuser': iu.is_superuser,
                                     'email': iu.email,
                                     'fullname': iu.get_full_name(),
                                     'suppliers': []}
                    supplier_mgrs = iu.suppliermanager_set.all()
                    for sup in supplier_mgrs:
                        internal_user['suppliers'].append(sup.supplier.to_dict())

                    users_dict[usernames_dict[iu.username]]['internal_user'] = internal_user
        except (EndUserExt.DoesNotExist, User.DoesNotExist):
            pass
        except Exception, e:
            logger.exception(e)

    if 'with_org' in req:
        users_with_org = [(user.get('uid'), user.get('org_uid')) for user in users if user.get('org_uid')]
        if len(users_with_org) > 0:
            orgs = EndUserEnterprise.objects.filter(uid__in=set([u[1] for u in users_with_org]))
            orgs_dict = dict([(org.uid, org) for org in orgs])
            for uid, org_uid in users_with_org:
                users_dict[uid]['org'] = orgs_dict[org_uid].to_dict()

    if 'with_managed' in req:
        users_with_managed = [user.get('uid') for user in users if user.get('is_org_staff')]
        if len(users_with_managed) > 0:
            managed = EndUserRole.objects.filter(user_uid__in=users_with_managed)
            for role in managed:
                if 'managed_org' in users_dict[role.user_uid]:
                    users_dict[role.user_uid]['managed_org'].append(role)
                else:
                    users_dict[role.user_uid]['managed_org'] = [role]

    return renderutil.json_response(users)


def update_user(request):
    """
    更新用户基本信息
    :param request(POST):
        - uid, 用户uid
        - [nick_name], 可选，昵称
        - [avatar], 可选，头像
        - [real_name], 可选，真实姓名
        - [gender], 可选，性别，单字母，M-男，F-女，X-不告诉你
        - [mobile], 可选，手机号，待实现
        - [id_card], 可选，身份证号，待实现
        - [password], 可选，密码，待实现（不使用用户明文，只提交用户填写的密码用SHA1计算出的签名）
        - [ex_nick_name], 可选，第三方昵称，字符串，用于更新
        - [ex_avatar], 可选，第三方头像，字符串，用于更新
        - [intro], 可选，简介
        - [entry_uid], 可选，入口用户uid，即用户首次扫码进入，成为新用户时入口用户的uid
        - [referrer], 可选，推荐人uid，即用户被推荐成为导游时推荐人的uid
        - [org_uid], 可选，归属组织uid
    :return:
        成功返回{'result': 'ok'}
        失败返回{'error': msg}

    eg. <a href="/tms-api/update_user">查看样例</a>
    """
    user = get_user_by_uid(request)
    if user is None or user.status != EndUser.STATUS_ACTIVE:
        return report_error('无效的用户')

    if user.user_type != EndUser.USER_PERSON:
        return report_error('只能修改普通用户的基本信息')

    r = user.referrer
    e = user.entry_uid
    # g = user.gender

    attributes = ['ex_nick_name', 'ex_avatar', 'nick_name', 'avatar', 'real_name', 'gender', 'mobile', 'id_card',
                  'password', 'intro', 'entry_uid', 'referrer', ]
    for attr in attributes:
        if attr in request.POST:
            if attr == 'password':
                setattr(user, attr, hashers.make_password(request.POST.get(attr)))
                continue
            elif request.POST.get('mobile') \
                    and EndUser.objects.filter(mobile=request.POST.get('mobile')).exclude(uid=user.uid).exists():
                return report_error('手机号[%s]已绑定其它账号' % request.POST.get('mobile'))
            elif attr in ['referrer', 'entry_uid']:
                # TODO: should verify entry_uid and referrer validity
                if request.POST.get(attr) == user.uid:
                    return report_error('推荐人/入口不可是用户自身')
                elif attr == 'referrer' and user.referrer:
                    return report_error('已有推广人不可变更')
                elif attr == 'entry_uid' and user.entry_uid:
                    return report_error('已有入口推广人不可变更')

        if request.POST.get(attr) is not None:
            setattr(user, attr, request.POST.get(attr))

    if r is not None and len(r) > 0:
        setattr(user, 'referrer', r)
    if e is not None and len(e) > 0:
        setattr(user, 'entry_uid', e)
    # setattr(user, 'gender', g)

    if 'org_uid' in request.POST:
        if request.POST.get('org_uid'):
            try:
                org = EndUserEnterprise.objects.get(uid=request.POST.get('org_uid'))
                if org.status != EndUserEnterprise.STATUS_ACTIVE or org.review_status != EndUserEnterprise.REVIEW_PASSED:
                    return report_error('无效的企业用户')
                else:
                    user.org_uid = org.uid
                    UserOrgSnapShot.objects.create(uid=user.uid, org_uid=org.uid, overhead_rate=org.overhead_rate)  # 保存关系快照

            except EndUserEnterprise.DoesNotExist:
                return report_error('无效的企业用户')
        else:
            user.org_uid = None  # 脱离组织关系
            UserOrgSnapShot.objects.create(uid=user.uid, org_uid='', overhead_rate=None)  # 保存关系快照

    user.save()
    return report_ok()


def set_org_role(request):
    """
    设置（添加或删除）企业职员/管理员，如果是退出归属企业，请用update_user接口
    注意：如果用户已有企业的某种身份，则设置新身份的话，将覆盖原有设置（即用户在企业中只能是一种身份）
    :param request (POST):
        - uid, 用户uid
        - org_uid, 企业uid
        - [role], 可选，
            * 默认为"staff"即普通职
            * "admin" 为管理员
            * "sp" 为超级管理员
        - [is_delete], 可选，是否删除
            如果包含该参数，则从指定org中删除指定uid的管理员/职员，忽略role参数
            否则，为指定org添加指定uid的用户为管理员或职元（取决于role）

    :return:
        成功返回{"result": "ok"} ，如果包含is_delete参数，则返回{"result": "ok", "affected": 1} (affected表示删除的记录数，一般为1)
        失败返回错误提示{"error": msg}

    eg. <a href="/tms-api/set_org_role">查看样例</a>
    """
    user = get_user_by_uid(request)
    if user is None:
        return report_error('无效的用户')

    org = get_user_by_uid(request, attr='org_uid')
    if org is None or org.user_type == EndUser.USER_PERSON:
        return report_error('无效的企业用户')

    role = request.POST.get('role')
    role = role if role in ('sp', 'admin', 'staff') else 'staff'
    if 'is_delete' in request.POST:
        rows = EndUserRole.objects.filter(user_uid=user.uid, org_uid=org.uid).delete()
        return report_ok({"affected": rows})
    else:
        role, created = EndUserRole.objects.update_or_create(user_uid=user.uid, org_uid=org.uid, defaults={"role": role})
        if created:
            return report_ok({'is_new': True})
        else:
            return report_ok()


def unbind_user(request):
    """
    解绑用户管理账号
    :param request (POST):
        - uid, 要解绑的普通终端用户的uid
        - account, 与之绑定的后台管理账号
        - passwd, 后台管理账号密码（用于解绑验证）
    :return:
        成功返回{result: ok} 失败返回错误消息{error: msg}

    eg. <a href="/tms-api/unbind_user">查看样例</a>
    """
    end_user = get_user_by_uid(request)
    if end_user is None:
        return report_error(u'无效的用户！', code=INVALID_ACCOUNT_ERR)

    try:
        user_ext = EndUserExt.objects.filter(uid=end_user.uid,
                                             ex_id_type=EndUserExt.ID_TYPE_INTERNAL,
                                             ex_id=request.POST.get('account'))
    except EndUserExt.DoesNotExist:
        return report_error('用户未绑定账号[%s]' % request.POST.get('account'))
    else:
        try:
            user = User.objects.get(username=request.POST.get('account'), is_active=True)
            # if not user.check_password(request.POST.get('passwd')):  # modify by shengzhe 01/19
            #     return report_error(u'账号密码不匹配！', code=PASSWORD_MISMATCH_ERR)
        except User.DoesNotExist:
            return report_error(u'无效的账号[%s]！' % request.POST.get('account'), code=INVALID_ACCOUNT_ERR)
        else:
            user_ext.delete()
            return report_ok({"msg": "已解绑账号%s" % request.POST.get('account')})


def bind_user(request):
    """
    将普通用户账号与后台管理账号绑定
    :param request(POST):
        - uid, 普通终端用户的uid
        - account, 后台管理账号
        - passwd, 后台管理账号密码
        - [override], 是否覆盖原先账号绑定设置，默认为0， 1表示覆盖
    :return:
        成功返回用户对象
            {
                'username': 'sp',
                'uid': 'afebfaa8457d4e0asdfqw7a317d9493e',
                'suppliers': [],
                'is_superuser': True,
                'is_staff': True,
                'fullname': '',
                'warning': '账号已绑定，请勿重复操作！',
                'email': 'winsom.huang@sh-anze.com'
            }

        如果管理账号已绑定同一用户账号，返回的用户对象中会包含"warning"提示
        如果管理账号已绑定其它用户账号，则override为1时直接覆盖，否则返回错误提示“账号已绑定其它用户，请重新确认”
        如果用户账号已绑定其它管理账号，则override为1时直接覆盖，否则返回错误提示“用户已绑定其它账号，请重新确认”
        失败返回{'error': msg}

    eg. <a href="/tms-api/bind_user">查看样例</a>
    """
    if not request.POST.get('uid') or not request.POST.get('account') or not request.POST.get('passwd'):
        return report_error(u'参数不完整！', code=INVALID_PARAMETERS_ERR)

    end_user = get_user_by_uid(request)
    if end_user is None:
        return report_error(u'无效的用户！', code=INVALID_ACCOUNT_ERR)

    try:
        user = User.objects.get(username=request.POST.get('account'), is_active=True)
        if not user.check_password(request.POST.get('passwd')):
            return report_error(u'账号密码不匹配！', code=PASSWORD_MISMATCH_ERR)
    except User.DoesNotExist:
        return report_error(u'无效的账号[%s]！' % request.POST.get('account'), code=INVALID_ACCOUNT_ERR)
    else:
        result = {}
        user_ext = EndUserExt.objects.filter(Q(uid=end_user.uid) | Q(ex_id=request.POST.get('account')),
                                             ex_id_type=EndUserExt.ID_TYPE_INTERNAL)
        # 检查用户或管理账号是否已绑定其它
        if user_ext.exists():
            if request.POST.get('override') == '1':
                user_ext.delete()
                end_user_ext = EndUserExt(ex_id_type=EndUserExt.ID_TYPE_INTERNAL,
                                          ex_id=request.POST.get('account'),
                                          uid=end_user.uid)
                end_user_ext.save()
            else:
                for ue in user_ext:
                    if ue.uid == end_user.uid:
                        return report_error('用户已绑定账号[%s]' % ue.ex_id, code=DUPLICATE_ACCOUNT_BINDING_ERR)
                    # elif ue.ex_id == request.POST.get('account'):
                    else:
                        return report_error('账号[%s]已绑定其它用户' % ue.ex_id, code=DUPLICATE_ACCOUNT_BINDING_ERR)
        else:
            end_user_ext = EndUserExt(ex_id_type=EndUserExt.ID_TYPE_INTERNAL,
                                      ex_id=request.POST.get('account'),
                                      uid=end_user.uid)
            end_user_ext.save()

        result.update({'uid': end_user.uid,
                       'username': user.username,
                       'is_staff': user.is_staff,
                       'is_superuser': user.is_superuser,
                       'email': user.email,
                       'fullname': user.get_full_name(),
                       'suppliers': []})
        supplier_mgrs = user.suppliermanager_set.all()
        for sup in supplier_mgrs:
            result['suppliers'].append(sup.supplier.to_dict())

        return json_response(result)


def mark(request):
    """
    关注或者取消关注指定商品（或其它对象，待扩展）
    :param request:http GET 请求，包含
        entity_type, 收藏类型，以单个或两个大写字母表示，比如"P"表示商品（待扩展）
        entity_id, 对应项目id，当entity_type为"P"时，是指商品的id
        [type]，可选，将条目标记为收藏，默认为0，收藏 （待扩展）
        [mark], 可选，0 或者 1，默认为1， 如果为1，则添加一条记录，不为1则删除对应的收藏记录
        此接口需要验证用户
    :return:
        成功返回{"result": "ok"}
        失败返回错误提示{"error": msg}

    eg. <a href="/tms-api/mark">查看样例</a>
    """
    user = validate_token(request)
    if not user:
        return REQUIRE_LOGIN

    req = request.POST if 'POST' == request.method else request.GET
    entity_type = req.get('entity_type', None)
    entity_id = req.get('entity_id', 0)
    type = req.get('type', 0)
    mark = req.get('mark', '1')  # if not implicitly set 0, it's to mark
    if not entity_type or not entity_id:
        return report_error(u'参数错误，需要提供entity_type及entity_id参数')

    try:
        record = UserFavorite.objects.get(uid=user['uid'], favor_type=type,
                                          entity_type=entity_type, entity_id=entity_id)
        if "1" != mark:
            record.delete()
    except UserFavorite.DoesNotExist:
        if "1" == mark:
            UserFavorite(uid=user['uid'], favor_type=type,
                         entity_type=entity_type, entity_id=entity_id).save()

    return report_ok()


def is_user_favorite(user_id, entity_id, entity_type='P'):
    """
    给定类型对象及其id，判断是否为指定用户的关注/收藏
    :param user_id:
    :param entity_id:
    :param entity_type:
    :return:
    """
    if not user_id or not entity_id or not entity_type:
        return False

    try:
        record = UserFavorite.objects.get(uid=user_id,
                                          favor_type=0,
                                          entity_type=entity_type,
                                          entity_id=entity_id)
        return True if record else False  # return True may be enough
    except UserFavorite.DoesNotExist:
        return False


def is_favorite(request):
    """
    给定类型对象及其id，判断是否为指定用户的关注/收藏
    :param entity_id:
    :param entity_type:

    :return:
    """
    req = request.POST if 'POST' == request.method else request.GET
    user = validate_token(request)
    res = False
    if user:
        res = is_user_favorite(user.get('uid'),
                               req.get('entity_id'),
                               req.get('entity_type', 'P'))
    return renderutil.json_response(res)


def my_favorite(request):
    """
    获取当前用户关注/收藏列表
    :param request: http GET 请求
        - [pos], 可选，起始偏移量，默认为0
        - [size]，可选，一次获取多少数据，默认为10
    :return:
        返回当前用户关注的商品列表（基础信息，参见get_product）

    eg. <a href="/tms-api/my_favorite">查看样例</a>
    """
    user = validate_token(request)
    if not user:
        return REQUIRE_LOGIN

    req = request.POST if 'POST' == request.method else request.GET
    try:
        from basedata.models import Product
        records = UserFavorite.objects.filter(uid=user['uid'])
        start_pos = int(req.get('pos', 0))
        page_size = int(req.get('size', 10))
        # page_size = page_size if 2 < page_size < 20 else 20 if page_size >= 20 else 2
        if req.get('page'):
            start_pos = int(req.get('page')) * page_size
        records = records[start_pos:start_pos+page_size]
        pids = [r.entity_id for r in records]
        products = Product.objects.filter(code__in=pids)
        return json_response([prd.to_dict() for prd in products])
    except ObjectDoesNotExist:
        return json_response([])


def my_history(request):
    """
    获取当前用户的查看商品详情的历史
    只返回最近的10条
    :param request: http GET 请求
    :return:
        返回商品列表（基础信息，见get_product）[{product1}, {product2}, ...]

    eg. <a href="/tms-api/my_history">查看样例</a>
    """
    user = validate_token(request)
    if not user:
        return REQUIRE_LOGIN

    try:
        from basedata.models import Product
        records = UserHistory.objects.filter(uid=user['uid'])
        records = records.filter(entity_type='P')[0:10]
        pids = [r.entity_id for r in records]
        products = Product.objects.filter(code__in=pids)
        results = [prd.to_dict() for prd in products]

        return json_response(results)
    except ObjectDoesNotExist:
        return json_response([])


def my_keyword(request):
    """
    获取当前用户的搜索的历史
    只返回最近的10条
    :param request: http GET 请求
        - [public]，可选，是否返回其它人搜索的关键字，无需参数值，不提供则返回个人搜索关键字历史
    :return:
        返回搜索关键字列表 [keyword1, keyword2, ...]

    eg. <a href="/tms-api/my_keyword?public">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    if 'public' in req:
        from config.models import AppSetting
        keywords = AppSetting.get('app.search.public_keywords', '')
        return json_response(keywords.split(',') if keywords else [])
        # try:
        #     records = UserHistory.objects.filter(entity_type='KW').values('entity_value').order_by('entity_value').distinct()[0:10]
        #     return json_response([r['entity_value'] for r in records])
        # except ObjectDoesNotExist:
        #     pass
    else:
        user = validate_token(request)
        if user:
            try:
                records = UserHistory.objects.filter(uid=user['uid'])
                records = records.filter(entity_type='KW').values('entity_value').order_by('entity_value').distinct()[0:10]
                return json_response([r['entity_value'] for r in records])
            except ObjectDoesNotExist:
                pass

    return json_response([])


def add_ship_addr(request):
    """
    添加物流地址(通常不需要单独调用该接口，创建订单时将地址信息传入会自动保存)
    :param request（POST）:
        - uid, 用户id
        - receiver, 收件人姓名
        - receiver_mobile, 收件人手机
        - ship_province, 收件省份
        - [ship_city], 收件市，可选
        - [ship_district], 收件区/县，可选
        - ship_address, 收件人地址
        - [zip_code]，邮编，可选
    :return:
        成功返回{"result": "ok", "id": ship_addr.id}
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/add_ship_addr">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号')

    receiver = request.POST.get('receiver')
    mobile = request.POST.get('mobile') or request.POST.get('receiver_mobile')
    address = request.POST.get('address') or request.POST.get('ship_address')
    if not receiver or not receiver.strip() \
            or not mobile or not mobile.strip() \
            or not address or not address.strip():
        return renderutil.report_error(u'请提供完整的收件人信息（含姓名/电话/地址）')

    from config.models import AppSetting
    max_limit = AppSetting.get('ship_address_max_limit', 200)
    if ShipAddress.objects.filter(uid=user.uid).count() >= max_limit:
        return renderutil.report_error(u'个人收件地址不得超过%s条！' % max_limit)

    ship_province = request.POST.get('ship_province')
    ship_city = request.POST.get('ship_city')
    ship_district = request.POST.get('ship_district')
    ship_addr, created = ShipAddress.objects.get_or_create(uid=user.uid,
                                                           receiver=receiver,
                                                           receiver_mobile=mobile,
                                                           ship_province=ship_province,
                                                           ship_city=ship_city,
                                                           ship_district=ship_district,
                                                           ship_address=address,
                                                           zip_code=request.POST.get('zip_code', ''))
    ship_addr = model_to_dict(ship_addr)
    ship_addr.update({"result": "ok"})
    return renderutil.json_response(ship_addr)


def update_ship_addr(request):
    """
    更新物流地址
    :param request（POST）:
        - uid, 用户uid
        - addr_id, 地址id
        - receiver, 收件人姓名
        - receiver_mobile, 收件人手机
        - ship_address, 收件人地址
        - [ship_province], 收件省份，可选
        - [ship_city], 收件市，可选
        - [ship_district], 收件区/县，可选
        - [zip_code]，邮编，可选
    :return:
        成功返回
        {
            "id": 1,
            "receiver": 收件人姓名,
            "receiver_mobile": 收件人手机,
            "ship_address": 收件人地址,
            "zip_code": 邮编,
            "result": "ok"
        }

        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/update_ship_addr">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号')

    receiver = request.POST.get('receiver')
    mobile = request.POST.get('mobile') or request.POST.get('receiver_mobile')
    address = request.POST.get('address') or request.POST.get('ship_address')
    if not receiver or not receiver.strip() \
            or not mobile or not mobile.strip() \
            or not address or not address.strip():
        return renderutil.report_error(u'请提供完整的收件人信息（含姓名/电话/地址）')

    ship_province = request.POST.get('ship_province')
    ship_city = request.POST.get('ship_city')
    ship_district = request.POST.get('ship_district')

    addr_id = request.POST.get('addr_id')
    try:
        ship_addr = ShipAddress.objects.get(uid=user.uid, id=addr_id)
        ship_addr.receiver = receiver
        ship_addr.receiver_mobile = mobile
        ship_addr.ship_province = ship_province
        ship_addr.ship_city = ship_city
        ship_addr.ship_district = ship_district
        ship_addr.ship_address = address
        ship_addr.zip_code = request.POST.get('zip_code', '')
        ship_addr.save()
        ship_addr = model_to_dict(ship_addr)
        ship_addr.update({"result": "ok"})
        return renderutil.json_response(ship_addr)
    except ShipAddress.DoesNotExist:
        return renderutil.report_error(u'地址参数[%s]无效或用户无权更新' % addr_id)


def del_ship_addr(request):
    """
    删除物流地址
    :param request（POST）:
        - uid, 用户的uid
        - addr_id, 物流地址id，见get_ship_addr
    :return:
    删除成功返回{"result": "ok"}, 否则返回错误提示{"error": msg}

    eg. <a href="/tms-api/del_ship_addr">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号')

    addr_id = int(request.POST.get('addr_id'))
    if not addr_id:
        return renderutil.report_error(u"缺少有效的addr_id参数")

    try:
        address = ShipAddress.objects.get(uid=user.uid, id=addr_id)
        address.delete()
    except ShipAddress.DoesNotExist:
        return renderutil.report_error(u'地址[%s]不存在或用户无权删除' % addr_id)

    return renderutil.report_ok({'addr_id': addr_id})


def get_ship_addr(request):
    """
    获取用户使用过的收件人地址列表
    :param request (GET):
        - uid, 用户的uid
    :return:
     成功返回地址数组
     [
        {
            "id": 1,
            "receiver": 收件人姓名,
            "receiver_mobile": 收件人手机,
            "ship_address": 收件人地址
            "zip_code": 邮编
        }
     ]
     失败则返回错误提示{"error": msg}

    eg. <a href="/tms-api/get_ship_addr">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return renderutil.report_error(u'无效的用户账号')

    addresses = ShipAddress.objects.filter(uid=user.uid)\
        .values('id', 'receiver', 'receiver_mobile', 'ship_province',
                'ship_city', 'ship_district', 'ship_address', 'zip_code')
    return renderutil.json_response(addresses)


def logoff(request):
    """
    注销已验证通过的用户
    :param request:
        无需参数，但是如果本地有uidtoken的话，仍需附在请求的header中
    :return:
        注销后返回{"result": "ok"}
    eg. <a href='/tms-api/logoff'>查看样例</a>
    """
    user = request.session.get('enduser')
    # if user:
        # del request.session['enduser']
    request.session.clear()
    request.session.flush()

    try:
        token = user['uidtoken'] if user else request.META.get('HTTP_UIDTOKEN')
        if token:
            user = EndUserExt.objects.get(token=token)
            user.token = renderutil.random_str(36)
            user.sms_code = ''
            user.save()

    except ObjectDoesNotExist:
        pass

    return renderutil.report_ok()


def create_or_update_wx_user(request, wx_user, user):
    if not user or not wx_user or not wx_user.get('openid'):
        return

    # client = renderutil.get_client(request)
    EndUserExt.objects.update_or_create(ex_id=wx_user.get('openid'),
                                        ex_id_type=EndUserExt.ID_TYPE_WECHAT_OPENID,
                                        defaults={'uid': user.uid})


# def verify_code(request):
#     """
#     验证用户手机号和短信验证码（测试时不发送真实短信，验证码一律为“666666”）
#     :param request:
#     - mobile, 手机号
#     - code，短信验证码
#     :return:
#     验证成功，返回{"mobile": 手机号, "name": 姓名（可能为空）, "uidtoken": 令牌}
#     验证失败，返回{"error": msg}
#
#     eg. <a href='/tms-api/verify_code?mobile=12345678901&code=666666'>查看样例</a>
#     """
#     mobile = req.get("mobile")
#     code = req.get("code")
#     if not code:
#         return renderutil.report_error("验证码不能为空")
#
#     if not mobile:
#         return renderutil.report_error("对不起，手机号码不能为空")
#
#     if not is_valid_mobile(mobile):
#         return renderutil.report_error("对不起，无效的手机号码")
#
#     try:
#         user = EndUserExt.objects.get(mobile=mobile)
#     except EndUserExt.DoesNotExist:
#         return renderutil.report_error("验证失败", renderutil.LOGIN_REQUIRED_ERR)
#     else:
#         if user.status != EndUser.STATUS_ACTIVE:
#             return renderutil.report_error("对不起，该手机号无效！", renderutil.LOGIN_REQUIRED_ERR)
#
#         if settings.USE_TZ:
#             second_delta = timezone.localtime(timezone.now()) - timezone.localtime(user.update_time)
#         else:
#             second_delta = datetime.datetime.now() - user.update_time
#         # TODO: 存在恶意阻止特定手机号验证的风险, 待修复
#         if not user.sms_code or second_delta.total_seconds() > settings.SMS_CODE_EXPIRY:
#             return renderutil.report_error("验证码已失效，请重新验证", renderutil.LOGIN_REQUIRED_ERR)
#
#         if user.sms_code != code[:6]:
#             cnt = 0 if len(user.sms_code) <= 6 else int(user.sms_code[-1])
#             cnt += 1
#             if cnt >= 3:
#                 user.sms_code = ''  # 安全起见，需要重新发送短信
#             else:
#                 user.sms_code = "%s#%s" % (user.sms_code[:6], cnt)
#             user.save()
#             return renderutil.report_error("验证失败，请重新验证", renderutil.LOGIN_REQUIRED_ERR)
#
#         if not user.is_verified:
#             user.is_verified = True
#
#         # reset the code to avoid duplicate verification
#         user.sms_code = ''
#         user.token = renderutil.random_str(36)  # generate a token for further validation
#         client = renderutil.get_client(request)
#         if not user.register_ip:
#             user.register_ip = client.get('ip')
#
#         user.last_login = timezone.now() if settings.USE_TZ else datetime.datetime.now()
#         user.last_login_ip = client.get('ip')
#         user.last_login_device = client.get('http_agent', '')[:100] if client.get('http_agent') else ''
#         user.save()
#
#         wx_user = request.session.get('wx_user') or {}
#         log.debug("wx_user in verify_code: %s" % json_encode(wx_user))
#         request.session['enduser'] = {"mobile": mobile,
#                                       "name": user.name if user.name else "",
#                                       # "nick_name": wx_user.get('nick_name') or user.name,
#                                       # "avatar": wx_user.get('headimgurl'),
#                                       "uidtoken": user.token,
#                                       "uid": user.id}
#         openid = wx_user.get('openid')
#         if openid:
#             request.session['enduser']['openid'] = openid
#             try:
#                 ex_user = EndUserThirdParty.objects.get(external_uid=openid)
#                 log.debug("Found existing wx_user: %s" % ex_user)
#             except EndUserThirdParty.DoesNotExist:
#                 log.debug("Create new wx_user: %s" % openid)
#                 ex_user = EndUserThirdParty(external_uid=openid,
#                                             type=EndUserThirdParty.THIRD_PARTY_WEIXIN)
#
#             ex_user.uid = user.id
#             ex_user.last_login = user.last_login
#             ex_user.last_login_ip = client.get('ip')
#             ex_user.last_login_device = user.last_login_device
#             ex_user.save()
#
#         return renderutil.json_response(request.session['enduser'])


# def send_code(request):
#     """
#     发送短信给用户，测试阶段不发送真实短信，所有涉及短信的数据都是666666
#     :param request:
#     - mobile, 用户手机号，同一号码两次发送验证码之间至少需要间隔60秒，每个手机号码每日少于 10 条
#     :return:
#     {"result": "ok"} 或者 {"error": error_msg}
#
#     eg. <a href='/tms-api/send_code?mobile=12345678901'>查看样例</a>
#     """
#     mobile = req.get("mobile")
#     if not mobile or not is_valid_mobile(mobile):
#         return renderutil.report_error("对不起，无效的手机号码")
#
#     # query user, if not exists then create a new one
#     try:
#         user = EndUserExt.objects.get(mobile=mobile)  # check if user exists
#     except EndUserExt.DoesNotExist:
#         # save a new user
#         user = EndUserExt(mobile=mobile)
#         user.save()
#
#     # reset sms_code and token
#     # "666666" for testing only, do not send a real sms if FAKE_SMS
#     code = '666666' if settings.FAKE_SMS else renderutil.random_num(6)
#     user.sms_code = code
#     user.save()
#
#     # ensure user DO NOT send a sms with interval less than 60 seconds
#     try:
#         from log.models import UserSmsLog
#         log = UserSmsLog.objects.filter(mobile=mobile).latest('id')
#         if settings.USE_TZ:
#             delta = timezone.localtime(timezone.now()) - timezone.localtime(log.send_time)
#         else:
#             delta = datetime.datetime.now() - log.send_time
#
#         if not settings.FAKE_SMS and delta.total_seconds() < 60:
#             return renderutil.report_error("对不起，发送短信过于频繁。请稍后再试")
#         # UserSmsLog.objects.filter(mobile=mobile)
#     except UserSmsLog.DoesNotExist:
#         pass
#
#     # send sms, save sms send log
#     from basedata.views import send_sms
#     result = send_sms(mobile, sms.SMS_TEMPLATE_VERIFICATION_CODE % code)
#
#     if result is True:
#         return renderutil.report_ok()
#     else:
#         return renderutil.report_error("发送短信失败: %s" % result and result.get('error'))


def me(request):
    """
    获取用户个人信息
    :param request:
        - [hotel_flag], 可选，标记用户当前酒店，如布丁，汉庭，如家等
        - [outlet_flag], 可选，标记用户当前门店，如布丁苏州XX店等
    :return:
    """
    req = request.POST if 'POST' == request.method else request.GET
    if req.get('hotel_flag'):
        request.session['hotel_flag'] = req.get('hotel_flag')
    if req.get('outlet_flag'):
        request.session['outlet_flag'] = req.get('outlet_flag')

    #if 'micromessenger' in request.META.get('HTTP_USER_AGENT', '').strip().lower():
    #    pass

    user = validate_token(request) or {}
    logger.debug("me: %s | %s" % (user, req.get('wx_user')))
    return renderutil.json_response(user)


def validate_token(request):
    """
    验证令牌
    先尝试验证session，如果session中有用户信息，则直接返回用户对象
    如果没有session记录，再验证令牌，令牌有效则返回用户对象
    :param request:
    在请求header中包含uidtoken
    :return:
    验证成功，返回用户对象
    失败则返回False
    """
    # log.debug("validate token META: %s" % request.META)
    # print request.META
    user = request.session.get('enduser')
    logger.debug("user in session(token validation): %s" % user)
    if user and user.get('mobile'):
        is_login = True
    else:
        is_login = False
        client = renderutil.get_client(request)
        token = request.COOKIES.get('uidtoken') or request.META.get('HTTP_UIDTOKEN')
        logger.debug("validate user via token: %s" % token)
        end_user = None
        if token:
            try:
                end_user = EndUserExt.objects.get(token=token, status=EndUserExt.STATUS_ACTIVE)
                is_login = True
            except ObjectDoesNotExist:
                logger.debug("validate user via token FAILED: %s" % token)
                pass
            else:
                if end_user.last_login:
                    if settings.USE_TZ:
                        delta = timezone.localtime(timezone.now()) - timezone.localtime(end_user.last_login)
                    else:
                        delta = datetime.datetime.now() - end_user.last_login

                    if delta.total_seconds() / 3600 > settings.TOKEN_EXPIRY:
                        is_login = False
                        logger.debug("validate user via token EXIPRED: %s" % token)

    logger.debug("user validation result: %s" % user)
    return user if is_login else False


def iplookup(request):
    """
    根据ip获取定位信息
    :param request:
        - js | json, 指定返回格式，默认为json, 参数名可以为js或json，无需值
    :return:
    """
    req = request.POST if 'POST' == request.method else request.GET
    client = renderutil.get_client(request)
    is_js = 'js' in req
    res = ''
    if client.get('ip'):
        cache_key = '%s:%s' % (client.get('ip'), 'js' if is_js else 'json')
        res = cache.get(cache_key)
        if not res:
            location = geoutil.get_location_by_ip(client.get('ip'))
            res = ("var window.ip_pos = %s" % location) if is_js else location
            cache.set(cache_key, res, 60 * 30)

    return renderutil.js_response(res) if is_js else renderutil.json_response(res)


def validate_user_and_supplier(request):
    req = request.POST if 'POST' == request.method else request.GET
    as_supplier = 'supplier_id' in req
    supplier_id = req.get('supplier_id')
    try:
        if as_supplier:
            user = get_user_by_uid(request, as_internal=True)
        else:
            user = get_user_by_uid(request)

        if not user:
            raise ValueError(u'无效的用户账号！')

        uid = user.uid
        if as_supplier:
            if not user.internal_user:
                raise ValueError('请先绑定管理账号！')

            if not supplier_id or not supplier_id.isdigit():
                raise ValueError('无效的供货商ID')
            from vendor.models import SupplierManager, SupplierSalesIncome
            if not SupplierManager.objects.filter(supplier_id=supplier_id, user=user.internal_user).exists():
                raise ValueError('访问未授权，不是该供货商[id:%s]的管理员' % supplier_id)

            uid = 'SUP-%s' % supplier_id.zfill(12)

        return uid, supplier_id, None
    except ValueError, e:
        return None, supplier_id, e.message


def query_accounts(request):
    """
    获取用户资金流水
    :param request(GET):
        - uid | uid, supplier_id
            提供supplier_id参数(供货商ID)时，uid用于验证该用户是否有权查看
            否则，仅提供用户uid，则只查询用户的资金流水
        - [account_no], 可选, 流水号，多个流水号可用英文逗号分隔
        - [is_income], 可选，1为是，0为否，不提供或其它值表示所有
        - [type], 可选，账目类别，包括：
            'bonus' - 奖励
            'charge' - 充值
            'deduct' - 扣除,
            'expense' - 消费支出
            'penalty' - 罚款
            'reward' - 回佣
            'roll-in' - 转入
            'roll-out' - 转出
            'sales'  - 销售收入
            'withdraw' - 提现
            'deduct', - 扣除, 已收入，因故扣除
            'return', - 返还，已扣款，因故返还
            'other' - 其它
        - [since], 可选，日期时间型，入账时间下限（不包含）
        - [before], 可选，日期时间型，入账时间上限（不包含）
        - [pos], 可选，获取的结果可能存在多页时，给定开始选取的位置，默认为0
        - [size], 可选，获取的结果可能存在多页时，确定返回每页记录数，默认为10
    :return:
        成功返回账户流水列表，如：
            [
                {
                    uid: "afebfaa8457d4e0aaeb1b7a317d9493e",
                    extra_data: "D160409PRFDSA",
                    extra_type: "basedata.Order",
                    figure: "10.00",  (入账金额，只有正值)
                    account_desc: "订单收益",
                    is_income: true,  （是否收入，true为收入, false为支出）
                    create_time: "2016-04-13 22:20:52",
                    type: "reward",
                    type_display: "回佣",
                    account_no: "A123456789",
                    unfrozen_at: "2016-08-01 16:33:48",  (解冻时间，仅当该笔资金未解冻时有此项)
                }
            ]
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/query_accounts">查看样例</a>
    """
    uid, supplier_id, err = validate_user_and_supplier(request)
    if err:
        return renderutil.report_error(err)

    req = request.POST if 'POST' == request.method else request.GET
    records = UserAccountBook.objects.filter(uid=uid)
    if req.get('account_no'):
        records = records.filter(account_no__in=req.get('account_no').split(','))
    is_income = req.get('is_income')
    if is_income in [0, '0']:
        records = records.filter(is_income=False)
    elif is_income in [1, '1']:
        records = records.filter(is_income=True)

    # [since], 入账时间下限（不包含）
    if req.get('since'):
        records = records.filter(create_time__gt=req.get('since'))
    # [before], 入账时间上限（不包含）
    if req.get('before'):
        records = records.filter(create_time__lt=req.get('before'))

    start_pos = int(req.get('pos', 0))
    page_size = int(req.get('size', 10))
    # page_size = page_size if 2 < page_size < 20 else 20 if page_size >= 20 else 2
    if req.get('page'):
        start_pos = int(req.get('page')) * page_size

    records = records[start_pos:start_pos + page_size]
    res = []
    # delta = timedelta(days=AppSetting.get('app.reward_deferred_days', REWARD_DEFERRED_DAYS))
    # unfrozen = now(settings.USE_TZ) - delta
    cur_time = now(settings.USE_TZ)
    # 收益记录，有一定的冻结时间
    for r in records:
        acct_item = r.to_dict()
        if r.effective_time and r.effective_time > cur_time:
            acct_item['unfrozen_at'] = r.effective_time

        res.append(acct_item)

    return renderutil.json_response(res)


def bd_query_accounts(request):
    """
    获取店铺资金流水
    :param request(GET):
        - store_code, 店铺code
        - [account_no], 可选, 流水号，多个流水号可用英文逗号分隔
        - [is_income], 可选，1为是，0为否，不提供或其它值表示所有
        - [type], 可选，账目类别，包括：
            'bonus' - 奖励
            'charge' - 充值
            'deduct' - 扣除,
            'expense' - 消费支出
            'penalty' - 罚款
            'reward' - 回佣
            'roll-in' - 转入
            'roll-out' - 转出
            'sales'  - 销售收入
            'withdraw' - 提现
            'deduct', - 扣除, 已收入，因故扣除
            'return', - 返还，已扣款，因故返还
            'other' - 其它
        - [since], 可选，日期时间型，入账时间下限（不包含）
        - [before], 可选，日期时间型，入账时间上限（不包含）
        - [pos], 可选，获取的结果可能存在多页时，给定开始选取的位置，默认为0
        - [size], 可选，获取的结果可能存在多页时，确定返回每页记录数，默认为10
    :return:
        成功返回账户流水列表，如：
            [
                {
                    uid: "afebfaa8457d4e0aaeb1b7a317d9493e",
                    extra_data: "D160409PRFDSA",
                    extra_type: "basedata.Order",
                    figure: "10.00",  (入账金额，只有正值)
                    account_desc: "订单收益",
                    is_income: true,  （是否收入，true为收入, false为支出）
                    create_time: "2016-04-13 22:20:52",
                    type: "reward",
                    type_display: "回佣",
                    account_no: "A123456789",
                    unfrozen_at: "2016-08-01 16:33:48",  (解冻时间，仅当该笔资金未解冻时有此项)
                }
            ]
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/query_accounts">查看样例</a>
    """
    # uid, supplier_id, err = validate_user_and_supplier(request)
    # if err:
    #     return renderutil.report_error(err)

    req = request.POST if 'POST' == request.method else request.GET

    store_code = req.get('store_code')
    if not store_code:
        return renderutil.report_error(u'缺少参数：store_code')
    # try:
    #     if SaleShop.objects.filter(code=code).exists():

    records = UserAccountBook.objects.filter(uid=store_code)
    if req.get('account_no'):
        records = records.filter(account_no__in=req.get('account_no').split(','))
    is_income = req.get('is_income')
    if is_income in [0, '0']:
        records = records.filter(is_income=False)
    elif is_income in [1, '1']:
        records = records.filter(is_income=True)

    # [since], 入账时间下限（不包含）
    if req.get('since'):
        records = records.filter(create_time__gt=req.get('since'))
    # [before], 入账时间上限（不包含）
    if req.get('before'):
        records = records.filter(create_time__lt=req.get('before'))

    start_pos = int(req.get('pos', 0))
    page_size = int(req.get('size', 10))
    # page_size = page_size if 2 < page_size < 20 else 20 if page_size >= 20 else 2
    if req.get('page'):
        start_pos = int(req.get('page')) * page_size

    records = records[start_pos:start_pos + page_size]
    res = []
    # delta = timedelta(days=AppSetting.get('app.reward_deferred_days', REWARD_DEFERRED_DAYS))
    # unfrozen = now(settings.USE_TZ) - delta
    cur_time = now(settings.USE_TZ)
    # 收益记录，有一定的冻结时间
    for r in records:
        acct_item = r.to_dict()
        if r.effective_time and r.effective_time > cur_time:
            acct_item['unfrozen_at'] = r.effective_time

        res.append(acct_item)

    return renderutil.json_response(res)


def get_accounts_summary(request):
    """
    获取用户资金账户总额 （要查询供应商的账户信息，请使用get_supplier_accounts_summary）
    :param request(GET):
        - uid, 必填，用户uid
        - [org_uid]，资金账号所属的企业用户uid，只有已绑定的管理账号才有权访问
    :return:
        成功返回收益记录列表，如：
        {
            total: "569.00",   (账户总额，含已申请提现但尚未到账的部分)
            income: "1169.00", （收入）
            deduct: "0",        (已收入，因故又被扣除的部分)
            expense: 600       （支出）
            withdraw_tbd: "400.00",  （尚未处理的申请提现金额，即冻结部分）
            reward_frozen: "100.00",  (收益已入账，但暂时不可使用部分）
            available: "69.00"       （账户中可使用金额，及总余额扣除冻结和已入账暂不可使用部分）
            uid: "7ad5b2c101cb4944ae053b6b275e91a6",
        }
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/get_accounts_summary">查看样例</a>
    """
    user, account_uid, err = validate_user_priviledge(request)
    if err:
        return report_error(err)

    result = UserAccountBook.get_account_summary(account_uid)
    return renderutil.json_response(result)


def bd_get_store_summary(request):
    """
    获取店铺资金账户总额 （要查询供应商的账户信息，请使用get_supplier_accounts_summary）
    :param request(GET):
        - store_code, 必填，店铺代码，store_code
        - [uid]，店主uid，只有已绑定的店主账号才有权访问
    :return:
        成功返回收益记录列表，如：
        {
            total: "569.00",   (账户总额，含已申请提现但尚未到账的部分)
            income: "1169.00", （收入）
            deduct: "0",        (已收入，因故又被扣除的部分)
            expense: 600       （支出）
            withdraw_tbd: "400.00",  （尚未处理的申请提现金额，即冻结部分）
            reward_frozen: "100.00",  (收益已入账，但暂时不可使用部分）
            available: "69.00"       （账户中可使用金额，及总余额扣除冻结和已入账暂不可使用部分）
            store_code: "S01234567",
        }
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/bd_get_store_summary">查看样例</a>
    """
    # user, account_uid, err = validate_user_priviledge(request)
    # if err:
    #     return report_error(err)
    req = request.POST if 'POST' == request.method else request.GET
    store_code = req.get('store_code')
    if not store_code:
        return report_error('缺少参数：store_code')

    if SaleShop.objects.filter(code=store_code).exists():
        result = UserAccountBook.bd_get_store_summary(store_code)
        return renderutil.json_response(result)
    else:
        return report_error('没有找到该店铺!')


def bd_get_account_summary_all_staff(request):
    """
    获取店铺资金账户总额 （要查询供应商的账户信息，请使用get_supplier_accounts_summary）
    :param request(GET):
        - store_code, 必填，店铺代码，store_code
        - [uid]，店主uid，只有已绑定的店主账号才有权访问
    :return:
        成功返回收益记录列表，如：
        {
            total: "569.00",   (账户总额，含已申请提现但尚未到账的部分)
            income: "1169.00", （收入）
            deduct: "0",        (已收入，因故又被扣除的部分)
            expense: 600       （支出）
            withdraw_tbd: "400.00",  （尚未处理的申请提现金额，即冻结部分）
            reward_frozen: "100.00",  (收益已入账，但暂时不可使用部分）
            available: "69.00"       （账户中可使用金额，及总余额扣除冻结和已入账暂不可使用部分）
            uid: "S01234567",
        }
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/bd_get_store_summary">查看样例</a>
    """
    # user, account_uid, err = validate_user_priviledge(request)
    # if err:
    #     return report_error(err)
    req = request.POST if 'POST' == request.method else request.GET
    store_code = req.get('store_code')
    if not store_code:
        return report_error('缺少参数：store_code')

    result = []
    if SaleShop.objects.filter(code=store_code).exists():
        if ShopManagerInfo.objects.filter(shopcode=store_code).exists():
            users = ShopManagerInfo.objects.filter(shopcode=store_code,
                                                   role__in=[ShopManagerInfo.ROLE_SHOPSTORE_MANAGER,
                                                             ShopManagerInfo.ROLE_SHOPSTORE_STAFF])
            for user in users:
                result.append(UserAccountBook.get_account_summary(user.uid))
            return renderutil.json_response(result)
        else:
            return report_error('没有该店铺员工信息!')
    else:
        return report_error('没有找到该店铺!')


def get_supplier_accounts_summary(request):
    """
    获取供应商资金账户总额
    :param request(GET):
        - uid, 必填，用户uid，用于验证该用户是否有权查看
        - supplier_id, 必填，供货商ID
    :return:
        成功返回账户统计信息，如：
        {
            total: "569.00",   (账户总额，含已申请提现但尚未到账的部分)
            income: "569.00", （收入）
            deduct: "0",        (已收入，因故又被扣除的部分)
            expense: 0       （支出）
            withdraw_tbd: "500",  （尚未处理的申请提现金额，即冻结部分）
            reward_frozen: "0",  (收益已入账，但暂时不可使用部分）
            available: "69.00"       （账户中可使用金额，及总余额扣除冻结和已入账暂不可使用部分）
            uid: "SUP-supplier_id",  (供货商资金流水中，uid为"SUP-"前缀加供货商id)
        }
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/get_supplier_accounts_summary">查看样例</a>
    """
    """
                sales_income :
            {
                已取消 :{
                    status : 3,
                    total_income : "200.00"  （已取消的收入总额）
                },
                已结算 :{
                    status : 2,
                    total_income : "200.00"
                },
                待结算 :{
                    status : 1,
                    total_income : "200.00"
                },
                待确认 :{
                    status : 0,
                    total_income : "200.00"
                }
            }
    """
    user = get_user_by_uid(request, as_internal=True)
    if not user:
        return renderutil.report_error(u'无效的用户账号！')
    elif not user.internal_user:
        return renderutil.report_error('请先绑定管理账号！')

    req = request.POST if 'POST' == request.method else request.GET
    supplier_id = req.get('supplier_id')
    if not supplier_id or not supplier_id.isdigit():
        return renderutil.report_error('无效的供货商ID')
    from vendor.models import SupplierManager, SupplierSalesIncome
    if not SupplierManager.objects.filter(supplier_id=supplier_id, user=user.internal_user).exists():
        return renderutil.report_error('访问未授权，不是该供货商[id:%s]的管理员' % supplier_id)

    result = UserAccountBook.get_account_summary('SUP-%s' % supplier_id.zfill(12))
    result['sales_income'] = SupplierSalesIncome.summary(supplier_id)
    return renderutil.json_response(result)


def get_capital_accounts(request):
    """
    获取用户资金账号（如已绑定的银行卡、支付宝账号等）列表
    :param request(GET):
        - uid, 必填，用户uid
        - [org_uid | supplier_id]，要解绑资金账号的企业用户uid或供应商的id，只有已绑定的管理账号才有权操作
    :return:
        成功返回账号列表，如：
        [
            {
                bank_code: "icbc",  （银行编码）
                bank_name: "爱存不存", （银行名称）
                ca_desc: "测试",    （账号描述）
                ca_name: "黄某某",    (开户名)
                ca_mobile: "13812345678",     (开户预留手机号)
                ca_no: "123456784123123"  (注：为了安全考虑，应只显示末4位)
                ca_type: "deposit",    （账号类型，如deposit-银行, alipay-支付宝）
                id: 1,
                is_default: false,  （是否默认账号）
                is_valid: false,    （是否验证有效）
                open_bank: "",      （开户银行名称）
                uid: "xxxxxxxxxxxxxxxxxxxxx",
            }
        ]
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/get_capital_accounts">查看样例</a>
    """
    user, account_uid, err = validate_user_priviledge(request)
    if err:
        return report_error(err)

    # TODO: fix 暂时未对uid传企业用户uid的情形做检查
    accounts = UserCapitalAccount.objects.filter(uid=account_uid)
    result = []
    for acct in accounts:
        res = model_to_dict(acct)
        # res['ca_no'] = "%s%s" % ("*" * 12, res['ca_no'][-4:])
        result.append(res)
    return json_response(result)


def validate_user_priviledge(request):
    """
    验证用户是否有修改指定企业用户/供应商资金账号的权限
    :param request:
    :return:
    """
    req = request.POST if 'POST' == request.method else request.GET
    as_internal = 'supplier_id' in req or 'supplier_code' in req
    user = get_user_by_uid(request, as_internal=as_internal)
    account_uid = user and user.uid
    err = None
    try:
        if not user:
            raise ValueError(u'无效的用户账号！')
        elif as_internal:
            from vendor.models import Supplier, SupplierManager, SupplierSalesIncome
            if 'supplier_id' in req:
                supplier_id = req.get('supplier_id')
            else:
                supplier_code = req.get('supplier_code')
                sup_id = Supplier.objects.filter(code=supplier_code).values_list('id', flat=True)
                if sup_id:
                    supplier_id = "%s" % sup_id[0]
                else:
                    raise ValueError('无效的供应商编码：%s' % supplier_code)

            if not SupplierManager.objects.filter(supplier_id=supplier_id, user=user.internal_user).exists():
                raise ValueError('没有操作权限！')
            account_uid = 'SUP-%s' % supplier_id.zfill(12)
        elif 'org_uid' in req:
            org = EndUserEnterprise.objects.get(uid=req.get('org_uid'))
            if org.status != EndUserEnterprise.STATUS_ACTIVE:
                raise ValueError('当前企业账号无效，请与系统管理员或客服联系' % org.uid)
            # 只有企业账号管理员可以操作
            if not EndUserRole.objects.filter(user_uid=user.uid, org_uid=org.uid,
                                              role__in=(EndUserRole.ROLE_ADMIN, EndUserRole.ROLE_SP)).exists():
                raise ValueError('没有操作权限！')
            account_uid = org.uid
    except EndUserEnterprise.DoesNotExist:
        err = '无效的企业账号！'
    except Exception, e:
        err = e.message

    return user, account_uid, err


def bind_capital_account(request):
    """
    绑定用户资金账号（如已绑定的银行卡、支付宝账号等），也可用于更新用户资金账号（ca_no相同时）
    :param request(POST):
        - uid, 必填，用户uid（如果要修改企业用户或供应商的资金账号，则该uid用于验证权限）
        - [org_uid | [supplier_id|supplier_code]]，要绑定资金账号的企业用户uid或供应商的id，只有已绑定的管理账号才有权操作
        - [ca_type], 账号类型，如：
            'wechat' - 微信钱包，默认值
            'alipay' - 支付宝
            'deposit' - 储蓄卡, 默认值
            'credit' - 信用卡
            'enterprise' - 企业账号
            'other' - 其它
        - ca_no, 账号，可能是银行卡，也可能是支付宝账号
        - ca_name, 开户名，一般是个人姓名或企业名称
        - ca_mobile, 开户预留的手机号
        - [bank_code, bank_name, open_bank]，当ca_type为deposit/credit/enterprise时必填
                bank_code: 银行编码，如"icbc"
                bank_name: 银行名称，如"工商银行"
                open_bank: 开户银行名称，如“徐家汇支行”
        - [ca_desc] 描述
        - [is_default] 是否默认， 默认值为否，1 表示是
    :return:
        成功返回{'result': 'ok', 'id': 1}，id为绑定的资金账号id
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/bind_capital_account">查看样例</a>
    """
    user, account_uid, err = validate_user_priviledge(request)
    if err:
        return report_error(err)

    ca_type = request.POST.get('ca_type', 'wechat')
    types = [t[0] for t in UserCapitalAccount.CAPITAL_ACCOUNT_TYPES]
    if not ca_type or ca_type not in types:
        return report_error(u'无效的账号类型')
    ca_no = request.POST.get('ca_no').strip()
    if not ca_no:
        return report_error(u'缺少资金卡号或账号参数')
    ca_name = request.POST.get('ca_name').strip()
    if not ca_name:
        return report_error('缺少开户名称')
    ca_mobile = request.POST.get('ca_mobile').strip()
    if not ca_mobile:
        return report_error('缺少开户手机号')

    defaults = {"ca_type": ca_type, 'ca_name': ca_name, 'ca_mobile': ca_mobile}
    if ca_type in ['deposit', 'credit', 'enterprise']:
        err = []
        if not request.POST.get('bank_code'):
            err.append('缺少银行编码')
        if not request.POST.get('bank_name'):
            err.append('缺少银行名称')
        if not request.POST.get('open_bank'):
            err.append('缺少开户行名称')
        if len(err) > 0:
            return report_error(','.join(err))

    defaults['bank_code'] = request.POST.get('bank_code').strip()
    defaults['bank_name'] = request.POST.get('bank_name').strip()
    defaults['open_bank'] = request.POST.get('open_bank').strip()

    if request.POST.get('ca_desc'):
        defaults['ca_desc'] = request.POST.get('ca_desc').strip()
    if request.POST.get('ca_desc'):
        defaults['ca_desc'] = request.POST.get('ca_desc').strip()
    if '1' == request.POST.get('is_default'):
        defaults['is_default'] = True
    try:
        account, created = UserCapitalAccount.objects.update_or_create(uid=account_uid,
                                                                       ca_no=ca_no,
                                                                       defaults=defaults)
        return report_ok({'id': account.pk})
    except IntegrityError:
        return report_error('账号[%s]已绑定' % request.POST.get('ca_no'))


def unbind_capital_account(request):
    """
    解绑用户资金账号
    :param request(POST):
        - uid, 必填，用户uid
        - account_id, 账号id，通过get_capital_accounts接口获取的id
        - [org_uid | supplier_id]，要解绑资金账号的企业用户uid或供应商的id，只有已绑定的管理账号才有权操作
    :return:
        成功返回{'result': 'ok'}
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/unbind_capital_account">查看样例</a>
    """
    user, account_uid, err = validate_user_priviledge(request)
    if err:
        return report_error(err)

    if not request.POST.get('account_id'):
        return report_error(u'缺少账号id参数')

    try:
        UserCapitalAccount.objects.get(uid=account_uid,
                                       pk=request.POST.get('account_id')).delete()
        return report_ok()
    except UserCapitalAccount.DoesNotExist:
        return report_error(u'未找到匹配的账号或无访问权限！')


def _import_account_book(excel_file):
    import xlrd
    # from basedata.models import Product
    # excel_file = "f:/twohou/pilot_products.xls"
    result = {"count": 0, "error": [], "records": []}

    try:
        book = xlrd.open_workbook(excel_file)
        data_sheet = book.sheet_by_index(0)

        # reverse data sheet headers to above property names
        headers = data_sheet.row_values(0, 0, data_sheet.ncols)
        expected = [u'账目类别', u'用户', u'用户UID', u'入账金额', u'是否收入', u'账目说明',
                    u'交易流水号', u'关联对象类型', u'补充信息', u'创建时间']
        expected_len = len(expected)
        if headers != expected:
            raise ValueError(u'导入数据格式不对！\n期望：%s\n导入：%s' % (','.join(expected), ','.join(headers)))

        uid_set = set()
        records = {}
        # validate data
        for x in range(1, data_sheet.nrows):
            row = data_sheet.row_values(x, end_colx=expected_len)
            if not (row[0] and row[2] and row[3] and row[4] and row[5]):
                result['error'].append(u"数据不完整，必须至少包含[账目类别，用户UID，入账金额，是否收入，账目说明]：%s" %
                                       ','.join(row[0]))
                continue
            if row[0] not in ACCOUNT_TYPES_REVERT_DICT:
                result['error'].append(u'账目类别[%s]无效' % row[0])
                continue
            row[3] = _handle_money(row[3])
            row[4] = _handle_bool(row[4])
            uid_set.add(row[2])
            result['records'].append(UserAccountBook(uid=row[2],
                                                     figure=row[3],
                                                     is_income=row[4],
                                                     type=ACCOUNT_TYPES_REVERT_DICT.get(row[0]),
                                                     account_desc=row[5],
                                                     trans_no=row[6],
                                                     extra_type=row[7],
                                                     extra_data=row[8],
                                                     create_time=row[9]))

        result['count'] = len(uid_set)
        qs = EndUser.objects.filter(uid__in=uid_set)
        if qs.count() != result['count']:
            uids = [q.uid for q in qs]
            difference = uid_set.difference(uids)
            result['error'].append(u'以下用户UID无效：\n%s' % ",".join(difference))
        else:
            UserAccountBook.objects.bulk_create(result['records'])

    except Exception, e:
        logger.exception(e)
        result['error'].append(u"解析Excel失败：%s" % (e.message or e.args[1]))
        return result

    print result
    return result


def _handle_bool(f_value):
    return str(f_value).lower() in ['true', '1', 'y', 'yes', u'是']


def _handle_money(s):
    if isinstance(s, basestring):
        if s[0] == u'￥':
            s = s[1:]
        if s[-1] == u'元':
            s = s[:-1]
    return Decimal(s or 0)


def import_account_book(request):
    """
    导入资金流水数据（财务打款）
    :param request:
    :return:
        返回上传文件的绝对引用路径
    """
    template_url = 'admin/profile/useraccountbook/import_acct.html'
    if not request.user.is_superuser:
        return render_to_response(template_url, {"auth_error": u"对不起，没有操作权限！"})

    params = {}
    if request.POST.get('action') == 'confirm':  # 保存数据
        pass
    else:
        files = request.FILES.getlist('files')
        if not files or len(files) == 0:
            return render_to_response(template_url)

        cur_time = now(settings.USE_TZ)
        path = cur_time.strftime('%Y-%m-%d')
        for f in files:
            file_path = "%supload/data/%s_%s_%s" % (settings.STATIC_ROOT, path, random_str(32), f.name[-12:])
            if not os.path.abspath(file_path).startswith(ABS_STATIC_ROOT):
                # TODO: invalid path given (out of ABS_STATIC_ROOT) or file not exists, must be log for security audit
                print "Invalid file path: %s" % file_path
                continue
            file_dir, file_name = os.path.split(file_path)
            os.path.exists(file_dir) or os.makedirs(file_dir, mode=0744)

            destination = open(file_path, 'wb+')
            print file_path

            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
            try:
                params = _import_account_book(file_path)  # parse and save to DB
            except Exception, e:
                logger.exception(e)
                params = {"error": [e.message or e.args[1]]}
            break  # process single file so far
            # file_url = "%s%s" % (settings.STATIC_URL, file_path[len(settings.STATIC_ROOT):])
            # result.append(file_url)

    return render_to_response(template_url, params)

    # print jsonall.json_encode(result)
    # return json_response(result)


def deduct(request):
    """
    扣款，从资金流水中扣除，暂不验证账户余额
    :param request:
        - uid, 被扣款用户的uid
        - figure, 扣除金额，必须为正值
        - account_desc, 账目说明
        - trans_no， 支付通道支付流水
        - [extra_type], 可选，关联对象类型，默认是"basedata.Order"，表示订单（暂不接受其它值，如有其他需要请跟我联系）
        - extra_data, 用于保存额外的关联数据，比如订单号，转出账号等，根据extra_type来定，目前暂时只接受订单号
    :return:
        成功返回{"error": "", "result": "ok", "account_no": "A160608144002MPVWQYC"}， account_no为TMS流水号
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/deduct">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return report_error(u'无效的用户账号！')

    figure = request.POST.get('figure', 0)
    if Decimal(figure) <= 0:
        return report_error(u'扣除金额必须是正值')
    if not request.POST.get('account_desc'):
        return report_error(u'请提供账目说明')
    if not request.POST.get('trans_no'):
        return report_error(u'请提供支付流水')

    if not request.POST.get('extra_data'):
        return report_error(u'请提供订单号')
    try:
        account = UserAccountBook.objects.create(uid=user.uid,
                                                 figure=figure,
                                                 is_income=False,
                                                 type='deduct',
                                                 account_desc=request.POST.get('account_desc'),
                                                 trans_no=request.POST.get('trans_no'),
                                                 extra_type='basedata.Order',
                                                 extra_data=request.POST.get('extra_data'))
        return report_ok({"account_no": account.account_no})
    except Exception, e:
        logger.exception(e)
        return report_error('扣除失败：%s' % e.message)


def thanksgiving(request):
    """
    打赏，在资金流水中为指定用户添加一笔奖励
    :param request:
        - uid, 发放赏金的用户uid
        - to_uid, 被打赏用户的uid
        - figure, 打赏金额，必须为正值
        - account_desc, 账目说明或用户打赏留言，比如“来自XXX的打赏：感谢您的优质服务！”
        - trans_no， 支付通道支付流水
    :return:
        成功返回{"error": "", "result": "ok", "account_no": "A160608144002MPVWQYC"}， account_no为TMS流水号
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/thanksgiving">查看样例</a>
    """
    user = get_user_by_uid(request)
    if not user:
        return report_error(u'无效的用户账号！')

    figure = request.POST.get('figure', 0)
    if Decimal(figure) <= 0:
        return report_error(u'打赏金额必须是正值')
    if not request.POST.get('account_desc'):
        return report_error(u'请说明打赏理由')
    if not request.POST.get('trans_no'):
        return report_error(u'请提供支付流水')

    to_uid = request.POST.get('to_uid')
    if not to_uid:
        return report_error('缺少打赏对象uid')

    to_user = get_user_by_uid(request, attr='to_uid')
    if not to_user:
        return report_error(u'打赏对象无效或不存在！')
    try:
        account = UserAccountBook.objects.create(uid=to_uid,
                                                 figure=figure,
                                                 is_income=True,
                                                 type='bonus',
                                                 account_desc=request.POST.get('account_desc'),
                                                 trans_no=request.POST.get('trans_no'),
                                                 extra_type='profile.EndUser',
                                                 extra_data=user.uid)
        return report_ok({"account_no": account.account_no})
    except Exception, e:
        logger.exception(e)
        return report_error('打赏失败：%s' % e.message)


def request_withdraw(request):
    """
    用户申请提现
    :param request (POST):
        - uid | uid, supplier_id
            提供supplier_id参数(供货商ID)时，uid用于验证该用户是否有权查看
            否则，仅提供用户uid，则只查询用户的资金流水
        - [ca_type], 账号类型，如：
            'wechat' - 微信钱包，默认值
            'alipay' - 支付宝
            'deposit' - 储蓄卡, 默认值
            'credit' - 信用卡
            'enterprise' - 企业账号
            'other' - 其它
        - ca_no, 提现到目标账号，如果是银行卡，则为银行卡号，微信钱包为微信openid，支付宝为支付宝账号
            注意：除微信账号外，其它账号必须已经绑定在用户名下（见get_capital_accounts），方可提现
        - amount，提现金额，数值型，不得超过用户账户总额
        - 每日提现限制为1次，可通过系统设置app.withdraw_limit_per_day修改
    :return:
        成功返回{'result': 'ok', 'id': 1}， id为请求的id，可用于提现确认接口confirm_withdraw
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/request_withdraw">查看样例</a>
    """
    # end_user = EndUser.objects.get(uid=request.POST.get('uid'), status=EndUser.STATUS_ACTIVE)
    real_uid = request.POST.get('uid')
    uid, supplier_id, err = validate_user_and_supplier(request)
    if err:
        return renderutil.report_error(err)

    if real_uid <> uid:
        uid_type = WithdrawRequest.TYPE_SUPPLIER
    else:
        uid_type = WithdrawRequest.TYPE_PERSONAL
    from config.models import AppSetting
    limit = AppSetting.get('app.withdraw_limit_per_day', 1)  # 默认每天只能提现一次
    cur_time = now(settings.USE_TZ)
    today = datetime.date(cur_time.year, cur_time.month, cur_time.day)
    if WithdrawRequest.objects.filter(status__in=[WithdrawRequest.STATUS_DONE, WithdrawRequest.STATUS_TBD,
                                                  WithdrawRequest.STATUS_AUDITING, WithdrawRequest.STATUS_CONFIRMING,
                                                  WithdrawRequest.STATUS_CONFIRMED],
                                      uid=uid,
                                      create_time__gt=today).count() >= limit:
        return report_error(u'每日提现不得超过%s次！' % limit)

    ca_type = request.POST.get('ca_type', 'wechat')
    types = [t[0] for t in UserCapitalAccount.CAPITAL_ACCOUNT_TYPES]
    amount = Decimal(request.POST.get('amount', 0))
    if not ca_type or ca_type not in types:
        return report_error(u'无效的账号类型')
    if not request.POST.get('ca_no'):
        return report_error(u'缺少资金卡号或账号参数')
    if not amount > 0:
        return report_error(u'提现金额必须大于0')

    data = {'uid': uid,
            'ca_type': ca_type,
            'ca_no': request.POST.get('ca_no'),
            'uid_type': uid_type,
            'real_uid': real_uid}

    summary = UserAccountBook.get_account_summary(uid)
    # 可提现金额应扣除已申请提现未处理的部分，及已入账暂不可使用的收益部分
    if amount <= summary['available']:
        try:
            data['amount'] = amount
            if uid_type == WithdrawRequest.TYPE_SUPPLIER:
                data['status'] = WithdrawRequest.STATUS_AUDITING
            req = WithdrawRequest(**data)
            req.save()
            return report_ok({'id': req.pk})
        except ValueError, e:
            return report_error(e.message)
    else:
        return report_error(u'当前最大可提现金额￥%s！' % summary['available'])


def confirm_withdraw(request):
    """
    确认提现记录打款成功，仅当已自动执行提现打款操作时使用
    :param request (POST):
        - uid | uid, supplier_id
            提供supplier_id参数(供货商ID)时，uid用于验证该用户是否有权查看
            否则，仅提供用户uid，则只查询用户的资金流水
        - id, 必填，提现请求记录id，在request_withdraw接口中返回
        - trans_no，交易流水号，即第三方支付接口返回的交易号
    :return:
        成功返回{'result': 'ok', 'account_no': '}， account_no为本地资金流水号，如果流水入账未成功，则account_no可能为null
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/confirm_withdraw">查看样例</a>
    """
    uid, supplier_id, err = validate_user_and_supplier(request)
    if err:
        return renderutil.report_error(err)

    if not request.POST.get('trans_no'):
        return report_error(u'请提供交易流水号！')

    try:
        req = WithdrawRequest.objects.get(id=request.POST.get('id'))
        # if req.uid != req.real_uid:
        #     req.uid = req.real_uid
        # if supplier_id:
        #     # if supplier_id != req.uid:
        #     #     return report_error(u'非当前用户的提现申请，无法操作')
        #     if req.real_uid != uid:
        #         return report_error(u'非当前供应商的提现申请，无法操作')
        # elif req.uid != uid:
        #     return report_error(u'非当前用户的提现申请，无法操作')
        if req.status not in [WithdrawRequest.STATUS_TBD, WithdrawRequest.STATUS_CONFIRMED]:
            # if req.status != WithdrawRequest.STATUS_CONFIRMED:
            return report_error(u'该提现申请已被处理，无法确认')
        else:
            account_no = req.confirm(trans_no=request.POST.get('trans_no'))
            return report_ok(data={'account_no': account_no})
    except WithdrawRequest.DoesNotExist:
        return report_error(u'找不到提现申请记录')


def query_withdraw_request(request):
    """
    查询用户提现申请
    :param request(GET):
        - uid | uid, supplier_id
            提供supplier_id参数(供货商ID)时，uid用于验证该用户是否有权查看
            否则，仅提供用户uid，则只查询用户的资金流水
        - [pos], 可选，起始偏移量，默认为0
        - [size]，可选，一次获取多少条数据，默认为10，取值范围2~20
        - [status]，可选，如下：
             0 - 处理中
             1 - 完成
             2 - 提现失败
             3 - 待审核
             4 - 待确认
             5 - 已确认
        - [id], 可选，提现申请ID

    :return:
        成功返回提现申请列表，按时间逆序排列（最新的在前），如下：
        [
            {
                account_no: "A160504232510BWKTSCH"  （TMS资金流水号）
                amount: "100.00",   （申请提现金额）
                ca_no: "7ad5b2c101cb4944ae053b6b275e91a6", （提现账户，如果是银行卡，则为银行卡号，微信钱包，则为微信openid，支付宝为支付宝账号）
                ca_type: "wechat",  （提现账户类别）
                create_time: "2016-05-04 23:20:54",  （申请时间）
                id: 11,
                real_uid: "7ad5b2c101cb4944ae053b6b275e91a6",  （用户uid）
                result: null,       （提现结果描述）
                status: 1,  （状态）
                uid: "7ad5b2c101cb4944ae053b6b275e91a6",  （用户uid）
                uid_type: 0, 1, 2    个人，供应商，其他
            },
        ]
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/query_withdraw_request">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET

    if req.get('id'):
        try:
            records = WithdrawRequest.objects.get(id=req.get('id'))
        except WithdrawRequest.DoesNotExist:
            return report_error(u'找不到提现申请记录')
        return json_response(records)

    if 'all' == req.get('uid'):
        records = WithdrawRequest.objects.all()
    else:
        uid, supplier_id, err = validate_user_and_supplier(request)
        if err:
            return renderutil.report_error(err)

        records = WithdrawRequest.objects.filter(uid=uid)

    if req.get('status') in ['0', '1', '2', '3', '4', '5']:
        records = records.filter(status=req.get('status'))

    start_pos = int(req.get('pos', 0))
    page_size = int(req.get('size', 10))
    # page_size = page_size if 2 < page_size < 20 else 20 if page_size >= 20 else 2
    if req.get('page'):
        start_pos = int(req.get('page')) * page_size
    records = records[start_pos:start_pos+page_size]

    return json_response(records)


def result_withdraw(request):
    """
    确认提现记录打款成功，仅当已自动执行提现打款操作时使用
    :param request (POST):
        - uid | uid, supplier_id
            提供supplier_id参数(供货商ID)时，uid用于验证该用户是否有权查看
            否则，仅提供用户uid，则只查询用户的资金流水
        - id, 必填，提现请求记录id，在request_withdraw接口中返回
        - result, 信息内容
    :return:
        成功返回{'result': 'ok'}，ok
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/confirm_withdraw">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    uid, supplier_id, err = validate_user_and_supplier(request)
    if err:
        return renderutil.report_error(err)

    if not req.get('id'):
        return report_error(u'请提供提现id号！')

    try:
        res = WithdrawRequest.objects.get(id=req.get('id'))
        if res.uid != uid:
            return report_error(u'非当前用户的提现申请，无法操作')
        # elif req.status != WithdrawRequest.STATUS_TBD:
        #     return report_error(u'该提现申请已被处理，无法确认')
        else:
            res.result = req.get('result')
            res.save()
            return report_ok(data={'result': 'ok'})
    except WithdrawRequest.DoesNotExist:
        return report_error(u'找不到提现申请记录')


def result_audit_withdraw(request):
    """
    提现申请审核通过
    :param request (POST):
        - uid | uid, supplier_id
            提供supplier_id参数(供货商ID)时，uid用于验证该用户是否有权查看
            否则，仅提供用户uid，则只查询用户的资金流水
        - id, 必填，提现请求记录id，在request_withdraw接口中返回
        - result, 信息内容
    :return:
        成功返回{'result': 'ok'}，ok
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/confirm_withdraw">查看样例</a>
    """
    req = request.POST if 'POST' == request.method else request.GET
    # uid, supplier_id, err = validate_user_and_supplier(request)
    # if err:
    #     return renderutil.report_error(err)

    if not req.get('id'):
        return report_error(u'请提供提现id号！')

    try:
        res = WithdrawRequest.objects.get(id=req.get('id'))
        # if res.uid != uid:
        #     return report_error(u'非当前用户的提现申请，无法操作')
        # # elif req.status != WithdrawRequest.STATUS_TBD:
        # #     return report_error(u'该提现申请已被处理，无法确认')
        # else:
        res.status = WithdrawRequest.STATUS_CONFIRMING
        res.process_time = now(settings.USE_TZ)
        res.save()
        return report_ok(data={'result': 'ok'})
    except WithdrawRequest.DoesNotExist:
        return report_error(u'找不到提现申请记录')
