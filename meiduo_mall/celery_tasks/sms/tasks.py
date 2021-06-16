# 定义一个任务，名字必须为tasks.py  这是由autodiscover_tasks()中参数related_name参数指定的，否则需要自定义传参
from celery_tasks.sms.yuntongxun.new_singleton_sms import CCP
from . import constants
from celery_tasks.main import celery_app
import logging


logger = logging.getLogger('django')

# 发送短信验证码的任务(就是一个函数)
# 调用装饰器task装饰异步任务,保证celery识别任务
# bind保证任务对象作为第一个参数self传入
# retry_backoff指发送异常自动重试的次数，第n次重试时间间隔为：retry_backoff * 2^(n-1)秒，即第一次重试间隔2s，第二次间隔2s，第三次间隔4s
# max_retries指重试的上限次数
@celery_app.task(bind=True, name='send_sms_code', retry_backoff=3)            # name起别名，celery默认的别名很长
def send_sms_code(self, mobile, sms_code):                                    # 参数：任务对象,手机号，验证码

    try:
        # send_result 返回发送结果，成功返回0，失败返回-1
        send_result = CCP().send_message(tid=constants.SEND_SMS_TEMPLATE_ID, mobile=mobile, datas=(sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60))      # 300/60 = 5.0 而 300//60 = 5
        return send_result
    except Exception as e:
        logger.error(e)
        # 捕获到异常e则自动重试发送，重试次数上限为3次
        raise self.retry(exc=e, max_retries=3)

# 调用时 send_sms_code.delay(mobile, sms_code)







