# -*- coding: utf-8 -*-

__author__ = 'Winsom'
import types

from django.db import models
from django.db.models.fields.files import ImageFieldFile
from django.forms.models import model_to_dict
from django.utils import timezone

import json
from django.core.serializers.json import DateTimeAwareJSONEncoder
from decimal import *
from datetime import datetime, date
from uuid import UUID


# 注意，由于抛弃了无关属性，使用该方法encode Model为json后无法decode还原成相同的Model对象
def json_encode(data):
    """
    The main issues with django's default json serializer is that properties that
    had been added to a object dynamically are being ignored (and it also has
    problems with some models).
    """

    def _any(data):
        ret = None
        if isinstance(data, types.ListType):
            ret = _list(data)
        elif isinstance(data, types.DictType):
            ret = _dict(data)
        elif isinstance(data, Decimal):
            # json.dumps() cant handle Decimal
            ret = str(data)
        elif isinstance(data, datetime):
            t = data if timezone.is_naive(data) else timezone.localtime(data)
            ret = t.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(data, date):
            t = data if timezone.is_naive(data) else timezone.localtime(data)
            ret = t.strftime('%Y-%m-%d')
        elif isinstance(data, models.query.QuerySet):
            # Actually its the same as a list ...
            ret = _list(data)
        elif isinstance(data, models.Model):
            ret = _model(data)
        elif isinstance(data, UUID):
            ret = data.hex
        else:
            ret = data
        return ret

    def _model(data):
        ret = {}
        # If we only have a model, we only want to encode the fields.
        for f in data._meta.fields:
            '''
            if isinstance(f, ForeignKey):
                v = getattr(data, f.name)
                if v is None:
                    ret[f.name] = 'null'
                else:
                    ret[f.name] = _model(v)
            else:
            '''
            v = getattr(data, f.attname)
            if isinstance(v, ImageFieldFile):
                ret[f.attname] = str(v)  # (hasattr(v, 'file') and v.url or None)
            elif isinstance(v, UUID):
                ret[f.attname] = v
            else:
                ret[f.attname] = _any(v)
        # And additionally encode arbitrary properties that had been added.
        # fields = dir(data.__class__) + ret.keys()
        # add_ons = [k for k in dir(data) if k not in fields]
        # for k in add_ons:
        #     ret[k] = _any(getattr(data, k))
        return ret

    def _list(data):
        ret = []
        for v in data:
            ret.append(_any(v))
        return ret

    def _dict(data):
        ret = {}
        for k, v in data.items():
            ret[k] = _any(v)
        return ret

    ret = _any(data)

    return json.dumps(ret, ensure_ascii=False, cls=DateTimeAwareJSONEncoder)


# 用于将model转成可以序列化为json的dict对象
# TODO: may need to handle ForeignKey and ManyToManyField
def get_dict_for_json(model):
    new_dict = model_to_dict(model)
    for attr, value in new_dict.items():
        if isinstance(value, ImageFieldFile):
            if hasattr(value, 'file'):
                new_dict[attr] = value.url
            else:
                new_dict[attr] = ''

    return new_dict
