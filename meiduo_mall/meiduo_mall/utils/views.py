from django.contrib.auth.mixins import LoginRequiredMixin
from django import http
from meiduo_mall.utils.response_code import RETCODE


# 自定义判断用户是否登录的扩展类
class LoginRequiredJSONMixin(LoginRequiredMixin):

    # 父类LoginRequiredMixin已经做了用户是否登录的判断(在dispatch方法中)，未登录则进行handle_no_permission处理
    # 根据需求，这里只需重写handle_no_permission方法，即可实现用户未登录的逻辑处理
    def handle_no_permission(self):
        # 直接响应json数据
        return http.JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': '用户未登录'})


'''
AccessMixin类中的方法：
def handle_no_permission(self):
    if self.raise_exception or self.request.user.is_authenticated:
        raise PermissionDenied(self.get_permission_denied_message())

class LoginRequiredMixin(AccessMixin): 
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
        
'''


















