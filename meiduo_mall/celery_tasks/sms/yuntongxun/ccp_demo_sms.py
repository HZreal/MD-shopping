# -*- coding:utf-8 -*-
# import ssl
# ssl._create_default_https_context =ssl._create_stdlib_context # 解决Mac开发环境下，网络错误的问题
from celery_tasks.sms.yuntongxun.CCPRestSDK import REST

_accountSid = '8a216da87955ba1901796a40d5d50975'                             # 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID
_accountToken = '6bc212ea08c5413c84e9c3513f24f5ca'                           # 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN
_appId = '8a216da87955ba1901796a40d6d7097c'                                  # 请使用管理控制台首页的APPID或自己创建应用的APPID
_serverIP = 'sandboxapp.cloopen.com'                                         # 说明：请求地址，生产环境配置成app.cloopen.com
_serverPort = "8883"                                                         # 说明：请求端口 ，生产环境为8883
_softVersion = '2013-12-26'                                                  # 说明：REST API版本号保持不变

# 云通讯官方提供的发送短信代码实例
# 参数：1.手机号码to 2.内容数据datas，格式为数组，例如：{'12','34'} 3.tempId 模板Id
# def sendTemplateSMS(to, datas, tempId):
#     rest = REST(_serverIP, _serverPort, _softVersion)                        # 初始化REST SDK
#     rest.setAccount(_accountSid, _accountToken)
#     rest.setAppId(_appId)
#
#     result = rest.sendTemplateSMS(to, datas, tempId)
#     print(result)


# 单例模式：目的是确保某一个类只有一个实例存在
# 单例模式保证了在程序的不同位置都可以且仅可以取到同一个对象实例：如果实例不存在，会创建一个实例；如果已存在就会返回这个实例
# 类创建实例对象并赋给类的属性_instace中，没有_instance动态创建
class CCP(object):           # 单例类
    # 单例的初始化方法
    def __new__(cls, *args, **kwargs):                 # 会在__init__之前调用

        if not hasattr(cls, '_instance'):
            # 单例不存在则实例化创建单例cls._instance，super()保证了不会调用此处的__new__()，而是基类的
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)

            # 初始化SDK，创建了一个REST对象，
            # 并保存在单例的属性中(单例cls._instance原本没有rest这个属性，动态新建)，便于调用单例类的属性rest就可以调用到REST对象
            rest = REST(_serverIP, _serverPort, _softVersion)
            cls._instance.rest = rest

            # 调用单例的属性cls._instance.rest即是调用REST对象
            cls._instance.rest.setAccount(_accountSid, _accountToken)
            cls._instance.rest.setAppId(_appId)

        return cls._instance     # 返回单例

    # 定义实例对象方法(不是类方法，是类方法就失去单例的意义) 实现单例类发送短信验证码
    def send_template_sms(self, to, datas, tempId):
        result = self.rest.sendTemplateSMS(to, datas, tempId)           # 发短信有延迟
        print(result)      # dict类型
        if result.get('statusCode') == '000000':
            return 0
        else:
            return -1

if __name__ == '__main__':
    # 注意： 测试的短信模板编号为1
    # sendTemplateSMS('17600992168', ['123456', 5], 1)
    to = '15926750521'
    datas = ['594268', 5]
    tempId = 1
    CCP().send_template_sms(to, datas, tempId)


















# 编码说明：coding = utf - 8或gbk
# from verifications.libs.yuntongxun.CCPRestSDK import REST
# # import ConfigParser
# accountSid = '您的主账号'
# accountToken = '您的主账号Token'
# appId = '您的应用ID'
# serverIP = 'app.cloopen.com'                              # 说明：请求地址，生产环境配置成app.cloopen.com。
# serverPort = '8883'                                       # 说明：请求端口 ，生产环境为8883.
# softVersion = '2013-12-26'                                # 说明：REST API版本号保持不变。
# def sendTemplateSMS(to, datas, tempId):
#     # 初始化REST SDK
#     rest = REST(serverIP, serverPort, softVersion)
#     rest.setAccount(accountSid, accountToken)
#     rest.setAppId(appId)
#     result = rest.sendTemplateSMS(to, datas, tempId)
#     print(result)
    # 可参考demo中的接口调用文件：SendTemplateSMS.py。


