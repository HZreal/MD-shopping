
from django.shortcuts import render
from django import http
# from models import User           # 导入模块时找不到，users不在导包路径，系统找不到users.model.py
from users.models import User       # 运行时不报错，程序运行时已进行apps/插入导包操作，但未运行时此处会报红色编辑错误(编辑器pycharm找不到)，只需设置apps标记为源根，就不会报编辑错误

from django.views import View
import re
from django.db import DatabaseError

class RegisterView(View):
    # 获取注册页面
    def get(self, request):
        return render(request, 'register.html')

    # 后端用户注册逻辑接口
    def post(self,request):
        # 接收请求数据:form表单:Django可以自动解析表单数据，故可用request.POST直接获取数据。json数据只能request.body获取，还要解码
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')

        # 校验参数:对前端数据再次校验，保证后端安全，避免黑客绕过前端发送数据。前后端校验逻辑相同
        # 判断参数：1.参数是否齐全，2.用户名合法，3.密码合法，4.确认密码相同，5.手机号合法，6.勾选协议
        # 只要缺少一个参数，或者参数格式有误，禁止此次请求，保证后端后续逻辑安全
        if not all([username, password, password2, mobile, allow]):                 # all([])判断列表元素是否为空，只要有一个为空则返回false
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

        # 保存用户注册数据
        # create_user()方法内置密码加密，存储到库等操作，访问了外部资源用try
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', context={'register': '注册失败'})


        # 响应结果
        return http.HttpResponse('注册成功，重定向到首页')






















































































































































































































































