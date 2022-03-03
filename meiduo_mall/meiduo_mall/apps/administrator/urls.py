from django.urls import path, re_path
from rest_framework_jwt.views import obtain_jwt_token
from administrator.views import *


urlpatterns = [
    re_path(r'^authorizations/$', obtain_jwt_token),

    # 数据统计
    path(r'/statistical/total_count', statistical.UserTotalCountView.as_view()),           # 用户总量统计
    path(r'/statistical/day_increment', statistical.UserDayCountView.as_view()),           # 日增用户统计
    path(r'/statistical/day_active', statistical.UserActiveCountView.as_view()),           # 日活跃用户统计
    path(r'/statistical/day_orders', statistical.UserOrderCountView.as_view()),            # 日下单用户量统计
    path(r'/statistical/month_increment', statistical.UserMonthCountView.as_view()),       # 月增用户统计
    path(r'/statistical/goods_day_views', statistical.GoodsDayView.as_view()),             # 日分类商品访问量

    # 用户管理
    path(r'/users', user_manager.UserQuerySearchView.as_view()),                           # 获取查询用户 增加用户

    # 商品管理
    # path(r'/goods/specs', goods_manager.GoodsSpecsView.as_view()),                         # 获取、保存规格表
    # path(r'/goods/specs/(?P<pk>\d+)', goods_manager.GoodsSpecsView.as_view()),             # 获取、修改、删除单一规格详情
    #
    # path(r'/skus/images', goods_manager.ImageView.as_view()),                              # 获取、保存图片表
    # path(r'/skus/images/(?P<pk>\d+)', goods_manager.ImageView.as_view()),                  # 获取、修改、删除单一图片表
    # path(r'/skus/simple', goods_manager.ImageView.as_view()),                              # 获取图片关联的sku的id
    #
    # path(r'/skus', goods_manager.SKUGoodsView.as_view()),                                  # 获取商品sku
    # path(r'/skus/categories', goods_manager.SKUCategorieView.as_view()),                   # 获取三级分类信息、SPU表的名称信息、当前SPU商品的规格选项信息

]