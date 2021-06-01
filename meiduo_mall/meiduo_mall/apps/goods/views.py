from django.shortcuts import render
from django.views import View
from django import http
from goods.models import GoodsCategory, SKU
from contents.utils import get_categories
from goods.utils import get_breadcrumb
from django.core.paginator import Paginator, EmptyPage
from meiduo_mall.utils.response_code import RETCODE
from goods import constants

class ListView(View):
    def get(self, request, category_id, page_num):              # 从首页点击三级分类进入此视图时，page_num默认是1
        # 获取校验参数(正则只能校验结构、类型，无法校验范围)
        try:
            # 查库看category_id(三级类别)是否存在
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist as e:
            return http.HttpResponseForbidden('参数category_id不存在')

        # 获取参数sort(sort没有值则取default，字典的语法)
        sort = request.GET.get('sort', default='default')
        # 根据传入的sort选择排序字段：排序字段必须是模型类的属性！！！
        if sort == 'price':
            sort_field = 'price'                            # 按照价格由低到高
        elif sort == 'hot':
            sort_field = '-sales'                           # 按照销量由低到高(属性是sales而不是sale别写错)
        else:     # 其余全归为default
            sort = 'default'                                 # 出现了随意值如sort=bfhj则也设置sort='default'，因为这个参数还要传给前端
            sort_field = 'create_time'                       # 按照创建时间(新品优先)由低到高


        # 获取商品分类数据(调用即可)
        categories = get_categories()

        # 获取面包屑导航(传入的是三级分类)
        breadcrumb = get_breadcrumb(category)

        # 分页和排序查询，条件：当前三级分类下的所有sku，且已上架，查询结果按sort_field排序
        # skus1 = SKU.objects.filter(category=category, is_launched=True).order_by(sort_field)
        # skus2 = SKU.objects.filter(category_id=category_id, is_launched=True).order_by(sort_field)
        skus = category.sku_set.filter(is_launched=True).order_by(sort_field)

        # 创建分页器对象：第一个参数为要分页的记录，第二个参数为每页的记录条数
        paginator = Paginator(skus, constants.GOODS_LIST_LIMIT)
        try:
            # 根据用户选择的页码page_num返回对应的那一页(此页码可能不合法，系统提供了此异常的捕获EmptyPage)
            page_skus = paginator.page(page_num)                         # 获取第page_num页中的5条记录
            # 取得总页数(前端分页插件需要)
            total_page = paginator.num_pages
        except EmptyPage:                                                # 捕获不合法的page_num
            return http.HttpResponseNotFound('Empty Page')

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'page_skus': page_skus,                                      # 第page_num页中的6条记录
            'total_page': total_page,                                    # 总共的页数
            'page_num': page_num,                                        # 当前页码
            'sort': sort,                                                # 前端依据sort设置当前用户选中a标签(默认/价格/人气)的样式，且分页器也需要此参数
            'category_id': category_id,
        }
        return render(request, 'list.html', context)


# 热销商品排行的axios请求
class HotGoodsView(View):
    def get(self, request, category_id):
        # 查询指定分类的sku信息，且必须上架，结果按销量递减排序，最后切片取前两位
        skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]

        # 将模型类列表转字典列表
        hot_skus = [{
            'id': sku.id,
            'name': sku.name,
            'price': sku.price,
            'default_image': sku.default_image.url,
        } for sku in skus]

        # 返回json数据给前端回调函数
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': hot_skus})


# 商品详情
class DetailView(View):
    def get(self, request, sku_id):
        # 接收校验参数
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            # return http.HttpResponseNotFound('sku_id不存在')
            return render(request, '404.html')

        # 查询商品分类
        categories = get_categories()

        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 查询SKU信息

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
        }
        return render(request, 'detail.html', context)




































































































































