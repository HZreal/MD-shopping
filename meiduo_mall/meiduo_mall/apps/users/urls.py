# users.urls
from django.urls import path,re_path
from . import views
from django.contrib.auth.decorators import login_required



urlpatterns = [
    # name就是给此url起别名，这个别名name指向这个路由，哪怕修改了此路由,依然可以通过别名name找到此路由
    # 为你的URL取名能使你在Django的任意地方唯一地引用它，尤其是在模板中。这个有用的特性允许你只改一个文件就能全局地修改某个URL模式。
    # reverse(users:register) —> '/register/'

    # 调用as_view()返回view，调用view()返回dispatch，dispatch起着请求映射分发的作用，引导到类视图的对应请求函数

    # 用户注册
    path('register/', views.RegisterView.as_view(), name='register'),

    # 用户输入用户名鼠标失去焦点的axios请求，判断注册的用户名是否重复
    re_path(r'^usernames/(?P<username>[a-zA-Z][0-9a-zA-Z_]{4,19})/count/$', views.UsernameCountView.as_view()),
    # path('usernames/<str:username>/count/', views.UsernameCountView.as_view()),              # 转换器语法<参数类型:参数名>   (无法正则校验)

    # 用户输入手机号鼠标失去焦点的axios请求，判断注册的手机号是否重复
    re_path(r'^mobiles/(?P<mobile>1[34578]\d{9})/count/$', views.MobileCountView.as_view()),

    # 用户登录
    # re_path(r'^login/$', views.LoginView.as_view(), name='login'),
    path('login/', views.LoginView.as_view(), name='login'),

    # 用户退出登录
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # 显示用户个人信息页面
    path('info/', views.UserInfoView.as_view(), name='info'),
    # path('info/', login_required(views.UserInfoView.as_view()), name='info'),

    # 接收axios请求，添加邮箱：数据库用户更新字段
    path('emails/', views.EmailView.as_view()),

    # 接收用户邮件验证
    path('emails/verification/', views.VerifyEmailView.as_view()),

    # 显示用户收货地址页面，同时通过查询显示当前登录用户的收货地址信息
    path('addresses/', views.AddressView.as_view(), name='address'),

    # 接收用户新增地址的axios请求
    path('addresses/create/', views.AddressCreateView.as_view()),

    # 用户修改或者删除收货地址的请求
    re_path(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),

    # 设置默认地址
    re_path(r'^addresses/(?P<address_id>\d+)/default/$', views.SetDefaultAddressView.as_view()),

    # 修改收货地址标题
    re_path(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateAddressTitleView.as_view()),

    # 显示修改密码页面
    path('password/', views.ChangePasswordView.as_view(), name='password'),

    # 商品sku详情页面 接收axios请求 保存用户浏览记录(post) 获取用户浏览记录(get)
    path('browse_histories/', views.UserBrowseHistory.as_view()),


]



# http://192.168.94.131:8888/group1//M00/00/00/CtM3BVni03-ANUDwAAAmv27pX4k9203075





