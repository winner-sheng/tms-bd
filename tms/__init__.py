# -*- coding: utf-8 -*-
from django.apps import AppConfig
from settings import STORE_NAME
from django.db.models import Lookup
from django.db.models.fields import Field
from django.db.models import Func
__author__ = 'Winsom'


class TMSConfig(AppConfig):
    name = 'TMS'
    verbose_name = STORE_NAME

default_app_config = 'TMSConfig'


@Field.register_lookup
class NotEqual(Lookup):
    lookup_name = 'ne'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s <> %s' % (lhs, rhs), params


@Field.register_lookup
class FindInSet(Lookup):
    lookup_name = 'inset'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return 'find_in_set(%s, %s)' % (rhs, lhs), params


class Convert(Func):
    function = 'CONVERT'
    template = '%(function)s(%(expressions)s using gbk)'
