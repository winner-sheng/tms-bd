# -*- coding: utf-8 -*-
# 包含各种与model处理相关的公共方法
from __future__ import division
from PIL import Image
import imghdr

__author__ = 'Winsom'


def make_thumb(path, size=480):
    pixbuf = Image.open(path)
    width, height = pixbuf.size

    if width > size:
        delta = width / size
        height = int(height / delta)
        pixbuf.thumbnail((size, height), Image.ANTIALIAS)

        return pixbuf


def image_type(img_file):
    return imghdr.what(img_file)
