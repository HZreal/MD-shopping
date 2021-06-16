from ronglian_sms_sdk import SmsSDK

# accId = '容联云通讯分配的主账号ID'
# accToken = '容联云通讯分配的主账号TOKEN'
# appId = '容联云通讯分配的应用ID'
# def send_message():
#     sdk = SmsSDK(accId, accToken, appId)
#     tid = '容联云通讯平台创建的模板'
#     mobile = '手机号1,手机号2'
#     datas = ('变量1', '变量2')
#     resp = sdk.sendMessage(tid, mobile, datas)
#     print(resp)

# 官方函数实例：
# accId = '8a216da87955ba1901796a40d5d50975'
# accToken = '6bc212ea08c5413c84e9c3513f24f5ca'
# appId = '8a216da87955ba1901796a40d6d7097c'

accId = '8a216da87955ba1901796fa1d38a0a80'
accToken = '86ddfadc98054ac4b2eab2a911d78e4a'
appId = '8a216da87955ba1901796fa1d4940a86'
# def send_message():
#     sdk = SmsSDK(accId, accToken, appId)
#     tid = '1'
#     mobile = '15926750521'
#     datas = ('123456', '5')
#     resp = sdk.sendMessage(tid, mobile, datas)
#     print(resp)




import json
import random

# 单例模式：目的是确保某一个类只有一个实例存在，保证了在程序的不同位置都可以且仅可以取到同一个对象实例
# 单例的优势：大量任务需要调用某个类的实例方法，而这个类的初始化方法参数固定，可以将此类设置成单例类，这样这些任务都只从一个唯一的实例中调用实例方法，若不设成单例，那么每个任务都会因为调用实例方法去初始化类，内存中将生产大量的实例(实质是一样的，id不同),造成内存严重浪费甚至崩溃
# 给类设置成单例类时，此类的初始化方法的参数应该为公共参数，即所有调用此类的实例方法的任务需要一个同样的实例环境，而非公共参数可以放在实例方法中
# 一个类初始化时，判断实例不存在，会创建一个实例；如果已存在就会返回这个实例，这样的类称为单例类
class CCP(object):                         # 单例类
    # 单例的初始化方法
    def __new__(cls, *args, **kwargs):                                      # 无需使用@staticmethod装饰器修饰，会在__init__之前调用

        # 类创建实例时判断实例是否存在，存在则不创建实例直接返回该实例
        if not hasattr(CCP, '_instance'):
            # 不存在则创建CCP实例并保存在类属性cls._instance中，super()保证了不会调用此处的__new__()，而是基类的
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)

            # 初始化SmsSDK，创建了一个SmsSDK对象
            sdk = SmsSDK(accId, accToken, appId)
            # 并保存在此类CCP的类属性中(CCP类原本没有sdk这个属性，动态新建)，便于调用单例类的类属性sdk就可以调用到SmsSDK对象，且保证了创建的SmsSDK实例唯一，实例存在则sdk存在，实例不存在，sdk不存在
            cls._instance.sdk = sdk

        # 实例存在或者刚创建实例完成，直接返回该实例
        return cls._instance

    # 定义实例对象方法(不是类方法，是类方法就失去单例的意义) 实现单例类发送短信验证码
    def send_message(self, tid, mobile, datas):
        resp = self.sdk.sendMessage(tid, mobile, datas)                      # 调用SmsSDK实例的方法sendMessage发送短信
        # print(resp)                     # json数据
        resp = json.loads(resp)           # 字典
        if resp.get('statusCode') == '000000':
            return 0
        else:
            return -1




# resp = '{"statusCode":"000000","templateSMS":{"smsMessageSid":"5b9afcce110b4005863b305ba4f60f65","dateCreated":"20210515003555"}}'
if __name__ == '__main__':

    # 使用单例调用，参数都是字符串
    sms_code = '%06d' % random.randint(0, 999999)
    print(sms_code)    # 512261

    # 调用单例类发送短信
    CCP().send_message(tid=1, mobile='15872060069', datas=(sms_code, 5))
    # CCP().send_message(tid=1, mobile='15926750521', datas=(sms_code, 5))
    # CCP().send_message(tid='1', mobile='15926750521', datas=('637596', '5'))

# resp
    # Sign plaintext: 8a216da87955ba1901796a40d5d509756bc212ea08c5413c84e9c3513f24f5ca20210515161306
    # Authorization plaintext: 8a216da87955ba1901796a40d5d50975: 20210515161306
    # Request url: https: // app.cloopen.com: 8883 / 2013 - 12 - 26 / Accounts / 8a216da87955ba1901796a40d5d50975 / SMS / TemplateSMS?sig = 7CFE948702393EEE5C38C5950E8E7F76
    # Request headers: {'Content-Type': 'application/json;charset=utf-8', 'Accept': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': b'OGEyMTZkYTg3OTU1YmExOTAxNzk2YTQwZDVkNTA5NzU6MjAyMTA1MTUxNjEzMDY='}
    # Request body: {"to": "15926750521", "appId": "8a216da87955ba1901796a40d6d7097c", "templateId": "1", "datas": ["637596", "5"]}
    # Response body: {"statusCode": "000000", "templateSMS": {"smsMessageSid": "85cc3ce1218b4492905a11e56273b887", "dateCreated": "20210515161307"}}
    # {"statusCode": "000000", "templateSMS": {"smsMessageSid": "85cc3ce1218b4492905a11e56273b887", "dateCreated": "20210515161307"}}