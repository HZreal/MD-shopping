from django.urls import path, re_path
from rest_framework_jwt.views import obtain_jwt_token
from administrator.views import *


urlpatterns = [
    re_path(r'^authorizations/$', obtain_jwt_token),
    path(r'statistical/total_count/', statistical.UserTotalCountView.as_view()),           # 用户总量统计
    path(r'statistical/day_increment/', statistical.UserDayCountView.as_view()),           # 日增用户统计
    path(r'statistical/day_active/', statistical.UserActiveCountView.as_view()),           # 日活跃用户统计
    path(r'statistical/day_orders/', statistical.UserOrderCountView.as_view()),            # 日下单用户量统计
    path(r'statistical/month_increment/', statistical.UserMonthCountView.as_view()),       # 月增用户统计
    path(r'statistical/goods_day_views/', statistical.GoodsDayView.as_view()),             # 日分类商品访问量




]