from haystack import indexes
from goods.models import SKU


# SKU索引数据模型类
class SKUIndex(indexes.SearchIndex, indexes.Indexable):

    # 使用文档定义索引字段，使用模板语法渲染
    # text接收索引字段，由多个数据库模型类字段组成。
    # document=True，表名该字段是主要进行关键字查询的字段
    # use_template = True表示后续通过模板来指明
    text = indexes.CharField(document=True, use_template=True)

    # 返回建立的索引模型类
    def get_model(self):
        return SKU

    # 返回要建立索引的数据查询集
    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_launched=True)


# 手动生成初始索引
# python manage.py rebuild_index
# 后续haystack检测到数据库sku信息的变化，会自动更新索引表












































