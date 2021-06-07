# 子应用verifications
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection           # django_redis使Django操作redis面向对象
from django import http
import random
import logging

from verifications.libs.captcha.captcha import captcha
from verifications import constants
from meiduo_mall.utils.response_code import RETCODE
from verifications.libs.yuntongxun.new_singleton_sms import CCP
from celery_tasks.sms.tasks import send_sms_code


# 创建日志器对象，参数是配置信息的key
logger = logging.getLogger('django')



# 生成图形验证码，返给前端，存入redis
class ImageCodeView(View):
    def get(self, request, uuid):
        # TODO uuid是唯一标识图形验证码所属用户，此时未注册，无法用用户名唯一标识！！！
        # 接收、校验参数(路径参数已正则校验格式)

        # 实现业务逻辑：
        # 生成图形验证码：通过captcha对象的generate_captcha()方法
        text, image = captcha.generate_captcha()
        # 保存图形验证码的text文本到redis的2号库
        redis_conn = get_redis_connection(alias='verify_code')                             # 参数alias类型str，指向redis配置信息CACHES中的key，默认是'default',即0号库，返回连接对象
        # redis_conn.setex('key', 'expires', 'value')                                      # 查看setex()命令
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)                                       # img_%s' % uuid 表示给uuid拼一个前缀，统一化

        # 返回响应
        return http.HttpResponse(content=image, content_type='image/jpg')



# 生成短信验证码
class SMSCodeView(View):
    def get(self, request, mobile):
        # 接收参数
        client_image_code = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        # 校验参数是否齐全，无需单独校验，mobile经过正则校验，client_image_code有问题，下面对比校验就会错误提示，uuid有问题，数据库取图形验证码为空就会错误提示
        if not all([client_image_code, uuid]):
            return http.HttpResponseForbidden({'code': RETCODE.NECESSARYPARAMERR, 'error_mesaage': '缺少必要参数'})        # 进入前端回调的catch

        redis_conn = get_redis_connection('verify_code')

        # 判断用户是否频繁发送短信验证码(发送短信验证码主体逻辑之前判断)
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:                       # 错误码4002
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'error_mesaage': '短信发送过于频繁'})

        # 连接Redis,查图形验证码
        # redis_conn = get_redis_connection('verify_code')               # 判断是否频繁发送的逻辑也需要用到连接对象，此代码提前
        server_image_code = redis_conn.get('img_%s' % uuid)              # 提取到内存
        # 图形验证码过期或者不存在，错误码4001
        if server_image_code is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'error_mesaage': '图形验证码失效'})
        # 图形验证码已提取到内存，需将库中的删除(避免用户恶意测试)
        try:
            redis_conn.delete('img_%s' % uuid)
        except Exception as e:
            print(e)
            # logger.error(e)
        # 校验用户输入的图形验证码和库中的是否相同,     py3中从redis存入取出数据都是byte类型(存取速度快)
        server_image_code = server_image_code.decode()                           # 将byte转str   linux用utf8
        if not client_image_code.lower() == server_image_code.lower():           # 错误码4001
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'error_mesaage': '图形验证码输入有误'})

        # TODO 生成的6位短信验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)                         # 手动输出日志
        print(sms_code)
        # 存储到redis的2号库，与图形验证码存库一样
        redis_conn = get_redis_connection('verify_code')
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 同时存一个有过期时间的标记flag, 标记未过期期间，拒绝用户的发短信请求。
        # redis_conn.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # 创建redis管道，提高请求访问性能，优化效率
        pl = redis_conn.pipeline()
        # 将需要执行的多条命令按顺序添加到管道队列中
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 由管道去向redis请求执行
        pl.execute()

        # 发送短信验证码(单例)
        # CCP().send_message(tid=constants.SEND_SMS_TEMPLATE_ID, mobile='15926750521', datas=(sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60))      # 300/60 = 5.0 而 300//60 = 5
        # 交给celery消息队列完成发送短信验证码：参数交给delay，再传给被装饰了的任务函数send_sms_code
        send_sms_code.delay(mobile='15926750521', sms_code=sms_code)

        # 返回响应
        return http.JsonResponse({'code': RETCODE.OK, 'error_mesaage': '发送短信验证码成功'})






































































