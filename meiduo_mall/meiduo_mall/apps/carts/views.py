from django.shortcuts import render
from django.views import View
import json, pickle, base64
from django import http
from goods.models import SKU
from django_redis import get_redis_connection
from meiduo_mall.utils.response_code import RETCODE
from carts import constants


# 购物车管理(登录用户与未登录用户均可进入，且对应不同的操作)
class CartsView(View):
    # 添加购物车(商品详情页面点击保存购物车)
    def post(self, request):
        # 接收参数
        json_str = request.body.decode()
        data = json.loads(json_str)
        sku_id = data.get('sku_id')
        count = data.get('count')                             # 商品选择数量
        selected = data.get('selected', True)                 # 勾选状态(非必传参数)，未传时给默认值True，即默认已勾选
        # 校验参数
        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必要参数')
        # 校验参数sku_id是否存在于库
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id有误')
        # 校验参数count是否是数字
        try:
            count = int(count)
        except Exception as e:
            return http.HttpResponseForbidden('参数count有误')
        # 校验参数selected类型是否是bool型(参数存在时)
        if selected:           # 上述在未传时给了默认值True，否则传入selected=False时不会进入下面的校验判断
            if not isinstance(selected, bool):                                 # isinstance(obj, type)校验obj对象是不是type类型
                return http.HttpResponseForbidden('')

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:              # 已登录返回True，操作redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 数据sku_id, count用harh类型存储
            # 查询key记录，sku_id存在则count自累加，不存在则count为当前最新值，但是redis的hincrby方法已封装此逻辑，直接调用
            pl.hincrby('carts_%s' % user.id, sku_id, count)
            # 勾选状态selected用set类型存储
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            pl.execute()

            # 响应结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加成功'})

        else:             # 未登录返回false，操作cookie购物车
            # 先获取cookie中的购物车数据                                                 'gAN9cQBLA31xAShYBQAAAGNvdW50cQJLAVgIAAAAc2VsZWN0ZWRxA4h1cy4='
            cart_str = request.COOKIES.get('carts')
            if cart_str:                   # 数据存在则反序列化获取
                # 将字符串转成byte类型密文数据                                                b'gAN9cQBLA31xAShYBQAAAGNvdW50cQJLAVgIAAAAc2VsZWN0ZWRxA4h1cy4='
                cart_str_bytes = cart_str.encode()
                # 将bytes类型密文数据进行base64解码，返回解码后的bytes类型数据                b'\x80\x03}q\x00K\x03}q\x01(X\x05\x00\x00\x00countq\x02K\x01X\x08\x00\x00\x00selectedq\x03\x88us.'
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 将bytes类型数据反序列化成python数据                                        {3: {'count': 1, 'selected': True}}
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}
            '''
            cart_dict = {                # 未登录用户购物车数据结构
                "sku_id1": {
                    "count": "1",
                    "selected": "True"
                },
                ...
            }
            '''
            # 判断当前要添加的sku_id在cart_dict中是否存在
            if sku_id in cart_dict:
                # 该sku已存在于购物车，取出count做累加
                origin_count = cart_dict[sku_id]['count']
                count += origin_count
            # 无论sku是否存在于购物车，都要重写购物车字典数据
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected,
            }

            # 将修改完成的购物车字典数据序列化
            # 将python字典数据序列化为byte类型数据                                                         b'\x80\x03}q\x00K\x03}q\x01(X\x05\x00\x00\x00countq\x02K\x01X\x08\x00\x00\x00selectedq\x03\x88us.'
            cart_dict_bytes = pickle.dumps(cart_dict)
            # 将bytes类型数据进行base64编码，返回编码后的bytes类型密文数据(像字符串的bytes数据)                        # b'gAN9cQBLA31xAShYBQAAAGNvdW50cQJLAVgIAAAAc2VsZWN0ZWRxA4h1cy4='
            cart_str_bytes = base64.b64encode(cart_dict_bytes)
            # 将bytes类型密文数据(像字符串)转成字符串(类似于request.body.decode)                                       'gAN9cQBLA31xAShYBQAAAGNvdW50cQJLAVgIAAAAc2VsZWN0ZWRxA4h1cy4='
            cookie_cart_str = cart_str_bytes.decode()

            # 响应结果
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加成功'})
            response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response


    # 查询购物车数据并展示页面
    def get(self, request):
        user = request.user
        if user.is_authenticated:          # 用户已登录，查询redis购物车
            redis_coon = get_redis_connection('carts')
            # 查询hash数据：redis中获取的源数据都是bytes类型
            redis_cart = redis_coon.hgetall('carts_%s' % user.id)        # 返回字典   {b'3': b'1'}
            # 查询set数据
            redis_selected = redis_coon.smembers('selected_%s' % user.id)      # 返回集合  {b'3', }

            # 将redis_cart和redis_selected合并数据，进行数据结构的构造，使之与未登录用户存入cookie信息的数据结构一致，便于统一化处理
            cart_dict = {}
            '''
            cart_dict = {                # 未登录用户购物车数据结构
                "sku_id1": {
                    "count": "1",
                    "selected": "True"
                },
                ...
            }
            '''
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_selected,           # selected的值通过判断获取，而非读取
                }

        else:                              # 用户未登录，查询cookies购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:  # 数据存在则反序列化获取
                # 将字符串转成byte类型密文数据
                cart_str_bytes = cart_str.encode()
                # 将bytes类型密文数据进行base64解码，返回解码后的bytes类型数据
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 将bytes类型数据反序列化成python数据
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}

        # 统一化处理购物车数据返给前端
        # 通过sku_id获取sku对象
        sku_ids = cart_dict.keys()
        # for sku_id in sku_ids:                 # 循环查询获取sku对象集
        #     sku = SKU.objects.get(id=sku_id)
        skus = SKU.objects.filter(id__in=sku_ids)     # 一次性查询出sku对象集
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'count': cart_dict.get(sku.id).get('count'),
                'selected': str(cart_dict.get(sku.id).get('selected')),     # 最后传给vue，vue无法识别python真实的True，转成字符串即可
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),                                   # 转字符串
                'amount': str(sku.price * cart_dict.get(sku.id).get('count')),
            })

        # 构造模板数据传入前端
        context = {
            'cart_skus': cart_skus,
        }
        return render(request, 'cart.html', context)


    # 修改购物车信息
    def put(self, request):
        # 接收参数
        json_str = request.body.decode()
        data = json.loads(json_str)
        sku_id = data.get('sku_id')
        count = data.get('count')  # 商品选择数量
        selected = data.get('selected', True)  # 勾选状态(非必传参数)，未传时给默认值True，即默认已勾选
        # 校验参数
        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必要参数')
        # 校验参数sku_id是否存在于库
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id有误')
        # 校验参数count是否是数字
        try:
            count = int(count)
        except Exception as e:
            return http.HttpResponseForbidden('参数count有误')
        # 校验参数selected类型是否是bool型(参数存在时)
        if selected:  # 上述在未传时给了默认值True，否则传入selected=False时不会进入下面的校验判断
            if not isinstance(selected, bool):  # isinstance(obj, type)校验obj对象是不是type类型
                return http.HttpResponseForbidden('')

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:      # 已登录，修改redis购物车
            redis_coon = get_redis_connection('carts')
            pl = redis_coon.pipeline()
            # 后端收到的是前端用户最终修改的数据，因此直接覆盖写入
            pl.hset('carts_%s' % user.id, sku_id, count)
            # 修改勾选状态(True则写入，False则删除)
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()

            # 响应数据
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'price': sku.price,
                'amount': sku.price * count,
                'default_image_url': sku.default_image.url,
            }
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改成功', 'cart_sku': cart_sku})

        else:                          # 未登录，修改cookie购物车
            # 先获取cookie中的购物车数据                                                 'gAN9cQBLA31xAShYBQAAAGNvdW50cQJLAVgIAAAAc2VsZWN0ZWRxA4h1cy4='
            cart_str = request.COOKIES.get('carts')
            if cart_str:  # 数据存在则反序列化获取
                # 将字符串转成byte类型密文数据                                                b'gAN9cQBLA31xAShYBQAAAGNvdW50cQJLAVgIAAAAc2VsZWN0ZWRxA4h1cy4='
                cart_str_bytes = cart_str.encode()
                # 将bytes类型密文数据进行base64解码，返回解码后的bytes类型数据                b'\x80\x03}q\x00K\x03}q\x01(X\x05\x00\x00\x00countq\x02K\x01X\x08\x00\x00\x00selectedq\x03\x88us.'
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 将bytes类型数据反序列化成python数据                                        {3: {'count': 1, 'selected': True}}
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}

            # 后端收到的是前端用户最终修改的数据，因此直接覆盖写入
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected,
            }

            # 将python字典数据序列化为byte类型数据
            cart_dict_bytes = pickle.dumps(cart_dict)
            # 将bytes类型数据进行base64编码，返回编码后的bytes类型密文数据(像字符串的bytes数据)
            cart_str_bytes = base64.b64encode(cart_dict_bytes)
            # 将bytes类型密文数据(像字符串)转成字符串(类似于request.body.decode)
            cookie_cart_str = cart_str_bytes.decode()

            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'price': sku.price,
                'amount': sku.price * count,
                'default_image_url': sku.default_image.url,
            }

            # 响应数据
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改成功', 'cart_sku': cart_sku})
            response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)
            return response


    # 删除购物车信息
    def delete(self, request):
        # 接收参数
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        # 校验参数
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoexNotExist:
            return http.HttpResponseForbidden('商品不存在')

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:            # 已登录删除redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 删除hash购物车商品sku_id信息(域和值)
            pl.hdel('cart_%s' % user.id, sku_id)
            # 同步删除set中的勾选状态
            pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除成功'})
        else:                               # 未登录删除cookie购物车
            # 先获取cookie中的购物车数据
            cart_str = request.COOKIES.get('carts')
            if cart_str:  # 数据存在则反序列化获取
                # 将字符串转成byte类型密文数据
                cart_str_bytes = cart_str.encode()
                # 将bytes类型密文数据进行base64解码，返回解码后的bytes类型数据
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 将bytes类型数据反序列化成python数据
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除成功'})
            # 删除字典指定key=sku_id的数据
            if sku_id in cart_dict:
                del cart_dict[sku_id]                   # 如果删除不存在的sku_id会抛出异常
                # 只有进行了删除操作才重写入cookie，否则不作任何处理
                cart_dict_bytes = pickle.dumps(cart_dict)
                cart_str_bytes = base64.b64encode(cart_dict_bytes)
                cookie_cart_str = cart_str_bytes.decode()
                # 新数据写入cookie
                response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)

            # 若不存在(无删除)直接响应(无需任何对cookie的操作)
            return response


