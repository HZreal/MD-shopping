from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from meiduo_mall.utils.views import LoginRequiredJSONMixin
from users.models import Address
from django_redis import get_redis_connection
from goods.models import SKU
from decimal import Decimal
import json, logging
from django import http
from orders.models import OrderInfo, OrderGoods
from django.utils import timezone
from meiduo_mall.utils.response_code import RETCODE
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage
from orders import constants

logger = logging.getLogger('django')

# a = timezone.localtime()        # 上海时区 2021-06-09 00:08:43.009191+08:00
# b = timezone.now()        # 格林尼治时间 2021-06-08 16:08:43.107134+00:00


# 结算订单是从Redis购物车中查询出被勾选的商品信息进行结算并展示
class OrderSettlementView(LoginRequiredMixin, View):
    # 提供订单结算页面
    def get(self, request):
        user = request.user
        # 查询该登录用户所有收货地址
        try:
            addresses = Address.objects.filter(user=user, is_deleted=False)
        except Address.DoesNotExist:
            # 未查到，则用户可以去编辑收货地址
            addresses = None

        # 查询购物车中被勾选的商品sku
        redis_conn = get_redis_connection('carts')
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)                       # sku字典 {b'3': b'1'}
        redis_selected = redis_conn.smembers('selected_%s' % user.id)               # 被勾选商品sku_id集合 {b'3'}

        # 构造购物车中被勾选的sku数据：{'sku_id': count,}
        new_cart_dict = {}
        for sku_id in redis_selected:                     # redis集合中取出的元素sku_id是bytes类型，第二个sku_id无需转int，因为集合循环的sku_id与字典的key都是bytes类型
            new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])                 # 取出redis_cart字典的value为bytes类型，需转int

        # 查询new_cart_dict中所有sku_id对应的sku
        skus = SKU.objects.filter(id__in=new_cart_dict.keys())
        # 遍历补充商品所选数量count，单个商品小计金额amount
        total_count = 0
        total_amount = Decimal(0.00)
        for sku in skus:
            # 动态给sku对象添加设置count, amount属性
            sku.count = new_cart_dict.get(sku.id)
            sku.amount = sku.price * sku.count                 # 单个商品sku的小计金额


            # 计算所选商品数量，所有商品价格
            total_count += sku.count
            total_amount += sku.amount          # 注意：price是decimal类型，所以amount也是decima类型，float类型与decimal类型无法直接加，因此total_amount定义为decimal类型

        # 指定邮费
        # freight = 10.00              # float
        freight = Decimal(10.00)
        # decimal是高精度浮点数，拆开存储 如1.22分成1和22存，读取时拼接回来
        # float浮点数不够精确，1.24可能实际存储的是1.2399999999
        # 因此decimal的1.22并不等于float的1.22

        # 模板数据
        context = {
            'addresses': addresses,
            'skus': skus,                                             # 已勾选商品对象集
            'total_count': total_count,                               # 勾选商品总数量
            'total_amount': total_amount,                             # 所有勾选商品价格
            'freight': freight,                                       # 运费
            'payment_amount': total_amount + freight,                  # 总金额
        }
        return render(request, 'place_order.html', context)


