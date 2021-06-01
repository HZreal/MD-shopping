from haystack import indexes
from goods.models import SKU


# SKU索引数据模型类
class SKUIndex(indexes.SearchIndex, indexes.Indexable):

    # 接收索引字段：使用文档定义索引字段，使用模板语法渲染
    text = indexes.CharField(document=True, use_template=True)

    # 返回建立的索引模型类
    def get_model(self):
        return SKU

    # 返回要建立索引的数据查询集
    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_launched=True)

















































