from django.shortcuts import render
from django.views import View
from django import http
from goods.models import GoodsCategory, SKU, GoodsVisitCount
from contents.utils import get_categories
from goods.utils import get_breadcrumb
from django.core.paginator import Paginator, EmptyPage
from meiduo_mall.utils.response_code import RETCODE
from goods import constants
from django.utils import timezone           # 处理时间的工具
from datetime import datetime



# 从首页点击三级分类进入此商品列表视图时，page_num默认是1
class ListView(View):
    def get(self, request, category_id, page_num):
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
    def get(self, request, sku_id):               # 若sku_id=4
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


        # 1.获取当前sku的具体信息
        # 获取当前sku拥有的规格对象集sku_specs
        sku_specs = sku.specs.order_by('spec_id')                    # [颜色, 内存]
        # 遍历每个规格，获取当前sku拥有的选项id组成的列表sku_key
        # sku_key = []
        # for spec in sku_specs:
        #     sku_key.append(spec.option.id)
        sku_key = [spec.option.id for spec in sku_specs]                # [8, 12]


        # 2.获取当前商品sku所在spu类下的所有SKU
        skus = sku.spu.sku_set.all()                                   # [sku3, sku4, sku5, sku6, sku7, sku8]
        # 构建不同规格选项的sku字典
        spec_sku_map = {}
        # 遍历每个sku，查询出其具体规格，选项，结果集存储在构建的spec_sku_map字典中
        for s in skus:
            # 获取某个sku拥有的规格
            s_specs = s.specs.order_by('spec_id')
            # 当前sku所拥有的选项id列表s_key，作为spec_sku_map字典的键
            s_key = [spec.option.id for spec in s_specs]
            # 向规格选项-sku字典添加记录
            spec_sku_map[tuple(s_key)] = s.id
        # sku_id=4时构造结果如下：
        # spec_sku_map = {
        #     (8, 11): 3,                                 # 规格选项组成元组作为字典key，sku_id作为字典value，规格决定sku是谁
        #     (8, 12): 4,
        #      ...
        #     (10, 12): 8,
        # }


        # 3.获取当前sku所在spu类拥有的规格信息(goods_specs即spu规格对象集)
        goods_specs = sku.spu.specs.order_by('id')                  # [颜色(id=4), 内存(id=5)]
        # 若当前sku的规格信息不完整，则不再继续(当前sku的规格条数不能大于当前sku所在spu类所拥有的规格条数)
        if len(sku_key) < len(goods_specs):
            return
        # goods_specs = [
        #    {
        #        'name': '屏幕尺寸',
        #        'options': [
        #            {'value': '13.3寸', 'sku_id': xxx},
        #            {'value': '15.4寸', 'sku_id': xxx},
        #        ]
        #    },
        #    {
        #        'name': '颜色',
        #        'options': [
        #            {'value': '银色', 'sku_id': xxx},
        #            {'value': '黑色', 'sku_id': xxx}
        #        ]
        #    },
        #    ...
        # ]


        # 4.用于前端用户点击某规格选项时，立即映射sku_id发给后端，即给选项对象绑定sku_id
        # enumerate()函数用于将一个可遍历的数据对象(如列表、元组或字符串)组合为一个索引序列，同时列出数据下标(默认从0开始，亦可start指定)和数据，一般用在 for 循环当中
        for index, spec in enumerate(goods_specs):                            # goods_specs为[颜色(id=4), 内存(id=5)]
            # 复制当前sku的选项列表(切片不指定开始和结尾索引即保留所有，也就是复制)
            key = sku_key[:]
            # spu规格拥有的选项对象集
            spec_options = spec.options.all()
            for option in spec_options:                                       # spec_options为[金色(id=8)，深灰色(id=9)，银色(id=10)]      [64GB(id=11), 256GB(id=12)]
                # 遍历选项，为每个选项对象设置属性sku_id
                key[index] = option.id                          # 当前选项与原sku_key列表中剩余选项组合，在spec_sku_map字典中查询对应的sku_id

                # 给每个选项对象动态绑定一个sku_id
                option.sku_id = spec_sku_map.get(tuple(key))                  # 设置结果：金色对象.sku_id=4；深灰色对象.sku_id=6；银色对象.sku_id=8；64GB对象.sku_id=3； 256GB对象.sku_id=4
                # 选项对象设置了属性sku_id后，jinja2模板渲染时就可以调用模型类

            # 当前规格对象动态设置属性spec_options，保存规格对象拥有的选项列表(jinja2模板可调用此属性遍历获取选项对象)
            spec.spec_options = spec_options


        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,                                # 传入当前sku对象给前端特别样式处理：高亮展示
            'specs': goods_specs,                      # 页面渲染需要当前sku所在spu类下的所有规格选项
        }
        return render(request, 'detail.html', context)


# 统计三级类别商品的访问量(用于后台管理使用)
class DetailVisitView(View):
    def post(self, request, category_id):
        # 接收校验参数
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('category_id不存在')

        # 获取当天日期：localtime会以设置文件中的时区TIME_ZONE为条件读取时间
        t = timezone.localtime()
        # 构造当天时间字符串：'%d-%02d-%02d' 或 '%d:%02d:%02d'  根据需求
        today_str = '%d-%02d-%02d' % (t.year, t.month, t.day)
        # 字符串转成当天时间对象datetime(调用strptime方法)，才能与date字段类型匹配
        today_date = datetime.strptime(today_str, '%Y-%m-%d')                                   # TODO python时间输出格式: %Y-%m-%d (%Y即2019年，%y即19年)
        # datetime.strftime()作用相反，将时间对象转字符串

        # 统计访问量
        # 先判断当天中指定的分类商品对应的记录是否存在
        try:
            # 如果存在拿到记录对象
            # GoodsVisitCount.objects.filter(date=today_date, category_id=category.id)
            # GoodsVisitCount.objects.filter(date=today_date, category_id=category_id)
            count_data = GoodsVisitCount.objects.get(date=today_date, category=category)            # 某一天的数据，要么存在要么不存在，不需用filter
        except GoodsVisitCount.DoesNotExist:
            # 如果不存在则创建记录对象(这里用初始化类的方法，而不用create，原因是不确定字段)
            count_data = GoodsVisitCount()
        # 设置字段值
        try:
            count_data.category = category                 # 对象不存在则设置，存在则覆盖
            count_data.date = today_date                   # 此行代码可不写，原因是模型类属性date设置了auto_now_add=True
            count_data.count += 1
            count_data.save()
        except Exception as e:
            return http.HttpResponseServerError('统计失败')

        # 返回响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})




























































































































