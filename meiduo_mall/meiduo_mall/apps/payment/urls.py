from django.urls import path, re_path
from payment import views

urlpatterns = [
    # 点击去支付的axios请求
    re_path(r'^payment/(?P<order_id>\d+)/$', views.PaymentView.as_view()),

    # 保存订单状态
    path('payment/status/', views.PaymentStatusView.as_view()),



]



