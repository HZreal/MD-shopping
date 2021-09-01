
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


accId = '8a216da87955ba1901796a40d5d50975'
accToken = '6bc212ea08c5413c84e9c3513f24f5ca'
appId = '8a216da87955ba1901796a40d6d7097c'

# accId = '8a216da87955ba1901796fa1d38a0a80'
# accToken = '86ddfadc98054ac4b2eab2a911d78e4a'
# appId = '8a216da87955ba1901796fa1d4940a86'

# 官方函数实例：
# def send_message():
#     sdk = SmsSDK(accId, accToken, appId)
#     tid = '1'
#     mobile = '15926750521'
#     datas = ('123456', '5')
#     resp = sdk.sendMessage(tid, mobile, datas)
#     print(resp)




import json
import random
# 发送短信验证码的单例类
class CCP(object):
    # 单例的初始化方法
    def __new__(cls, *args, **kwargs):
        # 若单例不存在，则创建单例
        if not hasattr(CCP, '_instance'):
            # 单例不存在则实例化创建单例cls._instance，super()保证了不会调用此处的__new__()，而是基类的
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)

            # 初始化SmsSDK，创建了一个sdk对象，
            # 并保存在单例的属性中(单例cls._instance原本没有sdk这个属性，动态新建)，便于调用单例类的属性sdk就可以调用到SmsSDK对象，且保证了创建的SmsSDK对象唯一，单例存在sdk存在，单例不存在，sdk不存在
            sdk = SmsSDK(accId, accToken, appId)
            cls._instance.sdk = sdk
        return cls._instance

    def send_message(self, tid, mobile, datas):
        resp = self.sdk.sendMessage(tid, mobile, datas)
        # print(resp)                     # json数据
        resp = json.loads(resp)         # 字典
        if resp.get('statusCode') == '000000':
            return 0
        else:
            return -1




# resp = '{"statusCode":"000000","templateSMS":{"smsMessageSid":"5b9afcce110b4005863b305ba4f60f65","dateCreated":"20210515003555"}}'
if __name__ == '__main__':

    # 官方函数调用
    # send_message()

    # 使用单例调用，参数都是字符串
    sms_code = '%06d' % random.randint(0, 999999)
    print(sms_code)    # 512261
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