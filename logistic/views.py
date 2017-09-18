# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import simplejson

from .models import ExpressSender, ExpressTemplate

from util import renderutil
from util import jsonall
from util.renderutil import logger

@login_required
def print_express(request):
    from vendor.models import SupplierManager
    from basedata.models import Order
    ids = request.REQUEST.get("ids")
    if not ids:
        return renderutil.report_error('参数信息不完整，缺少ids')
    id_list = ids.split(',')
    orders = Order.objects.filter(order_no__in=id_list)
    templates = []
    try:
        templates = ExpressTemplate.objects.filter(Q(create_by=request.user.id)
                                                   | Q(type=ExpressTemplate.TYPE_PUBLIC))
        for tmpl in templates:
            tmpl.template = simplejson.loads(tmpl.template)

    except ExpressTemplate.ObjectDoesNotExist:
        pass

    senders = ExpressSender.objects.all()
    if not request.user.is_superuser:
        suppliers = SupplierManager.objects.filter(user=request.user)
        senders = ExpressSender.objects.filter(supplier__in=[supplier.supplier.id for supplier in suppliers])

    return render_to_response('admin/logistic/print_express.html',
                              {'orders': jsonall.json_encode(orders), 'ids': ids,
                               'sender': jsonall.json_encode(senders),
                               'templates': jsonall.json_encode(templates)})


@login_required
def print_invoice(request):
    from basedata.models import Order
    ids = request.REQUEST.get("ids")
    if not ids:
        return renderutil.report_error('参数信息不完整')
    id_list = ids.split(',')
    orders = Order.objects.filter(order_no__in=id_list)
    for order in orders:
        order.sub_items = order.items.all()

    return render_to_response('admin/logistic/print_invoice.html', {'orders': orders, 'ids': ids})


@login_required
def get_express_template(request):
    """
    获取快递单模板
    :param request:
    :return: Json格式的快递单模板信息
    """
    try:
        if 'id' in request.REQUEST:  # if id given, return specific template in array, with single record
            template_id = request.REQUEST.get('id')
            template = ExpressTemplate.objects.get(id=template_id)
            # superuser and staff has access to all templates
            if not request.user.is_superuser:
                if template.type != ExpressTemplate.TYPE_PUBLIC \
                        and template.create_by != request.user.id:
                    return renderutil.report_error('对不起，您没有访问权限。')
            templates = [template]
        else:
            templates = ExpressTemplate.objects.filter(Q(create_by=request.user.id)
                                                       | Q(type=ExpressTemplate.TYPE_PUBLIC))

        return renderutil.json_response(templates)
    except ExpressTemplate.DoesNotExist:
        return renderutil.report_error('对不起，没有找到模板数据。')


@login_required
def set_express_template(request):
    """
    设置快递单模板
    :param request:
    :return: Json格式的快递单模板信息
    """
    # TODO: data must be secured
    setting = request.POST['data']
    if not setting:
        renderutil.report_error("缺少参数")

    setting = simplejson.loads(setting)
    name = setting['name']
    template = simplejson.dumps(setting['template'])
    type = setting['type']
    img_id = 0
    if setting['template']['background'] and setting['template']['background']['id']:
        img_id = setting['template']['background']['id']

    tmpl = None
    template_id = setting['id']
    if template_id and int(template_id) > 0:  # it's to update an existing template
        try:
            tmpl = ExpressTemplate.objects.get(id=template_id)
            # only supper user and template creator has permission to change a template
            if tmpl.create_by != request.user.id and not request.user.is_superuser:
                # TODO: the same admin in a supplier should have the access
                return renderutil.report_error("对不起，您没有修改权限。如有需要，请与系统管理员联系。")
            tmpl.name = name
            tmpl.template = template
            tmpl.type = type
            if img_id != 0:
                tmpl.shape_image_id = img_id
            tmpl.update_by = request.user.id
        except ExpressTemplate.DoesNotExist:
            return renderutil.report_error("对不起，您要修改的模板不存在，请确认是否已被删除。")
    else:
        tmpl = ExpressTemplate(name=name,
                               template=template,
                               type=type,
                               create_by=request.user.id)

        if img_id != 0:
            tmpl.shape_image_id = img_id

    try:
        tmpl.save()
        return renderutil.json_response({"id": tmpl.id, "name": tmpl.name})
    except Exception, e:
        logger.exception(e)
        return renderutil.report_error('保存模板信息失败：%s' % (e.message or e.args[1]))


@login_required
def del_express_template(request):
    """
    删除快递单模板
    :param request:
    :return: Json格式的删除结果
    """
    template_id = int(request.REQUEST.get('id', 0))
    if template_id > 0:
        try:
            template = ExpressTemplate.objects.get(id=template_id)
            if not request.user.is_superuser \
                    and template.create_by != request.user.id:
                return renderutil.report_error("对不起，您没有删除权限！")

            template.delete()
            return renderutil.json_response({'result': "ok"})
        except ExpressTemplate.DoesNotExist:
            return renderutil.report_error('对不起，没有找到该模板（id：%s）。' % template_id)
    else:
        return renderutil.report_error('无效的参数（id：%s）。' % template_id)