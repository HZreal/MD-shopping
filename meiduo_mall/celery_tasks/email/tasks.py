from django.core.mail import send_mail
from django.conf import settings
from celery_tasks.main import celery_app
import logging

logger = logging.getLogger('django')


# 定义发送验证邮件的任务
# bind保证任务对象作为第一个参数self传入，因为调用时传的参数是位置参数email, verify_email_url
# retry_backoff指发送异常自动重试的次数，第n次重试时间间隔为：retry_backoff * 2^(n-1)秒，即第一次重试间隔2s，第二次间隔2s，第三次间隔4s
# max_retries指重试的上限次数
@celery_app.task(bind=True, name='send_verify_email', retry_backoff=3)
def send_verify_email(self, to_email, verify_url):
    subject = "好又多购物邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用好又多购物。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
    try:
        # 发邮件
        send_mail(subject, '', settings.EMAIL_FROM, [to_email], html_message=html_message)
    except Exception as e:
        logger.error(e)
        # 捕获到异常e则自动重试发送，重试次数上限为3次
        raise self.retry(exc=e, max_retries=3)


# if __name__ == '__main__':
#     email = 'huangzhen_happy@163.com'
#     verify_url = 'www.baidu.com'
#     send_verify_email.delay(email, verify_url)












