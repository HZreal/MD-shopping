# celery程序入口
# Celery是Python开发的分布式任务调度模块，支持的消息服务有RabbitMQ、Redis等数据库
# celery通过消息进行通信，通常使用一个叫Broker(中间人)来协助client(任务的发出者)和worker(任务的处理者). clients发送消息到队列中，broker将队列中的信息派发给worker来处理
# Celery需要一种解决消息的发送和接受的方式，我们把这种用来存储消息的的中间装置叫做message broker, 也可叫做消息中间人，比如RabbitMQ， redis等
# RabbitMQ是一个功能完备，稳定的并且易于安装的broker. 它是生产环境中最优的选择
# Redis也是一款功能完备的broker可选项，但是其更可能因意外中断或者电源故障导致数据丢失的情况，开发可用

from celery import Celery
import os


# 发邮件时，为celery使用django配置文件而设置：celery进程与Django进程互相独立，celery进程无法直接读取到Django的配置文件settings
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'


# 创建Celery实例对象,即创建一个celery应用。内部封装了执行任务的装饰器task(self, *args, **opts)
celery_app = Celery('celery_instance')             # celery_instance用来标识这个实例，可不传，

# 加载配置：指定broker为redis
celery_app.config_from_object('celery_tasks.config')

# 注册任务：autodiscover_tasks的参数是一个列表
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])





# 协程运行在线程之上，当一个协程执行完成后，可以选择主动让出，让另一个协程运行在当前线程之上。协程并没有增加线程数量，只是在线程的基础之上通过分时复用的方式运行多个协程，
# 而且协程的切换在用户态完成，切换的代价比线程从用户态到内核态的代价小很多
# 协程只有在等待IO的过程中才能重复利用线程
# 协程注意事项：
        # 实际上操作系统并不知道协程的存在，它只知道线程，因此在协程调用阻塞IO操作的时候，操作系统会让线程进入阻塞状态，当前的协程和其它绑定在该线程之上的协程都会陷入阻塞而得不到调度，这往往是不能接受的。
        # 因此在协程中不能调用导致线程阻塞的操作。也就是说，协程只有和异步IO结合起来，才能发挥最大的威力。
# 总结：
        # 在有大量IO操作业务的情况下，我们采用协程替换线程，可以到达很好的效果，一是降低了系统内存，二是减少了系统切换开销，因此系统的性能也会提升
        # 在协程中尽量不要调用阻塞IO的方法，比如打印，读取文件，Socket接口等，除非改为异步调用的方式，并且协程只有在IO密集型的任务中才会发挥作用


# 消息队列是消息在传输的过程中保存消息的容器,现在主流消息队列有：RabbitMQ、ActiveMQ、Kafka等
# TODO rabbitMQ


# 在能够看到celery_tasks包的目录meiduo_mall下终端执行celery -A celery_tasks.main worker -l info 启动celery服务器
#  -A 指定入口，参数worker即celery执行者， -l info为日志等级
#  -c 指定并发的进程个数(默认每个CPU开4个)，比如1000个，但是进程过于耗费资源，可引入协程：即-P eventlet -c 1000

# 终端显示以下，并等待接收任务
# app:                       meiduo:0x41a8710
# transport:                 redis://192.168.94.131:6379/10
# concurrency:               4 (prefork)  即目前有四个并发进程等待任务，若开协程则如  1000(eventlet)
# task events:               OFF (enable -E to monitor tasks in this worker)
# queue队列：                . send_sms_code     .send_verify_email       显示要执行的任务
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
































