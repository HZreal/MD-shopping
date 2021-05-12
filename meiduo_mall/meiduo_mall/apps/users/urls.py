from django.urls import path,re_path
from . import views
urlpatterns = [
    # name就是给url起别名，这个别名name指向这个路由，哪怕修改了此路由,依然可以通过别名name找到此路由
    # 为你的URL取名能使你在 Django 的任意地方唯一地引用它，尤其是在模板中。这个有用的特性允许你只改一个文件就能全局地修改某个URL模式。
    # reverse(users:register) —> '/register/'
    # re_path(r'^register/$', views.RegisterView.as_view()),
    path('register/', views.RegisterView.as_view(), name='register'),       # 用户注册


]




