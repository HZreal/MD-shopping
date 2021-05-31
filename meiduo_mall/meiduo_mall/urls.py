"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include,re_path

# 在include()中指定命名空间而不提供app_name是不被允许的,即设置namespace同时必须设置app_name,且(urls,app_name)构成元祖

urlpatterns = [
    path('admin/', admin.site.urls),

    # 用户子应用
    path('', include(('users.urls', 'users'), namespace='users')),                  # users 指定命名空间，必须设置app_name
    # re_path(r'^$', include('users.urls')),                                        # TODO 所有路由在总路由校验匹配
    # re_path(r'^', include(('users.urls', 'users'), namespace='users')),           # TODO 所有路由在总路由中不校验匹配，只负责开始，由子应用去校验匹配

    # 主页内容子应用
    path('', include(('contents.urls', 'contents'), namespace='index')),

    # 验证子应用
    path('', include('verifications.urls')),

    # oauth2.0认证子应用
    path('', include('oauth.urls')),

    # 省市区地区管理子应用
    path('', include('areas.urls')),

    # 商品子应用
    path('', include(('goods.urls', 'goods'), namespace='goods')),



]
