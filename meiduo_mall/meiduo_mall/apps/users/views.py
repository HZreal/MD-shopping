from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django import http
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
# from models import User                                  # 导入模块时找不到，users不在导包路径，系统找不到users.model.py
from users.models import User, Address                     # 运行时不报错，程序运行时已进行apps/插入导包操作，但未运行时此处会报红色编辑错误(编辑器pycharm找不到)，只需设置apps标记为源根，就不会报编辑错误
from users.utils import generate_email_url, check_verify_email_token
from users import constants
from django.views import View
import re, json, logging
from django.db import DatabaseError
from meiduo_mall.utils.response_code import RETCODE                      # 将工程根meiduo_mall标记为源根，则编辑器不会报红，不论编辑器是否报红，解释器能找到模块就行
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from django_redis import get_redis_connection
from celery_tasks.email.tasks import send_verify_email
from goods.models import SKU
from carts.utils import merge_cart_cookies_redis



# 创建日志器
logger = logging.getLogger('django')

# 注册
class RegisterView(View):
    # 前后端不分离，由后端提供注册页面
    def get(self, request):
        return render(request, 'register.html')

    # 后端用户注册逻辑接口
    def post(self,request):
        # 接收form表单数据：Django可以自动解析表单数据，故可用request.POST直接获取数据。json数据只能request.body获取，还要解码
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
            return render(request, 'register.html', {'sms_error_message': '短信验证码无效'})
        if not client_sms_code == server_sms_code.decode():
            return render(request, 'register.html', {'sms_error_message': '输入短信验证码有误'})

        # 保存用户注册数据
        # 调用Django用户模型类方法create_user()，内置密码加密，存储到库等操作
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', context={'register_error_message': '注册失败'})

        # return render(request, 'register.html', context={'register_error_message': '注册失败'})             # 测试注册失败错误提示信息(页面整体刷新)

        # 实现状态保持(保存注册数据成功入库之后，响应之前)
        # 需求一：注册成功后即表示用户登入成功，转入首页，那么此时在注册成功后就实现状态保持(这里采用)
        # 需求二：注册成功后不表示用户登入成功，转入登录页面让用户登录，那么此时不用在注册成功后实现状态保持，而是等用户登录后转入首页才实现状态保持
        # Django用户认证系统(auth子应用)提供了login()方法。封装了写入session的操作，帮助我们快速登入一个用户，并实现状态保持，详看源码
        login(request, user)

        # 响应结果：注册成功，重定向到首页路径 '/'  给用户传sessionid, csrftoken等cookie信息
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=3600 * 24 * 14)
        return response


# 接收axios请求，判断注册的用户名是否重复
class UsernameCountView(View):
    def get(self, request, username):                 # username接收请求路由url的路径参数
        # 接收校验参数：路径参数正则格式校验
        # 使用username查询数据库中用户名为username的记录条数,
        count = User.objects.filter(username=username).count()

        # 响应结果：发送json数据
        return http.JsonResponse({'status': RETCODE.OK, 'error_mesaage': 'OK', 'count': count})


# 接收axios请求，判断注册的手机号是否重复
class MobileCountView(View):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'status': RETCODE.OK, 'error_message': 'OK', 'count': count})


