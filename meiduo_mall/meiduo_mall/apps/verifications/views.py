from django.shortcuts import render
from django.views import View
from verifications.libs.captcha.captcha import captcha
from verifications import constants
from django_redis import get_redis_connection                                              # django_redis时Django操作redis面向对象
from django import http


class ImageCodeView(View):
    def get(self, request, uuid):
        # uuid是唯一标识图形验证码所属用户，此时未注册，无法用用户名唯一标识
        # 接收、校验参数(路径参数已正则校验)

        # 实现业务逻辑：
        # 生成图形验证码：通过captcha对象的generate_captcha()方法
        text, image = captcha.generate_captcha()
        # 保存图形验证码的text文本到redis的2号库
        redis_conn = get_redis_connection(alias='verify_code')                             # 参数alias类型str，指向redis配置信息CACHES中的key，默认是'default',即0号库，返回连接对象
        # redis_conn.setex('key', 'expires', 'value')                                      # 查看setex()命令
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)                                       # img_%s' % uuid 表示给uuid拼一个前缀，统一化

        # 返回响应
        return http.HttpResponse(content=image, content_type='image/jpg')




































































