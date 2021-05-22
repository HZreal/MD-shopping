from django.urls import path,re_path
from oauth import views

urlpatterns = [
    # 接收axios请求，向qq第三方请求QQ登录扫码页面返回给前端
    path('qq/login/', views.QQAuthURLView.as_view()),

    # 处理用户QQ扫码登录后的回调逻辑
    path('oauth_callback/', views.QQAuthUserView.as_view()),
]




