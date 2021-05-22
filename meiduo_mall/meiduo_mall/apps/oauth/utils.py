# 对用户openid进行加密解密
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from oauth import constants
from itsdangerous import BadData



# 签名，序列化openid
def generate_access_token(openid):

    # 创建序列化对象：第一个参数是秘钥，越复杂越安全。第二个参数是过期时间
    s = Serializer(settings.SECRET_KEY, constants.ACCESS_TOKEN_EXPIRES)

    # 准备待序列化的字典数据
    data = {'openid': openid}

    # 调用dumps方法进行序列化，返回类型是byte
    token = s.dumps(data)

    # 转成字符串并返回
    return token.decode()


# 反序列化，解码
def check_access_token(access_token_openid):
    s = Serializer(settings.SECRET_KEY, constants.ACCESS_TOKEN_EXPIRES)

    try:
        data = s.loads(access_token_openid)
    except BadData:                                 # 密文过期
        return None
    else:                                           # 未过期，返回明文
        return data.get('openid')



