from django.contrib.auth.mixins import LoginRequiredMixin
from django import http
from meiduo_mall.utils.response_code import RETCODE



# LoginRequiredMixin类定义了dispatch方法，实现了is_authenticated认证以及调用super().dispatch()
# 通过as_view()原理可知，优先调用LoginRequiredMixin的dispatch方法，然后调用View类的dispatch()方法进入到UserInfoView实例的get()
# 因此用户未认证会被LoginRequiredMixin类的dispatch方法引导到handle_no_permission()进行处理，即不会进入此视图类，但是会被重定向到LOGIN_URL指定的地址(通常是登录页面)，当用户完成登录又重定向到next，可回到此类视图UserInfoView


# 自定义判断用户是否登录的扩展类：因为是axios请求无需重定向，因此判断用户未登录时，重写handle_no_permission方法即可
class LoginRequiredJSONMixin(LoginRequiredMixin):

    # 根据需求，这里只需重写handle_no_permission方法，即可实现用户未登录的逻辑处理
    def handle_no_permission(self):
        # 直接响应json数据
        return http.JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': '用户未登录'})





















