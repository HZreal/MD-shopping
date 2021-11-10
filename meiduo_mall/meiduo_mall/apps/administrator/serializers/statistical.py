from rest_framework import serializers
from goods.models import GoodsVisitCount


class GoodsCountSerializer(serializers.ModelSerializer):
    """
    商品分类序列化器
    """
    # category字段为外键字段 ------->  关联嵌套序列化返回（三种方式）

    # 对category字段单独指定返回
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GoodsVisitCount
        fields = ('count','category')