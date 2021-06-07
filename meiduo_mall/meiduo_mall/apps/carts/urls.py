from django.urls import path, re_path

from carts import views


urlpatterns = [
    # 购物车管理
    path('carts/', views.CartsView.as_view(), name='info'),

    # 用户是否勾选全选的axios请求
    path('carts/selection/', views.CartsSelectAllView.as_view()),

    # 展示商品简单购物车
    path('carts/simple/', views.CartsSimpleView.as_view()),



]