# 用户是否勾选全选购物车的axios请求
class CartsSelectAllView(View):
    def put(self, request):
        # 接收参数
        data = json.loads(request.body.decode())
        selected = data.get('selected', True)
        # 校验参数
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            # 获取所有记录    {b'3': b'1', b'5': b'2'}
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            # 取出字典所有的key
            sku_id_list = redis_cart.keys()              # 列表

            # 判断用户是否全选
            if selected:        # 全选
                # for sku_id in sku_id_list:
                #     pl.sadd('selected_%s' % user.id, sku_id)
                redis_conn.sadd('selected_%s' % user.id, *sku_id_list)          # 添加多个(列表加*  字典加**)
            else:              # 全不选
                redis_conn.srem('selected_%s' % user.id, *sku_id_list)

            # 响应
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

        else:             # 未登录
            # 先获取cookie中的购物车数据
            cart_str = request.COOKIES.get('carts')

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

            if cart_str:
                # 数据存在则反序列化获取
                cart_str_bytes = cart_str.encode()
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                cart_dict = pickle.loads(cart_dict_bytes)

                # 遍历修改勾选状态
                for sku_id in cart_dict:
                    cart_dict[sku_id]['selected'] = selected

                # 序列化
                cart_dict_bytes = pickle.dumps(cart_dict)
                cart_str_bytes = base64.b64encode(cart_dict_bytes)
                cookie_cart_str = cart_str_bytes.decode()
                # 重写入cookie
                response.set_cookie('carts', cookie_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)

            # 无论是否设置全选都会响应
            return response


