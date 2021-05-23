from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django import http
# from models import User                         # 导入模块时找不到，users不在导包路径，系统找不到users.model.py
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from users.models import User                     # 运行时不报错，程序运行时已进行apps/插入导包操作，但未运行时此处会报红色编辑错误(编辑器pycharm找不到)，只需设置apps标记为源根，就不会报编辑错误
from django.views import View
import re, json, logging
from django.db import DatabaseError
from meiduo_mall.utils.response_code import RETCODE                      # 将工程根meiduo_mall标记为源根，则编辑器不会报红，不论编辑器是否报红，解释器能找到模块就行
from django_redis import get_redis_connection
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from celery_tasks.email.tasks import send_verify_email
from users.utils import generate_email_url, check_verify_email_token



# 创建日志器
logger = logging.getLogger('django')

# 注册
class RegisterView(View):
    # 前后端不分离，由后端提供注册页面
    def get(self, request):
        return render(request, 'register.html')

    # 后端用户注册逻辑接口
    def post(self,request):
        # 接收请求数据:form表单:Django可以自动解析表单数据，故可用request.POST直接获取数据。json数据只能request.body获取，还要解码
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        client_sms_code = request.POST.get('sms_code')
        allow = request.POST.get('allow')

        # 校验参数:对前端数据再次校验，保证后端安全，避免黑客绕过前端发送数据。前后端校验逻辑相同
        # 判断参数：1.参数是否齐全，2.用户名合法，3.密码合法，4.确认密码相同，5.手机号合法，6.勾选协议
        # 只要缺少一个参数，或者参数格式有误，禁止此次请求，保证后端后续逻辑安全
        if not all([username, password, password2, mobile, allow, client_sms_code]):                 # all([])判断列表元素是否为空，只要有一个为空则返回false
            # HttpResponseForbidden封装了403响应码
            return http.HttpResponseForbidden('缺少必要参数')
        if not re.match(r'^[a-zA-Z][0-9a-zA-Z_]{4,19}$', username):
            return http.HttpResponseForbidden('请输入5-20位字符的用户名，首位只能是字母')
        if not re.match(r'^[a-zA-Z][0-9a-zA-Z]{7,19}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码，首位非数字')
        if not password2 == password:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        if not re.match(r'^1[34578]\d{9}$', mobile):
            return http.HttpResponseForbidden('您输入的手机号格式不正确')
        if not allow == 'on':              # checkbox被勾选时allow的值是'on'字符串
            return http.HttpResponseForbidden('请勾选用户协议')

        # 从redis中取短信验证码
        redis_conn = get_redis_connection('verify_code')
        server_sms_code = redis_conn.get('sms_%s' % mobile)
        if server_sms_code is None:
            return render(request, 'register.html', {'sms_error_mesaage': '短信验证码无效'})
        if not client_sms_code == server_sms_code.decode():
            return render(request, 'register.html', {'sms_error_mesaage': '输入短信验证码有误'})

        # 保存用户注册数据
        # create_user()方法内置密码加密，存储到库等操作，访问了外部资源用try
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', context={'register_error_message': '注册失败'})
         # 测试注册失败错误提示信息(页面整体刷新)
        # return render(request, 'register.html', context={'register_error_message': '注册失败'})

        # 实现状态保持(保存注册数据成功入库之后，响应之前)
        # 需求一：注册成功后即表示用户登入成功，转入首页，那么此时可以在注册成功后实现状态保持
        # 需求二：注册成功后不表示用户登入成功，转入登录页面让用户登录，那么此时不用在注册成功后实现状态保持，而是等用户登录后转入首页实现状态保持
        # 这里做需求一：
        # Django用户认证系统(auth子应用)提供了login()方法。封装了写入session的操作，帮助我们快速登入一个用户，并实现状态保持，详看源码
        login(request, user)

        # 响应结果：注册成功，重定向到首页路径 '/'  给用户传sessionid,csrftoken等cookie信息
        # return redirect(reverse('namespace:name'))
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=3600 * 24 * 14)
        return response


# 接收axios请求，判断注册的用户名是否重复
class UsernameCountView(View):
    def get(self, request, username):                # username接收请求路由url参数
        # 接收校验参数：路径参数正则匹配已完成
        # 使用username查询数据库中名为username的记录条数,
        count = User.objects.filter(username=username).count()

        # 响应结果：发送json数据
        data = {
            'status': RETCODE.OK,                          # 状态码
            'error_mesaage': 'OK',                         # 错误提示信息
            'count': count,                                # 记录条数
        }
        return http.JsonResponse(data)


# 接收axios请求，判断注册的手机号是否重复
class MobileCountView(View):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'status': RETCODE.OK,
            'error_message': 'OK',
            'count': count,
        }
        return http.JsonResponse(data)


