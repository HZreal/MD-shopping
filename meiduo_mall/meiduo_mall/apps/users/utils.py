# 自定义用户认证后端：实现多账号登录
import re

from django.contrib.auth.backends import ModelBackend
from users.models import User

# 通过账号获取用户(封装过程)
def get_user_by_account(account):
    # 校验username是用户名还是手机号
    try:  # 查数据库
        if re.match(r'^1[34578]\d{9}$', account):                   # username == 手机号
            user = User.objects.get(mobile=account)
        else:                                                       # username == 用户名
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user

# 自定义用户认证后端，继承自系统默认后端
class UsernameMobileBackend(ModelBackend):

    # Authenticates against settings.AUTH_USER_MODEL.
    # 默认是 AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
    # 需要在配置信息中设置自定义用户认证后端

    # 重写父类的authenticate()方法
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 使用账号查询用户
        user = get_user_by_account(username)          # 用户名或者手机号查询返回的用户对象

        # 如果查到，则校验密码是否正确
        if user and user.check_password(password):
            # 返回user
            return user
        else:
            return None







































































