# -*- coding: utf-8 -*-
"""
Django settings for tms project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
from django.conf import settings
settings.configure()

default_encoding = 'utf8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

ROOT_URLCONF = 'tms.urls'
LOGIN_URL = '/tms/login'
WSGI_APPLICATION = 'tms.wsgi.application'

# SECURITY WARNING: don't run with debug turned on in production!
ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ['127.0.0.1']
DEBUG = False
TEMPLATE_DEBUG = False
BASE_DIR = '/data/tms/'  # os.path.dirname(os.path.dirname(__file__))
APP_NAME = 'TMS'
#APP_HOST = 'hk.yichihui.com'
APP_HOST = 'tms.twohou.com'
APP_URL = 'http://%s:8001' % APP_HOST
SESSION_COOKIE_DOMAIN = APP_HOST
# 用于快速发送短信通知给供货商时嵌在短信中
URL_TO_INQUIRE_ORDER = "http://itravelbuy.twohou.com/sms/quickship/%(order_no)s/%(suffix)s"
TOKEN_EXPIRY = 7 * 24  # hours, 1 week
SMS_CODE_EXPIRY = 60 * 15  # 15 minutes
AGENT_QUERY_EXPIRY = 60 * 30  # 30 minutes
SESSION_COOKIE_AGE = 60*60*8  # 60 minutes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# 短信相关
# setting for SMS gateway
FAKE_SMS = False
FAKE_PAYMENT = False
FAKE_EMAIL = False
LOG_ROOT = '/data/log/nginx/'
global_app_setting = None  # used to store global configurable application settings

# Application definition
INSTALLED_APPS = (
    # 'bootstrap',
    # 'grappelli',
    # 'qiniustorage',
    'django.contrib.admin',
    # 'django.contrib.admin.apps.SimpleAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ueditor',
    'filemgmt',
    'article',
    'config',
    'log',
    'profile',
    'credit',
    'promote',
    'vendor',
    'basedata',
    'logistic',
    'report',
    'buding',
)

MIDDLEWARE_CLASSES = (
    'tms.middleware.auth.UserBasedExceptionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'tms.middleware.auth.AuthMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'tms.middleware.auth.AuthMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    # "django.middleware.transaction.TransactionMiddleware",

)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'podinns_tms',
        'HOST': '127.0.0.1',
        'USER': 'tms',
        'PASSWORD': 'tms@twohou.com',
        'CHARSET': 'utf-8',
        'STORAGE_ENGINE': 'INNODB',
        'OPTIONS': {
                    'init_command': 'SET foreign_key_checks = 0;',  # SET default_storage_engine=INNODB
        },
    }
}

TIME_ZONE = 'Asia/Shanghai'  # UTC
USE_TZ = False

STORE_NAME = '交易管理系统'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5=rh&=temogeiz8d78&721-om%xbjhxc=1@b3+5&uz%w&0f1i_'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            '127.0.0.1:11211',
            # '127.0.0.1:11212',
        ]
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'zh-hans'
USE_I18N = True
USE_L10N = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = "/data/static/"
STATIC_URL = '/static/'

MEDIA_ROOT = STATIC_ROOT+'images/'
MEDIA_URL = '/images/'
# ADMIN_MEDIA_PREFIX = STATIC_ROOT+'admin/images/'

# CAPTCHA_FONT = os.path.join(BASE_DIR, 'static/Vera.ttf')
STATICFILES_DIRS = (
    sys.path[0].replace('\\', '/') + '/static/',
    # sys.path[0].replace('\\', '/')
    # STATIC_ROOT,
    # MEDIA_ROOT,
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

TEMPLATE_DIRS = (
    sys.path[0].replace('\\', '/') + "/templates/",
    BASE_DIR + "templates/",
)
# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

# 七牛云存储相关配置
QINIU_ACCESS_KEY = '7WmRxMMgnC1pMMlVsRld6OXKUlIIbmf3613wz5nF'
QINIU_SECRET_KEY = '5s6E_IWufwDkr3aKZbRpdoJTZwYiBMSEKFbIc1bw'
QINIU_BUCKET_NAME = 'thoms'  # 要上传的空间
QINIU_BUCKET_DOMAIN = 'static.tms.twohou.com'  # '7xs3aw.com2.z0.glb.qiniucdn.com'
DEFAULT_FILE_STORAGE = 'qiniustorage.backends.QiniuStorage'
STATICFILES_STORAGE = 'qiniustorage.backends.QiniuStorage'
QINIU_SECURE_URL = False
QINIU_DOMAINS = ['static.tms.twohou.com', '7xs9j1.com2.z0.glb.qiniucdn.com', '7xs6ch.com2.z0.glb.qiniucdn.com']

import socket
# IS_LOCAL_DEV = socket.gethostname() == 'YYPC'    布丁生产服务器：iZbp1i0atz17i08tuc8jisZ
IS_LOCAL_DEV = socket.gethostname() in ['localhost', 'ShengdeMacBook-Air.local', 'YYPC', 'ShengdeAir']   # 'YYPC'
IS_REMOTE_DEV = socket.gethostname() in ['twohou-hotel', 'iZ23tgnmxyaZ']
# iZ23tgnmxyaZ
if IS_LOCAL_DEV:
    from .localsetting import *
elif IS_REMOTE_DEV:
    from .remotesetting import *

# 七牛静态资源访问URL
QINIU_URL = ("https://%s" % QINIU_BUCKET_DOMAIN) if QINIU_SECURE_URL else ("http://%s" % QINIU_BUCKET_DOMAIN)

# default setting
# FILE_UPLOAD_HANDLERS = ("django.core.files.uploadhandler.MemoryFileUploadHandler",
#                         "django.core.files.uploadhandler.TemporaryFileUploadHandler",)

FILE_UPLOAD_TEMP_DIR = MEDIA_ROOT+"upload/"
# for user upload
ALLOW_FILE_TYPES = ('.jpg', '.jpeg', '.gif', '.bmp', '.png', '.tiff')
# unit byte, maximum 50MB
ALLOW_MAX_FILE_SIZE = 50 * 1024 * 1024

os.path.exists(LOG_ROOT) or os.makedirs(LOG_ROOT, mode=0744)
LOGGING = {
    'version': 1,  # 指明dictConnfig的版本，目前就只有一个版本
    'disable_existing_loggers': False,  # 禁用所有的已经存在的日志配置
    'formatters': {  # 格式器
        'verbose': {  # 详细
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {  # 简单
            'format': '%(asctime)s %(levelname)s: %(message)s'
        },
    },
    # 'filters': {  # 过滤器
    #     'special': {  # 使用project.logging.SpecialFilter，别名special，可以接受其他的参数
    #         '()': 'project.logging.SpecialFilter',
    #         'foo': 'bar',#参数，名为foo，值为bar
    #     }
    # },
    'handlers': {  # 处理器，在这里定义了三个处理器
        # 'null': {  # Null处理器，所有高于（包括）debug的消息会被传到/dev/null
        #     'level': 'DEBUG',
        #     'class': 'django.utils.log.NullHandler',
        # },
        'console': {  # 流处理器，所有的高于（包括）debug的消息会被传到stderr，使用的是simple格式器
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_ROOT+'%s_debug.log' % APP_NAME,
            'formatter': 'verbose',
        },
        'track': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_ROOT+'%s_track.log' % APP_NAME,
            'formatter': 'verbose',
        },
        # 'mail_admins': {  # AdminEmail处理器，所有高于（包括）而error的消息会被发送给站点管理员，使用的是special格式器
        #     'level': 'ERROR',
        #     'class': 'django.utils.log.AdminEmailHandler',
        #     'filters': ['special']
        # }
    },
    'loggers': {  # 定义了三个记录器
        'django': {  # 使用null处理器，所有高于（包括）info的消息会被发往null处理器，向父层次传递信息
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG' if IS_LOCAL_DEV or IS_REMOTE_DEV else 'ERROR',
        },
        'suds': {  # 使用null处理器，所有高于（包括）info的消息会被发往null处理器，向父层次传递信息
            'handlers': ['console'],
            'propagate': True,
        },
        'django.tms': {  # 使用null处理器，所有高于（包括）info的消息会被发往null处理器，向父层次传递信息
            'handlers': ['file', 'console'],
            'propagate': False,
            'level': 'DEBUG' if IS_LOCAL_DEV or IS_REMOTE_DEV else 'ERROR',
        },
        'django.tracker': {  # 使用null处理器，所有高于（包括）info的消息会被发往null处理器，向父层次传递信息
            'handlers': ['track',],
            'propagate': False,
            'level': 'INFO',
        },
        # 'django.request': {  # 所有高于（包括）error的消息会被发往mail_admins处理器，消息不向父层次发送
        #     'handlers': ['mail_admins'],
        #     'level': 'ERROR',
        #     'propagate': False,
        # },
        # 'myproject.custom': {  # 所有高于（包括）info的消息同时会被发往console和mail_admins处理器，使用special过滤器
        #     'handlers': ['console', 'mail_admins'],
        #     'level': 'INFO',
        #     'filters': ['special']
        # }
    }
}

# mail setting
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.exmail.qq.com'  # 邮件smtp服务器
# EMAIL_PORT = '465'  # 端口
EMAIL_PORT = '25'  # 端口
EMAIL_HOST_USER = 'oms@sh-anze.com'  # 邮件账户
EMAIL_HOST_PASSWORD = 'Anze64687179'  # 密码
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'TMS <oms@sh-anze.com>'

MANAGERS = (('Winsom', 'winsom.huang@sh-anze.com'), ('ShengZhe', 'zhe.sheng@sh-anze.com'))
ADMINS = (('Winsom', 'winsom.huang@sh-anze.com'),)