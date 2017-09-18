# -*- coding: utf-8 -*-
# 包含各种地图与地理位置相关的工具方法
import urllib
import urllib2
import math
import json
from decimal import *

__author__ = 'Winsom'

BAIDU_API_KEY = "ihYIEGxrVQ2Bd66XP2OhURBa"
BAIDU_ROUTEMATRIX_API_URL = 'http://api.map.baidu.com/direction/v1/routematrix'
BAIDU_GEOCODER_API_URL = 'http://api.map.baidu.com/geocoder/v2/'
BAIDU_IP_LOCATION_API_URL = 'http://api.map.baidu.com/location/ip'


def get_distance(from_lat, from_lng, to_lat, to_lng):
    origins = "%s,%s" % (from_lat, from_lng)
    destinations = "%s,%s" % (to_lat, to_lng)
    data = {"method": "get",
            "output": "json",
            "ak": BAIDU_API_KEY,
            "origins": origins,
            "destinations": destinations}
    url = BAIDU_ROUTEMATRIX_API_URL + '?' + urllib.urlencode(data)
    result = None
    try:
        response = urllib2.urlopen(url)
        distance = response.read()
        distance = json.loads(distance)
        result = distance['result']['elements'][0]
        # print distance
    except Exception, e:
        print "Something wrong while reading API"

    return result


def get_location(address):
    data = {"method": "get",
            "output": "json",
            "ak": BAIDU_API_KEY,
            "address": address}
    url = BAIDU_GEOCODER_API_URL + '?' + urllib.urlencode(data)
    result = None
    try:
        response = urllib2.urlopen(url)
        api_result = response.read()
        if api_result:
            result = json.loads(api_result)
    except Exception, e:
        print "Read api failed: %s" % e.message

    return result


def get_location_by_ip(ip):
    data = {"method": "get",
            # "output": "json",
            "ak": BAIDU_API_KEY,
            "ip": ip,
            "coor": "bd09ll"}
    url = BAIDU_IP_LOCATION_API_URL + '?' + urllib.urlencode(data)
    result = None
    try:
        response = urllib2.urlopen(url)
        api_result = response.read()
        if api_result:
            result = json.loads(api_result)
    except Exception, e:
        print "Read api failed: %s" % e.message

    return result


def get_address(lat, lng):
    data = {"method": "get",
            "output": "json",
            "ak": BAIDU_API_KEY,
            "location": "%s,%s" % (lat, lng)}
    url = BAIDU_GEOCODER_API_URL + '?' + urllib.urlencode(data)
    result = None
    try:
        response = urllib2.urlopen(url)
        api_result = response.read()
        if api_result:
            result = json.loads(api_result)
    except Exception, e:
        print "Read api failed: %s" % e.message

    return result


'''
# 计算两点之间距离
# @param _lat1 - start纬度
# @param _lon1 - start经度
# @param _lat2 - end纬度
# @param _lon2 - end经度
# @return km(四舍五入)
'''


def get_simple_distance(src_lat, src_lng, dest_lat, dest_lng):
    from_lat = (math.pi() / 180) * src_lat
    to_lat = (math.pi() / 180) * dest_lat

    from_lng = (math.pi() / 180) * src_lng
    to_lng = (math.pi() / 180) * dest_lng

    # 地球半径
    earth_radius = 6378.1
    d = math.acos(math.sin(from_lat) * math.sin(to_lat)
                  + math.cos(from_lat) * math.cos(to_lat) * math.cos(to_lng - from_lng)) * earth_radius
    getcontext().rounding = ROUND_HALF_UP
    getcontext().prec = 8
    return d

