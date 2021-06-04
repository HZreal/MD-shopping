from django.urls import path, re_path
from goods import views


urlpatterns = [
    # 商品列表页
    re_path(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view(), name='list'),

    # 接收axios请求，热销商品排行
    re_path(r'^hot/(?P<category_id>\d+)/$', views.HotGoodsView.as_view()),

    # 商品详情页
    re_path(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view(), name='detail'),

    # 统计三级类别对应商品的访问量
    re_path(r'detail/visit/(?P<category_id>\d+)/$', views.DetailVisitView.as_view()),




]












