# celery程序入口

from celery import Celery

# 创建Celery实例对象,内部封装了执行任务的装饰器task(self, *args, **opts)
celery_app = Celery('meiduo')      # meiduo用来表示这个实例，可不传，


# 加载配置
celery_app.config_from_object('celery_tasks.config')


# 注册任务：autodiscover_tasks的参数是一个列表
celery_app.autodiscover_tasks(['celery_tasks.sms'])

# 消息队列是消息在传输的过程中保存消息的容器,现在主流消息队列有：RabbitMQ、ActiveMQ、Kafka等等
# TODO rabbitMQ

# 在能够看到celery_tasks包的目录meiduo_mall下终端执行celery -A celery_tasks.main worker -l info启动celery服务器
#  -A 指定入口，参数worker即celery执行者， -l info为日志等级

# 终端显示以下，并等待接收任务
# app:                       meiduo:0x41a8710
# transport:                 redis://192.168.94.131:6379/10
# concurrency:               4 (prefork)  即目前有四个并发进程等待任务，可指定数量(后续)
# task events:               OFF (enable -E to monitor tasks in this worker)
# queue队列：                . send_sms_code            显示要执行的任务
#  Connected to redis://192.168.94.131:6379/10
#  celery@DESKTOP-8GJGA4C ready

# 当进程接收到任务时：
# Received task: send_sms_code[eacf7e5a-e3cd-4fcb-91dd-d230947f7cae]         任务id
# Sign plaintext:  ...
# Authorization plaintext: ...
# Request url: 8a216da87955ba1901796fa1d38a0a80/SMS/TemplateSMS?sig=BE57C99FDCCB746E49FA9FC180C86A7F
# Request headers: {'Content-Type': 'application/json;charset=utf-8', 'Accept': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': b'OGEyMTZkYTg3OTU1YmExOTAxNzk2ZmExZDM4YTBhODA6MjAyMTA1MTcxNTI3NDM='}
# Request body: {"to": "15926750521", "appId": "8a216da87955ba1901796fa1d4940a86", "templateId": 1, "datas": ["659557", 5]}
# Response body: {"statusCode":"000000","templateSMS":{"smsMessageSid":"c0ed984491524ef18ebc13294604d725","dateCreated": "20210517152744"}}
# Task send_sms_code[eacf7e5a-e3cd-4fcb-91dd-d230947f7cae] succeeded in 0.5150000001303852s: 0    (状态码为0即成功)
