# 登录
class LoginView(View):
    # 提供用户登录页面
    def get(self, request):
        return render(request, 'login.html', )

    # 实现用户登录逻辑
    def post(self, request):
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # 校验参数
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^[0-9a-zA-Z_]{5,20}$', username):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')
        if not re.match(r'^[a-zA-Z][0-9a-zA-Z]{7,19}$', password):
            return http.HttpResponseForbidden('请输入正确的密码')

        # 认证用户
        # user = User.objects.get(username=username)
        # user.check_password(password)                                         # 父类提供的校验密码方法
        # 系统用户认证后端提供authenticate认证方法，封装了check_password()等操作，定义在auth.backends.ModelBackend类中，但无法用手机号认证，需要需要自定义用户认证后端，重写authenticate方法
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_error_msg': '账户或密码错误'})

        # 状态保持：login方法封装了写入session(会话保持)和写入cookie(sessionid)的操作
        login(request, user)

        # 使用remembered确定状态保持的周期时长，实现记住登录
        if remembered != 'on':                                          # 用户没有记住登录，则状态保持在浏览器会话结束后就销毁
            request.session.set_expiry(0)                               # 单位是秒
        else:                                                           # 用户记住登录，则状态保持周期为两周(默认，可设定)
            request.session.set_expiry(None)

        # 取出查询字符串参数next
        next = request.GET.get('next')
        if next:
            response = redirect(next)                      # 若有next,则直接重定向到next对应的路由
        else:
            response = redirect(reverse('contents:index'))

        # 为了实现首页右上角展示用户名信息，将用户名缓存到cookie中,由前端vue调用cookie信息得到username
        response.set_cookie('username', user.username, max_age=3600 * 24 * 14)

        # 用户登陆成功，合并cookie购物车到redis购物车
        response = merge_cart_cookies_redis(request, user, response)

        # 响应结果,重定向到首页
        return response


# 用户退出登录
class LogoutView(View):

    def get(self, request):
        # 清除状态保持，logout方法封装了清除服务器端session信息(redis的1号库)，以及cookie中sessionid操作
        logout(request)

        # 清除cookie中的username，否则即使退出登录还是会显示用户名，因为用户名的显示是由前端vue渲染的
        response = redirect(reverse('contents:index'))
        response.delete_cookie('username')

        # 响应结果
        return response


# 用户中心：需要验证用户登入才可进入(有多种方式，其他方式写在utils.view里)
# 方式一：继承父类LoginRequiredMixin(auth子应用)
# LoginRequiredMixin类定义了dispatch方法，实现了is_authenticated认证以及调用super().dispatch()
# 通过as_view()原理可知，优先调用LoginRequiredMixin的dispatch方法，然后调用View类的dispatch()方法分发进入到UserInfoView实例的get()
# 因此用户未认证会被LoginRequiredMixin类的dispatch方法引导到handle_no_permission()进行处理，即不会进入此视图类，但是会被重定向到LOGIN_URL指定的地址(通常是登录页面)，当用户完成登录又重定向到next，可回到此类视图UserInfoView
class UserInfoView(LoginRequiredMixin, View):
    # 提供用户中心页面
    def get(self, request):
        # if request.user.is_authenticated:
        #     return render(request, 'user_center_info.html')
        # else:
        #     return redirect(reverse('users:login'))
        # 以上验证登录逻辑因继承LoginRequiredMixin类自动验证

        # LoginRequiredMixin类有两个配置参数(详看源码)
        # login_url = '/login/'                 # 验证失败重定向的路由，在配置文件dev.py中设置，则每个需要验证的类视图不用写
        # redirect_field_name = REDIRECT_FIELD_NAME = 'next'      # 默认是next，完成登录又重定向到next，即回到此类视图

        # 当通过LoginRequiredMixin的验证，说明此用户已登录，那么request.user就是当前登录用户，即无需查库获取用户对象
        # 将用户信息通过模板显示在页面：整体刷新
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }

        return render(request, 'user_center_info.html', context)


# 方式二：用装饰器login_required，可以直接装饰函数视图，此处为类视图无法直接装饰，有以下2种方式：
# 1.装饰as_view()方法，即路由改为 path('info/', login_required(views.UserInfoView.as_view()), name='info'),
# class UserInfoView(View):
#     def get(self, request):
#         pass
# 2.定义obejct子类封装login_required装饰器，在dispatch分发之前做login_required装饰验证
# from django.contrib.auth.decorators import login_required
# class LoginRequiredMixin2(object):            # 继承自object而非View，这样不依赖任何视图，复用性强
#     @classmethod
#     def as_view(cls, **initkwargs):            # 自定义as_view，调用父类的as_view()方法
#         view = super().as_view()
#         return login_required(view)
# class UserInfoView(LoginRequiredMixin2, View):
#     def get(self, request):
#         pass

