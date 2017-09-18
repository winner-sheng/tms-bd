# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import BaseImage


class BaseImageAdmin(admin.ModelAdmin):
    list_display = ('thumb', 'origin', 'image_desc', 'usage',)  # 'width', 'height',
    list_editable = ('image_desc','usage', )
    readonly_fields = ['thumb',]  # 'width', 'height',
    fields = ['origin', 'thumb', 'image_desc', 'usage',]  # 'width', 'height',
    search_fields = ['image_desc', 'origin',  ]  # 'width',
    list_filter = ['usage']
    #formfield_overrides = {
    #    models.ImageField: {'widget': ClearableFileInput},
    #}
    save_as = True
    ordering = ['-upload_time']


# store_site.register(BaseImage, BaseImageAdmin)
admin.site.register(BaseImage, BaseImageAdmin)
