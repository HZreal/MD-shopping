from django.db import models

# Create your models here.


# 省市区模型类
class Area(models.Model):
    name = models.CharField(max_length=20, verbose_name='名称')
    # self表示此表为自关联
    # on_delete指定删除记录的模式为：设置对应记录的外键字段为NULL：仅在该外键字段null = True允许为null时可用
    # related_name 自定义主表中对从表的关联字段为sub(默认是主表名小写_set，这里默认即是area_set)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='sub', null=True, blank=True, verbose_name='上级行政名称')


    class Meta:
        db_table = 'tb_areas'
        verbose_name = '省市区'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