# 方式三：使用method_decorator装饰器(解决装饰器不能直接装饰类视图函数)，这是在dispatch分发之后验证
# 第一个参数是：装饰器本身及它的参数；第二个参数是：给这个类中的哪个函数装饰
# from django.contrib.auth.decorators import login_required
# from django.utils.decorators import method_decorator
# class LoginRequiredMixin3(object):
#     @method_decorator(login_required(login_url='/login/'))
#     def dispatch(self, request, *args, **kwargs):
#         return super(LoginRequiredMixin3, self).dispatch(request, *args, **kwargs)
# class UserInfoView(LoginRequiredMixin3, View):
#     def get(self, request):
#         pass




# 接收axios请求，添加邮箱
# 检测到用户未登录时，不会进入此视图函数，而是会进入LoginRequiredJSONMixin中执行重写函数handle_no_permission()
# 若用户处于未登录状态(比如手动删除cookie)，则根据需求返回json数据(错误码4101)，此时不会进入此视图函数
class EmailView(LoginRequiredJSONMixin, View):

    # put请求：数据库更新字段数据
    def put(self, request):
        # 接收参数：请求体数据保存在body中，对于非表单类型请求体数据，Django无法自动解析,通过request.body获取最原始的请求体数据(bytes类型)，自行根据请求体格式(JSON、XML等)进行解析
        body = request.body
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

        # 生成邮件验证地址(itdangerous序列化)
        verify_email_url = generate_email_url(request.user.id, email)

        # 让celery异步发送验证邮件
        send_verify_email.delay(email, verify_email_url)

        # 成功添加邮箱入库后响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加成功'})


# 接收用户邮件验证
class VerifyEmailView(View):
    def get(self, request):
        # 接收参数
        token = request.GET.get('token')
        # 校验参数
        if not token:
            return http.HttpResponseForbidden('缺少必要参数token')

        # 通过token反序列化解码并查库返回的用户对象
        user = check_verify_email_token(token)
        if not user:
            return http.HttpResponseForbidden('无效的token')

        # 将用户的email_active字段设置为True，表示用户邮箱已激活
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('激活邮箱失败')

        # 响应：重定向到用户中心
        return redirect(reverse('users:info'))


# 展示收货地址页面，同时通过查询显示当前登录用户收货地址信息
class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        # 显示的用户地址，查询条件为：属于当前登录用户且逻辑删除为False
        addresses = Address.objects.filter(user=request.user, is_deleted=False)

        # !!! Django模板与jinja2都能解析模型类，但是json和vue.js无法识别，需要解析(将模型类列表转成字典列表)
        # 这里用jinja2模板传数据到前端，然后由vue进行渲染，故也需要数据转换
        # 列表推导式将用户地址对象列表转成字典列表
        address_list = [{'id': address.id,
                         'title': address.title,
                         'receiver': address.receiver,
                         'province': address.province.name,
                         'city': address.city.name,
                         'district': address.district.name,
                         'place': address.place,
                         'mobile': address.mobile,
                         'tel': address.tel,
                         'email': address.email,
                         } for address in addresses]
        # a = request.user.default_address             # 用户的默认地址对象
        # c = request.user.default_address.id          # 用户对象外键返回默认地址对象，默认地址对象的id = 1
        # b = request.user.default_address_id          # 用户对象的default_address_id字段 = 默认地址id = 1

        # 构造模板数据
        context = {
            'default_address_id': request.user.default_address_id,                 # 默认地址的id：前端获取并显示
            'addresses': address_list,
        }
        # 响应页面
        return render(request, 'user_center_site.html', context)


