# 静态化页面：将动态渲染生成的页面结果保存成html文件，放到静态文件服务器中。用户直接去静态服务器，访问处理好的静态html文件。
# 意义：减少数据库查询次数，提升页面响应效率
# 操作时间：开发完成后部署上线之前
# 注意：用户相关数据不能静态化，其他动态变化的数据不能静态化
# 不能静态化的数据处理：
#               可以在用户得到页面后，在页面中向后端发送Ajax请求获取相关数据。
#               直接使用模板渲染出来


from contents.models import ContentCategory
from collections import OrderedDict
from contents.utils import get_categories
from django.template import loader
import os
from django.conf import settings



# 静态化首页：变化频繁，用django的crontab定时处理此任务，间歇更新静态文件
def generate_static_index_html():
    # 1.查询数据
    # 查询首页商品分类数据
    categories = get_categories()
    # 查询首页广告数据
    content_categories = ContentCategory.objects.all()  # 查广告类别(19条记录)
    # 构造有序字典数据
    contents = OrderedDict()
    for content_category in content_categories:
        # 查询条件是可展示，查询结果进行排序，返回的是对象集，即排序的列表，而contents字典的value刚好就是对象列表
        contents[content_category.key] = content_category.content_set.filter(status=True).order_by('sequence')
    # 构造上下文
    context = {
        'categories': categories,
        'contents': contents,
    }
    # render渲染：获取模板，渲染模板，然后响应
    # return render(request, 'index.html', context)


    # 2.渲染到模板(render前两步，不作响应)
    # 先获取模板文件
    template = loader.get_template('index.html')
    # 使用上下文渲染模板文件
    html_text = template.render(context)


    # 3.将模板文件写入到静态路径
    static_file_path = settings.STATICFILES_DIRS[0]
    file_path = os.path.join(static_file_path, 'index.html')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html_text)


# python shell执行：
# from contents.cron import generate_static_index_html
# generate_static_index_html()
# 执行完成即生成首页静态文件

# 使用python自带的http.server模块启动静态服务器，提供静态首页的访问测试(页面刷新明显变快)
# 进入到static上级目录
# cd ~/projects/meiduo_project/meiduo_mall/meiduo_mall
# 开启测试静态服务器
# python -m http.server 8080 --bind 127.0.0.1




# 采用crontab定时生成静态文件
# 1.安装crontab并注册，在dev.py文件之配置CRONJOBS=[(任务1), (任务2),    ...]

# python manage.py crontab add       # 添加定时任务到系统中，即可间歇更新静态文件
# python manage.py crontab show           # 显示已激活的定时任务
# python manage.py crontab remove     # 移除定时任务








