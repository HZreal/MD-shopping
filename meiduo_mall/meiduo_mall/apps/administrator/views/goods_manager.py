# from fdfs_client.client import Fdfs_client
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from administrator.serializers.goods_manager import SPUSpecificationSerializer, ImageSeriazlier, SKUSeriazlier, SKUGoodsSerializer, SKUCategorieSerializer
from administrator.utils import CustomPagination
from goods.models import SPUSpecification, SKUImage, SKU, GoodsCategory
from django.conf import settings
from celery_tasks.generate_detial_html.tasks import get_detail_html

class GoodsSpecsView(ModelViewSet):
    """
    商品规格
    """
    serializer_class = SPUSpecificationSerializer
    queryset = SPUSpecification.objects.all()
    pagination_class = CustomPagination


class ImageView(ModelViewSet):
    """
    商品图片
    """
    serializer_class = ImageSeriazlier
    queryset = SKUImage.objects.all()
    pagination_class = CustomPagination

    def simple(self, request):
        """
        获取图片关联的sku的id     匹配url中的simple
        :param request:
        :return:
        """
        data = SKU.objects.all()
        s = SKUSeriazlier(data, many=True)
        return Response(s.data)

"""
    # 重写拓展类的保存业务逻辑
    def create(self, request, *args, **kwargs):
        # 创建FastDFS连接对象
        client = Fdfs_client(settings.FASTDFS_PATH)
        # 获取前端传递的image文件
        data = request.FILES.get('image')
        # 上传图片到fastDFS
        res = client.upload_by_buffer(data.read())
        # 判断是否上传成功
        if res['Status'] != 'Upload successed.':
            return Response(status=403)
        # 获取上传后的路径
        image_url = res['Remote file_id']
        # 获取sku_id
        sku_id = request.data.get('sku')[0]
        # 保存图片
        img = SKUImage.objects.create(sku_id=sku_id, image=image_url)

        # 生成新的详情页页面
        get_detail_html.delay(img.sku.id)
        # 返回结果
        return Response(
            {
                'id': img.id,
                'sku': sku_id,
                'image': img.image.url
            },
            status=201  # 前端需要接受201状态
        )

    # 重写拓展类的更新业务逻辑
    def update(self, request, *args, **kwargs):

        # 创建FastDFS连接对象
        client = Fdfs_client(settings.FASTDFS_PATH)
        # 获取前端传递的image文件
        data = request.FILES.get('image')
        # 上传图片到fastDFS
        res = client.upload_by_buffer(data.read())
        # 判断是否上传成功
        if res['Status'] != 'Upload successed.':
            return Response(status=403)
        # 获取上传后的路径
        image_url = res['Remote file_id']
        # 获取sku_id
        sku_id = request.data.get('sku')[0]
        # 查询图片对象
        img=SKUImage.objects.get(id=kwargs['pk'])
        # 更新图片
        img.image=image_url
        img.save()

           # 生成新的详情页页面
        get_detail_html.delay(img.sku.id)
        # 返回结果
        return Response(
            {
                'id': img.id,
                'sku': sku_id,
                'image': img.image.url
            },
            status=201  # 前端需要接受201状态码
        )
"""

class SKUGoodsView(ModelViewSet):
    """
    商品SKU
    """
    serializer_class = SKUGoodsSerializer
    pagination_class = CustomPagination

    # 重写get_queryset方法，判断是否传递keyword查询参数
    def get_queryset(self):
        # 提取keyword
        keyword = self.request.query_params.get('keyword')

        if keyword == '' or keyword is None:
            return SKU.objects.all()
        else:
            return SKU.objects.filter(name=keyword)


class SKUCategorieView(ListAPIView):
    """
    SKU三级分类
    """
    serializer_class = SKUCategorieSerializer
    # 根据数据存储规律parent_id大于37为三级分类信息，查询条件为parent_id__gt=37
    queryset = GoodsCategory.objects.filter(parent_id__gt=37)