# 接收用户新增地址的axios请求
class AddressCreateView(LoginRequiredJSONMixin, View):
    def post(self, request):
        # 首先判断用户地址数量是否超过上限(超过上限直接错误返回，参数都无需接收校验)：查询当前登录用户的地址数量
        # count = Address.objects.filter(user__exact=request.user).count()
        # count = Address.objects.filter(user_id__exact=request.user.id).count()
        count = request.user.addresses.count()           # 一查多，Address模型类外键user，设置了related_name=addresses
        if count > constants.USER_ADDRESS_COUNTS_LIMIT:                      # 20
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超出用户地址数量上限'})

        # 接收参数
        data_dict = json.loads(request.body.decode())
        receiver = data_dict.get('receiver')
        province_id = data_dict.get('province_id')
        city_id = data_dict.get('city_id')
        district_id = data_dict.get('district_id')
        place = data_dict.get('place')
        mobile = data_dict.get('mobile')
        tel = data_dict.get('tel')
        email = data_dict.get('email')
        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place,mobile]):
            return http.HttpResponseForbidden('缺少必要参数')
        if not re.match(r'^1[34578]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 保存用户传入的地址信息
        try:
            # 初始化类关键字参数外键名还是外键名
            # address = Address(user=request.user, receiver=receiver, province=province_id, city=city_id, district=district_id, place=place, mobile=mobile)
            # address.save()
            address = Address.objects.create(                       # 外键指向的是对象，外键对应的字段存的是对应对象的id
                # user = request.user,
                user_id = request.user.id,
                title = receiver,
                receiver = receiver,
                # province = province_id,                          # 会报错，province = province_id对象
                province_id = province_id,                         # 因为传过来的都是id，因此用字段存
                city_id = city_id,                                 # 用字段设置，必须是调用objects管理器才可用，
                district_id = district_id,
                place=place,
                mobile=mobile,
                tel = tel,
                email = email,
            )

            # 如果用户没有默认地址则将当前地址设置为默认地址
            if not request.user.default_address:
                request.user.default_address = address                # 将新增的地址对象赋给User对象的外键default_address，数据库该字段default_address_id自动存储的是新增地址对象的id
                request.user.save()
        except DatabaseError as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 构造当前新增地址的字典数据传给前端
        address_dict = {
            'id': address.id,
            'title': address.title,
            'receiver': address.receiver,
            'province': address.province.name,
            'city': address.city.name,
            'district': address.district.name,
            'place': address.place,
            'mobile': address.mobile,
            'tel': address.tel,
            'email': address.email,
        }
        # 响应新增地址的结果：需要将新增地址信息的json数据返回给前端渲染
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


# 更新和删除用户地址信息
class UpdateDestroyAddressView(LoginRequiredJSONMixin, View):
    # 修改地址信息
    def put(self, request, address_id):
        # 接收参数
        data_dict = json.loads(request.body.decode())
        receiver = data_dict.get('receiver')
        province_id = data_dict.get('province_id')
        city_id = data_dict.get('city_id')
        district_id = data_dict.get('district_id')
        place = data_dict.get('place')
        mobile = data_dict.get('mobile')
        tel = data_dict.get('tel')
        email = data_dict.get('email')
        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必要参数')
        if not re.match(r'^1[34578]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 使用最新的地址信息覆盖指定的旧的地址信息
        try:
            Address.objects.filter(id=address_id).update(           # update()返回的是修改的记录条数
                user_id=request.user.id,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email,
            )
            # 修改完成后，在数据库中取出该收货地址对象
            address = Address.objects.get(id=address_id)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '修改地址失败'})

        # 构造修改地址的字典数据传给前端
        address_dict = {'id': address.id,
                        'title': address.title,
                        'receiver': address.receiver,
                        'province': address.province.name,
                        'city': address.city.name,
                        'district': address.district.name,
                        'place': address.place,
                        'mobile': address.mobile,
                        'tel': address.tel,
                        'email': address.email,
                        }
        # 响应修改地址的结果：需要将新增地址信息的json数据返回给前端渲染
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改地址成功', 'address': address_dict})


    # 删除地址信息
    def delete(self, request, address_id):
        try:
            address = Address.objects.get(id=address_id)
            address.is_deleted = True                            # 实现指定地址的逻辑删除
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

        # 成功删除后的响应
        # 前端收到状态码为0时，调用splice(index, 1)方法删除对象数组addresses中当前对象
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})


