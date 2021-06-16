#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # 第二个参数meiduo_mall.settings.dev 指定配置环境为开发环境。dev实际就是之前的setting
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)                    # 接收终端python manage.py runserver 0:8000所有参数


if __name__ == '__main__':
    main()



# runserver方法是调试Django时用到的运行方式，它使用Django自带的WSGI Server运行，主要在测试和开发中使用，并且runserver开启的方式也是单进程.