# 登录
class LoginView(View):
    # 后端提供用户登录页面
    def get(self, request):
        return render(request, 'login.html', )

    # 实现用户登录逻辑
    def post(self, request):
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # 校验参数，与前端相同
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^[0-9a-zA-Z_]{5,20}$', username):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')
        if not re.match(r'^[a-zA-Z][0-9a-zA-Z]{7,19}$', password):
            return http.HttpResponseForbidden('请输入正确的密码')

        # 认证用户
        # user = User.objects.get(username=username)                            # ORM操作mysql
        # user.check_password(password)                                         # 父类提供的校验密码
        # 父类提供的认证方法，封装了check_password()等，定义在auth.backends.ModelBackend类中，但无法用手机号认证，需要重写authenticate
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_error_msg': '账户或密码错误'})

        # 状态保持
        login(request,user)
        # 使用remembered确定状态保持周期，实现记住登录
        if remembered != 'on':                                          # 用户没有记住登录，则状态保持在浏览器会话结束后就销毁
            request.session.set_expiry(0)                               # 单位是秒
        else:                                                           # 状态保持周期为两周(默认，可设定)
            request.session.set_expiry(None)

        # 取出查询字符串参数next
        next = request.GET.get('next')
        if next:
            return redirect(next)                      # 若有next,则直接重定向到next对应的路由

        # 为了实现首页右上角展示用户名信息，将用户名缓存到cookie中,由前端vue调用cookie信息渲染
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=3600 * 24 * 14)
        # 响应结果,重定向到首页
        return response


# 用户退出登录
class LogoutView(View):

    def get(self, request):
        # 清除状态保持,logout()内部封装了清除session的操作
        logout(request)

        # 删除cookie中的用户名，否则即使退出登录还是会显示用户名，因为用户名的显示是由前端vue渲染的
        response = redirect(reverse('contents:index'))
        response.delete_cookie('username')

        # 响应结果
        return response


# 用户中心：需要验证用户登录才可进入，继承父类LoginRequiredMixin，利用next参数重定向
class UserInfoView(LoginRequiredMixin, View):
    # 提供用户中心页面
    def get(self, request):
        # if request.user.is_authenticated:
        #     return render(request, 'user_center_info.html')
        # else:
        #     return  redirect(reverse('users:login'))
        # 以上验证登录逻辑因继承LoginRequiredMixin类自动验证

        # LoginRequiredMixin类有两个配置参数(详看源码)
        # login_url = '/login/'               # 在配置文件dev.py中设置，则每个需要验证的视图函数不用写
        # redirect_field_name = REDIRECT_FIELD_NAME = 'next'    # 默认next，引导到原来的路由，无需设置

        # LoginRequiredMixin验证用户已登录，那么request.user就是登录用户，即无需查库获取用户对象
        # print(request.user)            # 用户对象
        # 将用户信息通过模板显示在页面：每次页面一刷新都会传一次
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }
        print(context)
        return render(request, 'user_center_info.html', context)


# 接收axios请求，添加邮箱
# 后端检测到用户未登录时，不会跳入此视图函数，而是会先跳到LoginRequiredJSONMixin中执行重写函数handle_no_permission()
# 若用户处于未登录状态(比如手动删除cookie)，则根据需求返回json数据(错误码4101)，此时不会进入此视图函数
class EmailView(LoginRequiredJSONMixin, View):

    # put请求：数据库更新字段数据
    def put(self, request):
        # 接收参数：对于非表单类型的请求体数据，Django无法自动解析,通过request.body属性获取最原始的请求体数据，自行根据请求体格式（JSON、XML等）进行解析，request.body返回bytes类型
        body = request.body             # 前端json数据保存在请求体body
        json_str = body.decode()
        data_dict = json.loads(json_str)
        email = data_dict.get('email')

        # 校验参数
        if not email:
            return http.HttpResponseForbidden('缺少必要参数')
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('输入参数email有误')

        # 将用户输入的邮箱保存到数据库用户表的email字段
        try:
            request.user.email = email                       # 更新字段
            request.user.save()                              # 入库
            # User.objects.filter(username__exact=request.user.username).update(email=email)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})

        # 生成邮件验证地址
        verify_email_url = generate_email_url(request.user)

        # 让celery发送验证邮件
        send_verify_email.delay(email, verify_email_url)

        # 成功添加邮箱后响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加成功'})


# 接收用户邮件验证
class VerifyEmailView(View):
    def get(self, request):
        # 接收参数
        token = request.GET.get('token')
        # 校验参数
        if not token:
            return http.HttpResponseForbidden('缺少必要参数token')

        # 通过token解码并查库返回的用户对象
        user = check_verify_email_token(token)
        if not user:
            return http.HttpResponseForbidden('无效的token')
        # 将用户的email_active设置为True
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('激活邮箱失败')

        # 响应：重定向到用户中心
        return redirect(reverse('users:info'))
















































































































































































































