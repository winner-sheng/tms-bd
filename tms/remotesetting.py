# -*- coding: utf-8 -*-
# as separate setting file for local testing

# Development Server Settings go here
# import test settings
DEBUG = True
TEMPLATE_DEBUG = True
BASE_DIR = '/data/tms/'  # os.path.dirname(os.path.dirname(__file__))
APP_HOST = 'test.tmonkey.cn:8001'
APP_URL = 'http://%s' % APP_HOST
SESSION_COOKIE_DOMAIN = ''
SESSION_COOKIE_AGE = 60*60*24  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
# 用于快速发送短信通知给供货商时嵌在短信中
URL_TO_INQUIRE_ORDER = "http://test.itravelbuy.twohou.com/sms/quickship/%(order_no)s/%(suffix)s"
FAKE_SMS = True
FAKE_PAYMENT = True
FAKE_EMAIL = True
# 七牛云存储相关配置
QINIU_BUCKET_NAME = 'thoms-rtest'
QINIU_BUCKET_DOMAIN = '7xs9j1.com2.z0.glb.qiniucdn.com'
QINIU_SECURE_URL = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'twohou_tms',
        'HOST': '127.0.0.1',
        'USER': 'tms',
        'PASSWORD': 'tms@twohou.com',
        'CHARSET': 'utf-8',
        'STORAGE_ENGINE': 'INNODB',
        'OPTIONS': {
                    'init_command': 'SET foreign_key_checks = 0;',
        },
    }
}
# USE_TZ = False
LOG_ROOT = '/data/log/nginx/'
INTERNAL_IPS = ('127.0.0.1', )
# Application definition
INSTALLED_APPS = (
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
    # 'bootstrap_toolkit',
    # 'debug_toolbar',
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
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    # "django.middleware.transaction.TransactionMiddleware",

)
# DEBUG_TOOLBAR_PANELS = [
#     'debug_toolbar.panels.versions.VersionsPanel',
#     'debug_toolbar.panels.timer.TimerPanel',
#     'debug_toolbar.panels.settings.SettingsPanel',
#     'debug_toolbar.panels.headers.HeadersPanel',
#     'debug_toolbar.panels.request.RequestPanel',
#     'debug_toolbar.panels.sql.SQLPanel',
#     'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#     'debug_toolbar.panels.templates.TemplatesPanel',
#     'debug_toolbar.panels.cache.CachePanel',
#     'debug_toolbar.panels.signals.SignalsPanel',
#     'debug_toolbar.panels.logging.LoggingPanel',
#     'debug_toolbar.panels.redirects.RedirectsPanel',
# ]
# CONFIG_DEFAULTS = {
#     # Toolbar options
#     'RESULTS_CACHE_SIZE': 3,
#     'SHOW_COLLAPSED': True,
#     'JQUERY_URL': '/static/js/jquery.js',
#     # Panel options
#     'SQL_WARNING_THRESHOLD': 100,   # milliseconds
# }