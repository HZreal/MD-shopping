from django.db import models

# 定义一个抽象模型基类，其中字段被QQ登录，订单等多个模型类继承
class BaseModel(models.Model):
     create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')             # auto_now_add 保存首次创建的时间，以后不会变
     update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')                 # auto_now 保存修改数据的时间，每次修改都会变

     class Meta:
         abstract = True              # 说明此模型类是抽象类，用于继承，数据库迁移时不会创表