# 设置默认地址
class SetDefaultAddressView(LoginRequiredJSONMixin, View):
    def put(self, request, address_id):
        try:
            # 用地址id查库返回当前地址对象
            address = Address.objects.get(id=address_id)
            # 设置用户对象的属性(外键)default_address为当前地址对象
            request.user.default_address = address
            request.user.save()

        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})
        # 成功设置后响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})


# 修改收货地址标题
class UpdateAddressTitleView(LoginRequiredJSONMixin, View):
    def put(self, request, address_id):
        # 接收参数：用户输入的title内容放在请求体body中
        data_dict = json.loads(request.body.decode())
        title = data_dict.get('title')
        # 校验参数
        if not title:
            return http.HttpResponseForbidden('缺少必要参数')

        # 修改地址标题
        try:
            address = Address.objects.get(id=address_id)
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置地址标题失败'})
        # 成功设置后响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置地址标题成功'})


# 修改密码视图
class ChangePasswordView(LoginRequiredMixin, View):
    # 显示修改密码界面
    def get(self, request):
        return render(request, 'user_center_pass.html')

    # 接收用户修改密码的表单并处理
    def post(self, request):
        # 接收参数
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')

        # 校验参数
        if not all([old_password, new_password, new_password2]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 校验原始密码，判断是否是该用户
        if not re.match(r'^[A-Za-z][A-Za-z0-9]{7,19}$', old_password):
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg':'原始密码错误'})
        try:
            # user = User.objects.get(id=request.user.id)
            # user.check_password(old_password)
            result = request.user.check_password(old_password)             # 校验成功返回True，失败则返回False
            if not result:
                return render(request, 'user_center_pass.html', {'origin_pwd_errmsg': '原始密码错误'})
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg':'原始密码错误'})

        # 校验新密码
        if not re.match(r'^[A-Za-z][A-Za-z0-9]{7,19}$', new_password):
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg':'密码最少8位，最长20位'})
        if not new_password == new_password2:
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg':'两次输入的密码不一致'})

        # 将新密码保存入库
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg':'修改密码失败'})

        # 密码被修改则应立即清除状态保持(清除session以及cookie中的sessionid等)
        logout(request)

        # 返回至登录页面，同时清理cookie信息
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')
        return response


# 商品sku详情页面接收axios请求保存/查询用户浏览记录
class UserBrowseHistory(LoginRequiredJSONMixin, View):
    # 保存用户浏览记录(用户访问某sku详情页面，页面加载完成则会自动转入此post)
    def post(self, request):
        # 接收参数
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        # 校验参数
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')

        # 保存sku_id到redis数据库3号库
        redis_conn = get_redis_connection('history')
        # 用管道操作redis：以下操作命令需依次进行，任何一个卡顿都影响效率
        pl = redis_conn.pipeline()
        # 选择redis的list数据类型，自定义key
        key = 'history_%s' % request.user.id
        # 先去重复：若库中存在，则删除库中的sku_id    lrem(key,count,value)表示从左(count>0)/从右(count<0)删除count个值等于value的元素,count=0时表示删除所有值等于value的元素，即去重
        pl.lrem(key, 0, sku_id)
        # 再保存(左插)：最近浏览的sku排在前面
        pl.lpush(key, sku_id)
        # 最后截取：取前5个予以展示， ltrim(key, start, stop)表示截取start到stop的元素
        pl.ltrim(key, 0, 4)
        pl.execute()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


    # 查询获取用户浏览记录(用户个人信息中心页面展示)
    def get(self, request):
        # 查询redis取出该用户最近浏览sku_id列表
        redis_conn = get_redis_connection('history')
        sku_id_list = redis_conn.lrange('history_%s' % request.user.id, 0, -1)        # 0, 4 亦可
        # 循环查询每个sku_id对应的sku信息，并将模型类转字典
        skus = []
        for sku_id in sku_id_list:
            try:
                sku = SKU.objects.get(id=sku_id)
            except SKU.DoexNotExist:
                return http.HttpResponseServerError('参数错误')
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url,
            })

        # 返回响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'skus': skus})











































































































































