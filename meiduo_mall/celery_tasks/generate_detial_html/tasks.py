import logging
from celery_tasks.main import celery_app
from goods.models import SKU


logger = logging.getLogger('django')


# 异步生成新的详情页页面
@celery_app.task(bind=True, name='get_detail_html')
def get_detail_html(sku_id):
    # 获取当前sku对象
    sku = SKU.objects.get(id=sku_id)