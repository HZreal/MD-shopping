import re
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings                         # 引入配置文件，这里等价于引用dev.py
from django import http
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
import logging
from oauth.models import OAuthQQUser
from django.contrib.auth import login,logout
from oauth.utils import generate_access_token, check_access_token
from users.views import User

# 创建日志输出器
logger = logging.getLogger('django')


class QQAuthURLView(View):
    # 向QQ方请求扫码页面地址login_url        即oauth2.0认证中的由authorization code获取认证码code
    def get(self, request):
        # 接收next
        next = request.GET.get('next')

        # 初始化工具对象      settings.QQ_CLIENT_ID读取配置文件中的参数
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        # get_qq_url()封装了拼接路由并向第三方QQ发送请求，请求QQ登录扫码页面地址返回给前端，前端拿到login_url即可打开扫码页面
        login_url = oauth.get_qq_url()             # 'https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=101518219&redirect_uri=http%3A%2F%2Fwww.meiduo.site%3A8000%2Foauth_callback&state=%2F'
        # 响应login_url给前端a标签的href属性
        return http.JsonResponse({'code': RETCODE.OK, 'error_message': 'OK', 'login_url': login_url})


# 处理用户QQ扫码登录后的回调逻辑 回调路由oauth_callback/
class QQAuthUserView(View):
    def get(self, request):
        # 获取QQ方返回的认证码code
        code = request.GET.get('code')
        if not code:
            return http.HttpResponseForbidden('获取code失败')

        # 创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI)
        try:                                         # 网络之间服务器访问，避免异常
            # 使用认证码code获取授权码access_token，get_access_token()内部封装了向QQ方发送请求获取授权码
            access_token = oauth.get_access_token(code)
            # 使用授权码access_token获取QQ方标识用户的唯一openid，get_open_id()同样封装了发送请求
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)           # 日志输出(等级error)
            return http.HttpResponseServerError('OAuth2.0认证失败')

        # 通过openid判断该QQ用户是否绑定过我们的用户
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 未查到说明openid未被绑定，则转到绑定页面，并将openid在模板中发给用户
            # openid由用户随着表单的提交一并发给后端，这样openid与该用户信息唯一对应！！！(好处：后端不用存储，也不用考虑如何将openid与用户对应起来)
            access_token_openid = generate_access_token(openid)                # 序列化加密
            context = {'access_token_openid': access_token_openid}
            return render(request, 'oauth_callback.html', context)
        else:
            # 查到说明openid已被绑定，则转到state=next，并做状态保持等
            # TODO 状态保持的是用户模型对象而不是QQ登录模型对象
            login(request, oauth_user.user)                                  # oauth_user.user表示从QQ登录模型实例中(通过外键)找到对应的用户模型对象
            # 响应：重定向到首页，并设置cookie以及做状态保持
            # response = redirect(reverse('contents:index'))
            # 响应：重定向到state=next，并设置cookie以及做状态保持
            next = request.GET.get('state')                                  # 取出多次请求一直携带的参数state
            response = redirect(next)
            response.set_cookie('username', oauth_user.user.username, max_age=3600 * 24 * 14)
            return response


    # 接收用户绑定信息post表单
    def post(self, request):
        # 接收参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        client_sms_code = request.POST.get('sms_code')
        access_token_openid = request.POST.get('access_token_openid')

        # 校验参数
        if not all([mobile, password, client_sms_code]):
            return http.HttpResponseForbidden('缺少必要参数')
        if not re.match(r'^1[34578]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号')
        if not re.match(r'^[a-zA-Z][0-9a-zA-Z]{7,19}$', password):
            return http.HttpResponseForbidden('请输入正确的密码')
        # 判断短信验证码是否一致
        redis_coon = get_redis_connection('verify_code')
        server_sms_code = redis_coon.get('sms_%s' % mobile)
        if server_sms_code is None:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '短信验证码已失效'})
        if not client_sms_code == server_sms_code:
            return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入的短信验证码有误'})

        # 判断openid是否有效：openid通过itsdangerous序列化后只有600秒有效期
        openid = check_access_token(access_token_openid)                      # 反序列化，解码
        if not openid:                            # 失效则返回错误信息
            return render(request, 'oauth_callback.html', {'openid_errmsg': 'openid已失效'})

        # 使用手机号查询数据库中用户是否存在
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:                                 # 手机号不存在则新建用户，然后绑定openid
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)             # 自动入库
        else:                                                     # 手机号存在说明用户存在，只需校验密码，然后绑定openid
            if not user.check_password(password):                 # 判断用户输入的密码是否正确
                return render(request, 'oauth_callback.html', {'account_errmsg': '账号或密码错误'})

        # 将新建用户或已存在用户绑定到openid，实际就是创建qq登录用户模型类对象
        try:
            # oauth_qq_user = OAuthQQUser(user=user, openid=openid)
            # oauth_qq_user.save()
            OAuthQQUser.objects.create(user=user, openid=openid)           # 封装上面两步，自动调用save入库
        except Exception as e:
            logger.error(e)
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': '账号或密码错误'})

        # 成功绑定则实现状态保持
        login(request, user)
        # 并重定向到state=next(从哪来，QQ登录后回哪去)，设置cookie并响应
        next = request.GET.get('state')
        response = redirect(next)
        response.set_cookie('username', user.username, max_age=3600 * 24 * 14)
        return response























































