# 接收axios请求提交订单，保存订单基本信息和订单商品信息
class OrderCommitView(LoginRequiredJSONMixin, View):
    def post(self, request):
        # 接收参数(订单商品不需接收，后端可查到)
        data = json.loads(request.body.decode())
        address_id = data.get('address_id')                                     # 勾选的地址id
        pay_method = data.get('pay_method')                                     # 勾选的支付方式，取到的是radio类型input标签中value的值：1(货到付款) 或 2(支付宝支付)
        # 校验参数
        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return http.HttpResponseForbidden('参数address_id有误')
        # 判断支付方式pay_method是否合法
        # if pay_method not in [1, 2]:
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method有误')

        # transaction模块提供的atomic方法实际调用类Atomic，此类有__call__方法实现类实例装饰器，__enter__,__exit__方法实现with上下文管理器
        # atomic方法定义一个事务，有以下两种方式：
        # 装饰器用法@transaction.atomic：作用于视图函数，整个视图中所有MySQL数据库的操作都看做一个事务，范围太大，不够灵活。而且无法直接作用于类视图。
        # 上下文管理器with语句用法with transaction.atomic()：可以灵活的有选择性的把某些MySQL数据库的操作看做一个事务。而且不用关心是视图函数还是类视图。
        # 开启一次事务
        with transaction.atomic():
            # 在数据库操作之前设置保存点，下面数据库操作不一致则退回此保存点
            save_point = transaction.savepoint()

            # 不确定哪里有隐藏的异常(如下面的save都可能抛异常)，直接暴力回滚
            try:
                # 登录用户
                user = request.user
                # 自定义订单编号：时间 + user_id   ==>   20200621122853000000001
                order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
                # 保存订单基本信息(创建订单对象)
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,                                           # 本订单商品总量，创建此对象时默认设为0，后续设置
                    total_amount=0,                                          # 本订单总额
                    freight=Decimal(10.00),
                    pay_method=pay_method,
                    # status='UNPAID' if pay_method == 'ALIPAY' else 'UNSEND',
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )

                # 从redis中查询已勾选的sku
                redis_conn = get_redis_connection('carts')
                redis_cart = redis_conn.hgetall('carts_%s' % user.id)                                    # 返回字典
                redis_selected = redis_conn.smembers('selected_%s' % user.id)                            # 返回集合
                new_cart_dict = {}
                for sku_id in redis_selected:
                    new_cart_dict[int(sku_id)] = int(redis_cart.get(sku_id))

                for sku_id in new_cart_dict.keys():
                    # 对每个商品的下单操作

                    # 缩小下面continue范围，意义就是每个商品sku都有多次下单的机会，直至库存不足
                    while True:
                        # 查库获取勾选商品信息(不能有缓存，要查询实时信息)
                        sku = SKU.objects.get(id=sku_id)                               # 查询商品的库存信息时，不能有缓存，不能用filter(id__in=sku_ids)查

                        # 获取数据库中原始的库存和销量，后面乐观锁更新库存销量时，以此原始值为条件去更新，若因为并发原始值被修改过，则更新失败
                        origin_stock =sku.stock
                        origin_sales = sku.sales

                        # 获取要提交订单的商品的数量，且判断是否超过库存
                        sku_count = new_cart_dict.get(sku_id)
                        if sku_count > origin_stock:
                            # 库存不足需要回滚至保存点
                            transaction.savepoint_rollback(save_point)
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

                        # 模拟网络延迟7s
                        # import time
                        # time.sleep(7)
                        # 在延迟时间7s内，数据库操作未提交而又有其他用户对同样的商品并发下单，会造成数据库数据异常

                        # SKU 减库存，加销量
                        # sku.stock -= sku_count
                        # sku.sales += sku_count
                        # sku.save()                          # 需要开启远程elasticsearch服务器，因为mysql被修改时会被haystack检测到，haystack修改索引表后需要访问并重写进elasticsearch
                        # 悲观锁：类似于互斥锁，锁住操作后别人无法操作，容易死锁
                        # 乐观锁：并不是真实存在的锁，而是在更新的时候判断此时的库存是否与之前查询出的库存相同，不同则表示有资源抢夺，相同则表示未修改过。执行更新
                        # 任务队列：将下单的逻辑放到任务队列中（如celery），将并行转为串行，所有人排队下单，性能最好，实现最难
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count
                        # 采用乐观锁：以原始值为条件更新数据库数据，若因并发，原始值被修改过，则返回0表示有资源抢夺，更新数据失败
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
                        if result ==0:
                            # return http.JsonResponse('下单失败')
                            # 库存10 A用户要买1 但此时下单有B用户资源抢夺买2 即使B下单完成库存依然对A足够 不能因为B的抢夺而告知A下单失败，而是让A再去下单，直至库存不足

                            # continue退出此次for循环进行下个sku处理，不合需求
                            # 因此上面加个while循环使continue作用域缩小至while，即继续此商品的下单
                            continue                         # 此次while下单结束，进行此商品下次while循环继续尝试下单

                        # SPU 加销量：这里无需设置乐观锁，因为只要上面更新sku库存销量捕获到有资源抢夺时，while循环不会执行到此
                        sku.spu.sales += sku_count
                        sku.spu.save()

                        # 保存订单商品信息
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price,
                        )

                        # 累加订单商品的数量和总价到订单基本信息
                        order.total_count += sku_count
                        order.total_amount += sku.price * sku_count

                        # 下单成功，跳出while死循环
                        break

                # 支付总额需再加上运费(for循环外)
                order.total_amount += order.freight
                order.save()

                # 清除购物车中已结算的商品
                # pl = redis_conn.pipeline()
                # pl.hdel('carts_%s' % user.id, *redis_selected)
                # pl.srem('selected_%s' % user.id, *redis_selected)
                # pl.execute()

            # 捕获可能隐藏的异常，进行暴力回滚
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_point)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})

            # 数据库同步操作成功，则提交此次事务
            transaction.savepoint_commit(save_point)

        # 响应：order_id是作为此axios请求成功回调后再次发送请求订单成功页面的路由查询字符串参数
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'order_id': order_id})


