# -*- coding: utf-8 -*-
__author__ = 'winsom'
from django.dispatch import Signal


product_onshelf = Signal(providing_args=['obj'])
product_offshelf = Signal(providing_args=['obj'])
product_stock_warning = Signal(providing_args=['obj'])

order_new = Signal(providing_args=['obj'])
order_revoked = Signal(providing_args=['obj'])
order_paid = Signal(providing_args=['obj'])
order_packing = Signal(providing_args=['obj'])
order_shipped = Signal(providing_args=['obj'])
order_signoff = Signal(providing_args=['obj'])
order_returned = Signal(providing_args=['obj'])
order_refunded = Signal(providing_args=['obj'])
order_request_refund = Signal(providing_args=['obj'])
order_closed = Signal(providing_args=['obj'])
order_deleted = Signal(providing_args=['obj'])
order_split = Signal(providing_args=['obj'])
