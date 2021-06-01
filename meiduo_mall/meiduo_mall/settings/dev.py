# 开发环境的配置文件，在manage.py中声明
# global_settings.py是全局配置信息，描述的更详细

"""
Django settings for meiduo_mall project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os, sys     # 早期dirs列表设置模板路径用os.path.join()
from pathlib import Path



# Build paths inside the project like this: BASE_DIR / 'subdir'.
# 注意：本模块路径为meiduo_mall/meiduo_mall/settings/dev.py
import meiduo_mall.utils.fastdfs.fdfs_storage

BASE_DIR = Path(__file__).resolve().parent.parent                      # BASE_DIR指向 meiduo_mall/meiduo_mall/
# BASE_DIR = Path(__file__).resolve().parent.parent.parent             # BASE_DIR指向 meiduo_mall/
# print(__file__)
# print(Path(__file__))
# print(Path(__file__).resolve())                                      # 这三个输出结果均是 F:\Django\meiduo\meiduo_mall\meiduo_mall\settings\dev.py 即本模块路径
# print(Path(__file__).resolve().parent)                               # F:\Django\meiduo\meiduo_mall\meiduo_mall\settings
# print(BASE_DIR)                                                      # F:\Django\meiduo\meiduo_mall\meiduo_mall
# 早期版本如下
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))                  # __file__表示本模块dev.py文件名
# abspath(__file__)获取本模块绝对路径 F:\Django\meiduo\meiduo_mall\meiduo_mall\settings\dev.py
# dirname获取本模块所在的目录路径 F:\Django\meiduo\meiduo_mall\meiduo_mall\settings 即获取父级目录
# 外层dirname再取上上级目录路径 F:\Django\meiduo\meiduo_mall\meiduo_mall 即是BASE_DIR



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--h#-v9pv2gjo+)ttwk^um9&1cl!+r*5@2hu_f@qicg152#(lvu'

# 开发者调试用，部署上线后则改为False
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# 允许访问后端的主机列表，默认为空仅支持本机访问
# 安全机制：只能以列举的主机进行访问
# 改变允许方式：加入ip或者域名
# 此时默认的localhost和127.0.0.1访问需要命令行添加参数访问 python manage.py runserver 127.0.0.1:8000
ALLOWED_HOSTS = ['localhost',
                 '127.0.0.1',
                 '192.168.0.103',
                 'www.meiduo.site',
                 ]


# 指定自定义用户模型类，否则迁移等操作会去找系统的auth.User模型类
AUTH_USER_MODEL = 'users.User'                             # 语法： 子应用名.模型类名

# 指定自定义认证后端
AUTHENTICATION_BACKENDS = ['users.utils.UsernameMobileBackend']

# 判断用户是否是登录，指定登录后重定向的地址
LOGIN_URL = '/login/'
# redirect_field_name = REDIRECT_FIELD_NAME = 'next'         # 默认是next

# QQ登录的配置参数
QQ_CLIENT_ID = '101518219'
QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'
QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'
# QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback/'

# 配置邮件服务器             # SIARACHOFWNZJGBO
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'                         # 指定邮件后端
EMAIL_HOST = 'smtp.163.com'                                                           # 发邮件主机
EMAIL_PORT = 25                                                                       # 发邮件端口
EMAIL_HOST_USER = 'huangzhen_happy@163.com'                                           # 授权的邮箱
EMAIL_HOST_PASSWORD = 'SIARACHOFWNZJGBO'                                              # 邮箱授权时获得的密码，非注册登录密码
EMAIL_FROM = '开心购，舒心买<huangzhen_happy@163.com>'                                        # 发件人抬头
# SMTP是用来发送邮件,IMAP、POP协议是用来接收邮件

# 邮件验证地址
EMAIL_VERIFY_URL = 'http://www.meiduo.site:8000/emails/verification/'

# 指定自定义的Django文件存储类
DEFAULT_FILE_STORAGE = 'meiduo_mall.utils.fastdfs.fdfs_storage.FastDFSStorage'

# FastDFS服务器路由
FDFS_BASE_URL = 'http://192.168.94.131:8888/'

# Haystack配置
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://192.168.94.131:9200/',                         # Elasticsearch服务器ip地址，端口号固定为9200
        'INDEX_NAME': 'meiduo_mall',                                  # Elasticsearch建立的索引库的名称
    },
}
# 当Haystack检测到数据库添加、修改、删除数据时，自动生成新的索引
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'
# Haystack设置分页器每页显示记录数量，不指定默认仅一页显示所有
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 5


# 查看导包路径(或者说模块搜索路径PYTHONPATH)
# print(sys.path)                                                     # PYTHONPATH 是一个列表，python解释器对模块的搜索按列表中的顺序搜索
# ['F:\\Django\\meiduo\\meiduo_mall',
# 'F:\\Django\\meiduo',
# 'F:\\virtualenvs\\py3_django_1\\lib\\site-packages',  ... ]

# sys.path.insert(列表下标, 路径)                                     # 插入模块搜索路径(导包路径)
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))                    # 运行才生效！！表示将目录apps/插入到模块搜索路径PYTHONPATH列表中,告知解释器可以在apps/这个目录去找模块
# print(sys.path)
# PYTHONPATH列表多了一个路径 'F:\\Django\\meiduo\\meiduo_mall\\meiduo_mall\\apps',       # 此时解释器就可通过目录apps/找到子应用模块了

# TODO 通过右击apps—>mark directory as—>source root 即标记为源根，也会将目录apps/写到PYTHONPATH中，可以解决安装子应用的问题，但是生成迁移文件时会报错，提示找不到模块users (why?) 而采用sys.path.insert，生成迁移文件正常执行
# 标记为源根：是告诉IDE编译器(pycharm)此文件夹及其子文件夹包含应作为构建过程的一部分进行编译的源代码，也即是pycharm编辑器能找到该模块，但运行代码是解释器进行的，解释器不一定找得到该模块，解释器找模块是通过模块搜索路径顺序查找的


# 安装注册子应用，子应用是否注册取决于其是否需要迁移或者需要模板渲染
INSTALLED_APPS = [
    'django.contrib.admin',                             # admin子应用，Django后台管理系统
    'django.contrib.auth',                              # auth子应用，Django默认的用户认证系统
    'django.contrib.contenttypes',
    'django.contrib.sessions',                          # sessions子应用
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 注册子应用
    # 'meiduo_mall.apps.users',                         # 通过工程这个源根(F:\\Django\\meiduo\\meiduo_mall)找到
    'users',                                            # 所有子应用都定义在包apps中，
    # 'users.apps.UsersConfig',
    'contents',                                         # 首页广告模块
    'verifications',                                    # 图形验证码
    'oauth',                                            # oauth2.0认证
    'areas',                                            # 省市区
    'goods',                                            # 商品
    'haystack',                                         # 全文检索




]


# 中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# 此工程的URL配置入口，默认是工程名.urls  可修改但一般不改
ROOT_URLCONF = 'meiduo_mall.urls'


# 模板配置
TEMPLATES = [
    # jinja2模板引擎
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',          # jinja2 引擎
        # 此处的BASE_DIR指的是本工程里的meiduo_mall，而非工程本身的meiduo_mall
        'DIRS': [BASE_DIR / 'templates'],                             # 模板文件加载路径
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # 补充jinja2引擎环境
            'environment': 'meiduo_mall.utils.jinja2_env.environment',
        },
    },

    # 默认模板引擎
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },

]


WSGI_APPLICATION = 'meiduo_mall.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
# sqlite是一个嵌入式小型关系型数据库,主要是在移动端使用
# 中型数据库：mysql(甲骨文) sqlserver(微软)
# 大型数据库：oracle DB2
DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': BASE_DIR / 'db.sqlite3',

        'ENGINE': 'django.db.backends.mysql',
        'HOST': '192.168.94.131',
        'PORT': '3306',
        'USER': 'huangzhen',
        'PASSWORD': 'root',
        'NAME': 'meiduo',

    }
}

# session数据的存储方式可以如下:
# 方式一：Django对session的默认存储方式，可不写
# SESSION_ENGINE='django.contrib.sessions.backends.db'
# 方式二：设置为本地缓存：储存在本机内存中，如果丢失则不能找回，比数据库的方式读写更快
# SESSION_ENGINE='django.contrib.sessions.backends.cache'
# 方式三：设置为混合存储：优先从本机内存中存取，如果没有则从数据库中存取
# SESSION_ENGINE='django.contrib.sessions.backends.cached_db'
# 方式四：设置为redis存储：以后session不再保存在系统django_session表中，而是保存在redis库
CACHES = {
    # 默认存储在0号库
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",                    # 去找中间件
        # "LOCATION": "redis://127.0.0.1:6379/0",                      # 网络通信三要素：协议，ip，port
        "LOCATION": "redis://192.168.94.131:6379/0",                   # 远程redis的0号库
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },

    # session存储在1号库
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.94.131:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },

    # 验证码存储在2号库
    "verify_code": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.94.131:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
# 以上进行了分库存储操作
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

# 语言设置
# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-Hans'

# 时区
# TIME_ZONE = 'UTC'    # 格林尼治时间
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
# Django是通过STATIC_URL区分动态资源和静态资源
# Django认定：请求资源http://ip:port + STATIC_URL + 文件名 为静态资源
# 即STATIC_URL规定是否是静态资源
STATIC_URL = '/static/'

# 告知系统静态文件加载路径，目前开发环境放在工程中，部署上线则放在Nginx代理服务器
STATICFILES_DIRS = [
    BASE_DIR / 'static',             # os.path.join(BASE_DIR, 'static')
]



# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# 日志配置信息
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,         # 是否禁用已经存在的日志器
    'formatters': {                            # 日志信息输出显示的格式
        'verbose': {                           # 描述详细
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {                            # 描述简单
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {                               # 对日志进行过滤
        'require_debug_true': {                # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {                               # 日志处理方式
        'console': {                            # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {                                # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            # 'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/meiduo.log'),
            'filename': BASE_DIR.parent / 'logs/meiduo.log',                                     # 日志文件的存放位置
            'maxBytes': 300 * 1024 * 1024,                       # 每个日志文件的大小
            'backupCount': 10,                                   # 日志文件个数(一个文件存满自动生成下一个)
            'formatter': 'verbose'
        },

        # 若日志文件不够，还可再建，如'file1':{ },
    },

    'loggers': {                                                # 日志器
        'django': {                                             # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],                    # 可以同时向终端与文件中输出日志
            'propagate': True,                                  # 是否继续传递日志信息
            'level': 'INFO',                                    # 日志器接收的最低日志级别
        },

        # 可再建，如'django1': { },
    }
}


# import logging
# # 创建日志记录器对象，参数django就是LOGGING里loggers的配置信息
# logger = logging.getLogger('django')
# # 输出日志
# logger.debug('测试logging模块debug')
# logger.info('测试logging模块info')
# logger.error('测试logging模块error')