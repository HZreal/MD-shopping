from django.shortcuts import render
from django.views import View
from goods.models import GoodsChannelGroup, GoodsChannel, GoodsCategory
from collections import OrderedDict                  # 有序字典
from contents.models import Content, ContentCategory



# 首页
class IndexView(View):
    # 提供首页页面
    def get(self, request):
        # 查询首页商品分类数据
        # 构造商品分类字典(作为模板数据传入前端显示)
        # categories = {}                       # 无序的
        categories = OrderedDict()              # 创建有序字典

        # 查询商品频道(37个) 按照组id、sequence排序
        channels = GoodsChannel.objects.order_by('group_id', 'sequence')
        for channel in channels:
            # 获取当前频道所在的组id
            group_id = channel.group_id
            # 遍历每一个频道时，其组id有重复，只有不重复时才将group_id作为key添加到字典categories中
            if group_id not in categories:
                # 构造categories字典内部key(就是group_id)和value(字典)
                categories[group_id] = {'channels': [], 'sub_cats': []}

            # 频道外键得到一级分类(一对一)
            cat1 = channel.category
            # 构造key='channels'对应的第一个列表
            categories[group_id]['channels'].append({'id': cat1.id, 'name': cat1.name, 'url': channel.url})
            # 构造key='sub_cats'对应的第二个列表：这个列表元素是二级类别对象(字典)
            for cat2 in cat1.subs.all():
                sub_cats2 = []                           # 二级类别对象(字典)中依然有个key='sub_cats'对应的值是一个列表(存放三级分类对象集)
                for cat3 in cat2.subs.all():
                    sub_cats2.append({'id': cat3.id, 'name': cat3.name})
                categories[group_id]['sub_cats'].append({'id': cat2.id, 'name': cat2.name, 'sub_cats': sub_cats2})            # 注意：前端通过字典的key(字符串)读取value值数据，前后端需保持一致，值变量可自定义
            # 上面构造数据传入对象的部分属性数据，下面传入整个对象数据
            # for cat2 in cat1.subs.all():
            #     cat2.sub_cats = []                         # 给二级类别动态添加一个字段(保存三级类别集的列表)
            #     for cat3 in cat2.subs.all():
            #         cat2.sub_cats.append(cat3)
            #     categories[group_id]['sub_cats'].append(cat2)


        # 查询首页广告数据
        content_categories = ContentCategory.objects.all()               # 查广告类别
        # 构造有序字典数据
        contents = OrderedDict()
        for content_category in content_categories:
            # 查询条件是可展示，查询结果进行排序，返回的是对象集，即排序的列表，而contents字典的value刚好就是对象列表
            contents[content_category.key] = content_category.content_set.filter(status=True).order_by('sequence')


        # 将数据传给jinja2模板
        context = {
            'categories': categories,
            'contents': contents,
        }
        return render(request, 'index.html', context)



    def post(self, request):
        pass







































































































































































































































