from django.urls import path, re_path
from orders import views


urlpatterns = [
    # 提供订单结算页面
    path('orders/settlement/', views.OrderSettlementView.as_view(), name='settlement'),

    # 提交订单
    path('orders/commit/', views.OrderCommitView.as_view()),

    # 提供提交订单成功后的页面
    path('orders/success/', views.OrderSuccessView.as_view()),

    # 用户订单信息
    re_path(r'^orders/info/(?P<page_num>\d+)/$', views.UserOrderInfoView.as_view(), name='info'),

    # 点击我的订单页面待评价
    path('orders/comment/', views.OrderCommentView.as_view()),
]