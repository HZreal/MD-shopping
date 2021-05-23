import re
from django.contrib.auth.backends import ModelBackend
from users.models import User

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings
from users import constants

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

# 自定义用户认证后端，继承自系统默认后端，实现多账号登录
class UsernameMobileBackend(ModelBackend):
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


# 生成邮件验证地址
def generate_email_url(user):

    s = Serializer(settings.SECRET_KEY, constants.VERIFY_EMAIL_TOKEN_EXPIRES)

    data = {
        'user_id': user.id,
        'email': user.email,
    }

    # 序列化：调用dumps方法进行序列化，返回类型是byte
    token = s.dumps(data).decode()

    # 拼接邮件验证地址
    verify_email_url = settings.EMAIL_VERIFY_URL + '?token=' + token

    return verify_email_url


def check_verify_email_token(token):
    # 反序列化token
    s = Serializer(settings.SECRET_KEY, constants.VERIFY_EMAIL_TOKEN_EXPIRES)

    try:
        data = s.loads(token)
    except BadData:                             # 密文过期
        return None
    else:                                       # 未过期
        # 取数据
        user_id = data.get('user_id')
        email = data.get('email')
        # 查库看是否存在这样的用户
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user






















































