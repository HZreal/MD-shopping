from django.shortcuts import render
from django.views import View
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from alipay import AliPay
from django.conf import settings
import os
from orders.models import OrderInfo
from django import http
from meiduo_mall.utils.response_code import RETCODE
from payment.models import Payment


# 获取应用私钥和支付宝公钥路径
app_private_key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/app_private_key.pem')
alipay_public_key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/alipay_public_key.pem')
# 读取文件中的字符串
app_private_key_string = open(app_private_key_path).read()
alipay_public_key_string = open(alipay_public_key_path).read()


# 对接支付宝的支付接口：将支付宝扫码登录链接发给前端
class PaymentView(LoginRequiredJSONMixin, View):
    def get(self, request, order_id):
        # 校验参数order_id
        user = request.user
        try:
            # 此订单必须是该登录用户的，数据库存在的，未支付的
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息有误')

        # 创建对接支付宝接口的SDK对象，传递公共参数
        alipay = AliPay(
            # 应用id
            appid=settings.ALIPAY_APPID,
            # 默认的异步回调地址，这里不传下面采用同步回调return_url形式
            app_notify_url=None,
            # 应用私钥，客户端用于签名
            app_private_key_string=app_private_key_string,
            # 支付宝公钥，客户端用于解密
            alipay_public_key_string=alipay_public_key_string,
            # 签名类型
            sign_type='RSA2',
            # 指定开发环境(上线则为生产环境)
            debug=settings.ALIPAY_DEBUG,
        )

        # SDK对象调用api_alipay_trade_page_pay方法，对接支付宝统一收单下单并支付页面接口，传递请求参数，返回请求的参数字符串(app_id,biz_content,out_trade_no等参数拼接)
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,                                         # 订单编号，必传
            total_amount=str(order.total_amount),                          # 订单金额，decimal转str
            subject='md_market_%s' % order_id,                             # 订单标题
            return_url=settings.ALIPAY_RETURN_URL,                         # 同步通知的回调地址
            notify_url=None                                                # 异步通知的回调地址
        )

        # 拼接完整的支付宝登录页地址
        # 生产环境转到：https://openapi.alipay.com/gateway.do? + order_string
        # 开发环境转到：https://openapi.alipaydev.com/gateway.do? + order_string
        alipay_url = settings.ALIPAY_URL + '?' + order_string

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})



# 成功支付后的同步回调
class PaymentStatusView(View):
    """保存订单支付结果"""
    def get(self, request):
        # 获取所有查询字符串参数
        query_dict = request.GET
        # 参数转成标准字典类型
        data = query_dict.dict()
        # 参数中移除sign并提取其余参数进行验签
        signature = data.pop('sign')                            # 字典的pop方法

        # 使用SDK对象，调用验证通知接口函数进行验证
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type='RSA2',
            debug=settings.ALIPAY_DEBUG,
        )
        success = alipay.verify(data, signature)               # 返回bool类型，验证成功返回True
        # 验证通过后对支付状态进行处理(保存订单编号和交易编号，修改订单状态)
        if not success:
            # 验证失败则拒绝此次请求
            return http.HttpResponseForbidden('invalid request')
        else:
            # 获取订单编号和交易编号，并保存
            order_id = data.get('out_trade_no')
            trade_id = data.get('trade_no')
            Payment.objects.create(
                # order='',                                           # 无法直接拿到订单对象，调用模型类用字段代替存储
                order_id=order_id,
                trade_id=trade_id,
            )

            # 修改订单状态(待支付—>待评价)
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])

            # 响应结果
            context = {
                'trade_id': trade_id,
            }
            return render(request, 'pay_success.html', context)



















































































































































