from django.urls import path,re_path
from oauth import views

urlpatterns = [
    # 提供QQ登录扫码页面
    path('qq/login/', views.QQAuthURLView.as_view()),

    # 处理QQ登录后的回调
    path('oauth_callback/', views.QQAuthUserView.as_view()),
]