# 展示商品简单购物车
class CartsSimpleView(View):
    def get(self, request):

        user = request.user
        if user.is_authenticated:
            # 用户已登录，查询Redis购物车
            redis_conn = get_redis_connection('carts')
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            redis_selected = redis_conn.smembers('selected_%s' % user.id)

            # 将redis_cart和redis_selected合并数据，进行数据结构的构造，使之与未登录用户存入cookie信息的数据结构一致，便于统一化处理
            cart_dict = {}
            '''
            cart_dict = {                # 未登录用户购物车数据结构
                "sku_id1": {
                    "count": "1",
                    "selected": "True"
                },
                ...
            }
            '''
            for sku_id, count in redis_cart.items():
                cart_dict[sku_id] = {
                    'count': int(count),
                    'selected': sku_id in redis_selected
                }

        else:
            # 用户未登录，查询cookie购物车
            cart_str = request.COOKIES.get('carts')

            if cart_str:
                # 反序列化
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

        # 统一化处理购物车数据，构造前端需求数据
        cart_skus = []
        sku_ids = cart_dict.keys()
        # 前面用skus = SKU.objects.filter(id__in=sku_ids)查询，这里换用一般查询
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku_id).get('count'),
                'default_image_url': sku.default_image.url,
            })

        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_skus': cart_skus})

