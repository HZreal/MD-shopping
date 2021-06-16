# 详情页的数据变化的频率没有首页广告那么频繁，而且是当SKU信息有改变时才要更新的，所以我们采用新的静态化方案。
# 方案一：通过Python脚本手动一次性批量生成所有商品静态详情页(部署上线前)。
# 方案二：后台运营人员修改了SKU信息时，异步的静态化对应的商品详情页面。
# 注意：
#         用户数据和购物车数据不能静态化。
#         热销排行和商品评价不能静态化



# 先使用方案一来静态详情页。当有运营人员修改时才会补充方案二

# 脚本执行的解释器    # /usr/bin/env python(linux)
#!F:\virtualenvs\py3_django_1\Scripts\python.exe


# 指定导包路径
import sys
sys.path.insert(0, '../')

# 指定脚本执行用的Django环境变量和配置文件
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'

# 启动Django
import django
django.setup()


from django.template import loader
from django.conf import settings
from contents.utils import get_categories
from goods.utils import get_breadcrumb
from goods.models import SKU

def generate_static_sku_detail_html(sku_id):
    # 查询sku信息
    sku = SKU.objects.get(id=sku_id)

    # 查询商品分类
    categories = get_categories()

    # 查询面包屑导航
    breadcrumb = get_breadcrumb(sku.category)

    # 构建当前sku的规格键
    sku_specs = sku.specs.order_by('spec_id')
    sku_key = [spec.option.id for spec in sku_specs]

    # 获取当前商品sku所在spu类下的所有SKU
    skus = sku.spu.sku_set.all()
    # 构建不同规格参数（选项）的sku字典
    spec_sku_map = {}
    for s in skus:
        # 获取某个sku拥有的规格
        s_specs = s.specs.order_by('spec_id')
        # 用于形成规格选项-sku字典的键
        key = [spec.option.id for spec in s_specs]  # sku拥有的规格的id组成的列表
        # 向规格选项-sku字典添加记录
        spec_sku_map[tuple(key)] = s.id

        # 获取当前sku所在spu类拥有的规格信息(goods_specs即spu规格对象集)
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续(当前sku的规格条数不能小于当前sku所在spu类所拥有的规格条数)
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            key = sku_key[:]
            spec_options = spec.options.all()
            for option in spec_options:
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options


        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }


        template = loader.get_template('detail.html')
        html_text = template.render(context)
        file_path = os.path.join(settings.STATICFILES_DIRS[0], 'detail/' + str(sku_id) + '.html')
        # 在windows下，新文件的默认编码是gbk，这样python解释器会用gbk编码去解析我们的网络数据流txt，然而txt此时已经是decode过的unicode编码，这样的话就会导致解析不了
        with open(file_path, 'w', encoding='utf-8') as file:                  # windows下必须指定encoding='utf-8'
            file.write(html_text)



if __name__ == '__main__':
    skus = SKU.objects.all()
    for sku in skus:
        print(sku.id)
        generate_static_sku_detail_html(sku.id)





# chmod +x regenerate_detail_html.py            # linux中可能要修改Python脚本文件为可执行

# windows执行本脚本文件python regenerate_detail_html.py
# 16个商品sku对应16个静态网页文件


# 使用Python自带的http.server模块来模拟静态服务器，提供静态首页的访问测试

