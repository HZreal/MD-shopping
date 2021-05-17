# 定义任务，名字必须为tasks.py  因为autodiscover_tasks()中参数related_name参数指定的，否则需要自定义传参

from celery_tasks.sms.yuntongxun.new_singleton_sms import CCP
from . import constants
from celery_tasks.main import celery_app


# 发送短信验证码的任务(就是一个函数)
# 调用装饰器task装饰异步任务,保证celery识别任务
@celery_app.task(name='send_sms_code')           # name起别名，celery默认的别名很长
def send_sms_code(mobile, sms_code):     # 参数：手机号，验证码

    # send_result 返回发送结果，成功返回0，失败返回-1
    send_result = CCP().send_message(tid=constants.SEND_SMS_TEMPLATE_ID, mobile=mobile, datas=(sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60))      # 300/60 = 5.0 而 300//60 = 5
    return send_result


# 调用时 send_sms_code.delay(mobile, sms_code)







