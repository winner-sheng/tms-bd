# -*- coding: utf-8 -*-
__author__ = 'winsom'
from django.views.debug import technical_500_response
from tms import settings
from django import http
import sys
from util.webtool import sendmail
from util.renderutil import logger


class AuthMiddleware(object):
    def process_request(self, request):
        if not request.user.is_superuser and request.user.has_perm('basedata.as_supplier'):
            print request.user, ' is a supplier'
            if request.path[:5] == '/tms/':
                return http.HttpResponsePermanentRedirect('/stms/%s' % request.path[5:])
        elif request.path[:6] == '/stms/':
            return http.HttpResponsePermanentRedirect('/tms/%s' % request.path[6:])
        # log.debug('REMOTE_ADDR: %s' % request.META['REMOTE_ADDR'])
        # if request.META.get('REMOTE_ADDR') in getattr(settings, "BLOCKED_IPS", []):
        #     return http.HttpResponseForbidden('<h1>Forbidden</h1>')
        #
        # if 'TMS_AUTH_TOKEN' in request.META:
        #     log.debug('TMS_AUTH_TOKEN: %s' % request.META['TMS_AUTH_TOKEN'])

        # if 'POST' == request.method:
        #     request.GET = request.POST

        # if request.user and not hasattr(request.user, 'is_supplier'):
        #     log.debug('user: %s' % request.user)
        #     sm = request.user.suppliermanager_set.all()  # defined in vendor.SupplierManager
        #     request.user.is_supplier =  sm and len(sm) > 0
        return None


class UserBasedExceptionMiddleware(object):
    def process_exception(self, request, exception):
        if not settings.DEBUG:
            uid = request.POST.get('uid') or request.GET.get('uid')
            sendmail(subject='%s: TMS出错了' % (uid or request.user),
                     message=None,
                     from_email=settings.DEFAULT_FROM_EMAIL,
                     recipient_list=[email for name, email in settings.MANAGERS],
                     html_message=technical_500_response(request, *sys.exc_info()).content)
        in_ips = settings.INTERNAL_IPS or ['127.0.0.1']
        if (request.user and request.user.is_superuser) or request.META.get('REMOTE_ADDR') in in_ips:
            res = technical_500_response(request, *sys.exc_info())
            logger.debug(res)

        return None