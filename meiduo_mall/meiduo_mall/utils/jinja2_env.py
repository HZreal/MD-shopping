# 此文件名记得不要取jinja2.py ！！！否则系统模块jinja2.py无法使用

# from django.contrib.staticfiles.storage import staticfiles_storage
from django.templatetags.static import static
from django.urls import reverse

from jinja2 import Environment

# date过滤器
from django.template.defaultfilters import date

def environment(**options):
    # 创建环境对象
    env = Environment(**options)

    # TODO 自定义语法：{{ static('静态文件相对路径') }}     {{ url('路由命名空间') }}
    # 将上面这些新的语法定义到环境中
    env.globals.update({
        # 'static': staticfiles_storage.url,
        'static': static,                           # 获取静态文件的前缀
        'url': reverse,                             # 传入命名空间做重定向(反向解析)。在模板里使用url('路由命名空间'),实际就是调用reverse做重定向

    })

    # 返回环境对象
    return env