"""
WSGI config for meiduo_mall project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# 第二个参数指定配置环境为生产环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings.prod')

application = get_wsgi_application()
