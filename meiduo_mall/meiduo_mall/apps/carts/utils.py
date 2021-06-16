import pickle, base64
from django_redis import get_redis_connection



# 合并购物车
def merge_cart_cookies_redis(request, user, response):
    # 获取cookies中的购物车信息
    cart_str = request.COOKIES.get('carts')

    # 判断cookie中是否有购物车信息，存在则合并，不存在不合并
    if not cart_str:
        return response

    # 购物车数据存在则反序列化获取，合并
    cookie_cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

    '''
    cart_dict = {                # 未登录用户购物车数据结构
        "sku_id1": {
            "count": "1",
            "selected": "True"
        },
        ...
    }
    '''

    # 准备新的数据容器，保存cookie购物车中的sku_id,count  selected, unselected
    new_cart_dict = {}                       # 存sku_id, count键值对
    new_selected_add = []                    # 存已勾选的sku_id
    new_selected_rem = []                    # 存未勾选的sku_id

    # 遍历出cookies中的数据
    for sku_id, cookie_dict in cookie_cart_dict.items():
        new_cart_dict[sku_id] = cookie_dict.get('count')
        if cookie_dict.get('selected'):
            new_selected_add.append(sku_id)
        else:
            new_selected_rem.append(sku_id)

    # 根据新的数据结构，合并到redis
    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()
    pl.hmset('carts_%s' % user.id, new_cart_dict)         # hmset一次性设置key下的多个域和值，传入参数的是字典
    if new_selected_add:    # 有值则操作
        pl.sadd('selected_%s' % user.id, *new_selected_add)
    if new_selected_rem:
        pl.srem('selected_%s' % user.id, *new_selected_rem)
    pl.execute()

    # 删除cookies
    response.delete_cookie('carts')

    return response