# '/orders/success/?order_id='+ order_id + '&payment_amount=' + payment_amount + '&pay_method=' + pay_method
class OrderSuccessView(LoginRequiredMixin, View):
    # 提供提交订单成功后的页面
    def get(self, request):
        # 接收参数
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context ={
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method,
        }

        return render(request, 'order_success.html', context)



# 用户个人订单信息
class UserOrderInfoView(LoginRequiredMixin, View):
    # 提供我的订单页面
    def get(self, request, page_num):
        # 当前登录用户
        user = request.user

        # 查询该用户的所有订单
        orders = user.orderinfo_set.all().order_by("-create_time")
        # 遍历所有订单
        for order in orders:
            # 绑定订单状态
            order.status_name = OrderInfo.ORDER_STATUS_CHOICES[order.status-1][1]                   # status_name获取到订单状态的具体描述
            # 绑定支付方式
            order.pay_method_name = OrderInfo.PAY_METHOD_CHOICES[order.pay_method-1][1]

            # 给订单动态绑定一个属性sku_list，存储订单商品sku
            order.sku_list = []
            # 查询订单商品
            order_goods = order.skus.all()                                  # OrderGoods模型类外键order指定了related_name=skus
            # 遍历订单商品
            for order_good in order_goods:
                sku = order_good.sku
                sku.count = order_good.count
                sku.amount = sku.price * sku.count
                order.sku_list.append(sku)

        # 分页处理
        page_num = int(page_num)
        try:
            paginator = Paginator(orders, constants.ORDERS_LIST_LIMIT)
            page_orders = paginator.page(page_num)
            total_page = paginator.num_pages
        except EmptyPage:
            return http.HttpResponseNotFound('订单不存在')

        context = {
            "page_orders": page_orders,                      # 一页的订单对象集
            'total_page': total_page,
            'page_num': page_num,
        }
        return render(request, "user_center_order.html", context)



"""订单商品评价"""
class OrderCommentView(LoginRequiredMixin, View):
    # 转到评价页面
    def get(self, request):
        order_id = request.GET.get('order_id')


        context = {

        }
        return render(request, '', context)



    # 接收用户提交的评价
    def post(self, request):
        data = json.loads(request.body.decode())
        order_id = data.get('order_id')
        sku_id = data.get('sku_id')
        score = data.get('score')
        comment = data.get('comment')
        is_anonymous = data.get('is_anonymous')



        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '评价成功'})








































































































