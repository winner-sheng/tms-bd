# -*- coding: utf-8 -*-

from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
# from django.db.transaction import atomic

from .models import UserPayLog, WechatMsgLog, UserMailLog
from util.renderutil import *
from tms import settings
from django.db import connection
from django.utils.encoding import force_text
from django.contrib.admin.models import LogEntry, CHANGE


def get_content_type_for_model(obj):
    # Since this module gets imported in the application's root package,
    # it cannot import models from other applications at the module level.
    from django.contrib.contenttypes.models import ContentType
    return ContentType.objects.get_for_model(obj, for_concrete_model=False)


def log_change(user_id, obj, message, flag=CHANGE):
        LogEntry.objects.log_action(
            user_id=user_id,
            content_type_id=get_content_type_for_model(obj).pk,
            object_id=obj.pk,
            object_repr=force_text(obj),
            action_flag=flag,
            change_message=message
        )


@login_required
def export_paylog(request):
    """
    导出支付日志列表
    :param request:
        - ids, PayLog的id列表
        - [format]，输出格式
    :return:
    """
    if not request.user.is_superuser and not request.user.is_staff:
        return report_error("对不起，访问未授权！")

    ids = request.REQUEST.get("ids")
    if not ids:
        return report_error('参数信息不完整')
    if ids == 'all':
        if not request.user.is_superuser:
            return report_error("对不起，访问未授权！")
        paylog = UserPayLog.objects.all()
    elif ids == 'select_across':  # across selected in one page
        paylog = UserPayLog.objects.filter(id__in=request.session.get('selected_for_export', []))
        del request.session['selected_for_export']
    else:
        id_list = ids.split(',')
        paylog = UserPayLog.objects.filter(id__in=id_list)

    output_format = request.REQUEST.get('format', 'csv')  # 默认导出csv格式
    if output_format == 'json':
        return json_response([model_to_dict(p_log) for p_log in paylog])
    else:
        data = [[u"支付码", u"是否退款", u"订单编号", u"用户手机号", u"支付方式",
                 u"支付总额", u"支付时间", u"已确认"]]
        for p_log in paylog:
            data.append([p_log.pay_code,
                         "Yes" if p_log.is_refund else "No",
                         p_log.order_no,
                         p_log.uid,
                         p_log.get_pay_type_display(),
                         p_log.pay_amount,
                         render_date(p_log.pay_time),
                         "Yes" if p_log.is_confirmed else "No"])
        file_name = "paylog_%s.csv" % datetime.now().strftime('%y%m%d')
        return export_csv(file_name, data)


def wechat_to(request):
    """
    向指定用户发送微信消息（注意：只是将发送请求放入队列，异步发送）
    :param request(POST):
        - uid | open_id, 收件人uid | 微信open_id，二选一，如有多个用户，可用英文逗号分隔
        - subject, 主题
        - body, 正文，JSON格式数据
        - [business_code]， 可选，业务代码
    :return:
        成功返回{"result": "ok", "count": 1}  count为成功加入队列的消息数量
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/wechat_to">查看样例</a>
    """
    uid = request.POST.get('uid')
    open_id = request.POST.get('open_id')
    try:
        count = WechatMsgLog.put_in_queue(uid, open_id, subject=request.POST.get('subject'), body=request.POST.get('body'))
        return report_ok({'count': count})
    except ValueError, e:
        return report_error(e.message)


def email_to(request):
    """
    向指定用户发送邮件消息（注意：只是将发送请求放入队列，异步发送）
    :param request(POST):
        - mail_to, 收件人email，如有多个用户，可用英文逗号分隔
        - subject, 主题
        - body, 正文，JSON格式数据
        - [mail_from], 发件人email，默认为oms@sh-anze.com
    :return:
        成功返回{"result": "ok", 'id': 123}, id为邮件队列编号
        失败返回错误消息{"error": msg}

    eg. <a href="/tms-api/email_to">查看样例</a>
    """
    users = []
    mail_to = request.POST.get('mail_to')
    if not mail_to:
        return report_error('缺少有效的uid或open_id参数！')
    else:
        mails = mail_to.split(',')

    subject = request.POST.get('subject')
    body = request.POST.get('body')
    if not subject or not body:
        return report_error('subject及body参数不能为空！')

    log_id = UserMailLog.put_in_queue(mail_to=mails, subject=subject, body=body)
    return json_response({'result': 'ok', 'id': log_id})


def query_wechat_msg(request):
    """
    查询未发送的微信消息，交付发送任务处理
    :param request(GET:
        - [size], 默认为100
        - [business_code]， 可选，业务代码
        - [max_retries], 可选，最大尝试次数，忽略已经超过指定尝试次数的消息
            注意：第一次获取的时候为0
    :return:
        [
            {
                body: "body",
                retries: 4,  (尝试发送次数)
                uid: "uid",
                open_id: "oid1",
                create_time: "2016-04-15 14:37:32",
                id: 1,
                subject: "subject"
            },
        ]
    eg. <a href="/tms-api/query_wechat_msg">查看样例</a>
    """
    from config.models import AppSetting
    time_threshold = now(settings.USE_TZ) - \
                     timedelta(minutes=(AppSetting.get('app.wechat_message_sending_out') or 10))
    sender = "%s%s" % (day_str(str_format="%y%m%d%H%M%S"), random_code(6))

    cursor = connection.cursor()
    sql = 'update log_wechatmsglog set retries = retries + 1, sender = %s, claim_time=now() ' \
          'where is_sent = 0 and (claim_time is null or claim_time < %s) '
    params = [sender, time_threshold]
    if request.REQUEST.get('business_code'):
        sql = "%s and %s" % (sql, 'business_code=%s')
        params.append(request.REQUEST.get('business_code'))
    if request.REQUEST.get('max_retries'):
        sql = "%s and %s" % (sql, 'retries=%s')
        params.append(request.REQUEST.get('max_retries'))

    size = int(request.REQUEST.get('size', 100))
    sql += ' limit %s'
    params.append(size)
    rows = cursor.execute(sql, params)
    print rows, ' rows affected'
    cursor.close()
    # 更新后再获取
    logs = WechatMsgLog.objects.filter(sender=sender).values('id', 'uid', 'open_id', 'subject', 'body', 'create_time', 'retries')
    return json_response(logs)


def mark_wechat_msg(request):
    """
    标记微信消息为已发送
    :param request(POST):
        - id: 微信消息id，通过query_wechat_msg接口获取，多条消息用英文逗号分隔
    :return:
        成功返回
            {'result': 'ok', 'rows': 1}
            rows表示标记成功记录数
        失败返回
            {"error": msg}

    eg. <a href="/tms-api/mark_wechat_msg">查看样例</a>
    """
    ids = request.POST.get('id', '')
    if not ids:
        return report_error('缺少id参数！')

    ids = ids.split(',')
    rows = WechatMsgLog.objects.filter(id__in=ids).update(is_send=True)
    return json_response({'result': 'ok', 'rows': rows})