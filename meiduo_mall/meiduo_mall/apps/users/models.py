# Django内嵌了ORM框架
# 作用：把数据库表的行与相应的对象建立关联,互相转换.使得数据库的操作面向对象
# ORM操作数据库需要驱动程序，mysql驱动程序就是MySQLdb
# 每个模型类都隐藏着一个属性objects = Manager()
from django.contrib.auth.models import AbstractUser
from django.db import models
from meiduo_mall.utils.models import BaseModel

# Django自带用户认证系统：处理用户账号、组、权限以及基于cookie的用户会话。
# Django认证系统位置：
#         django.contrib.auth包含认证框架的核心和默认的模型。
#         django.contrib.contenttypes是Django内容类型系统，它允许权限与你创建的模型关联。
# Django认证系统同时处理认证和授权：
#         认证：验证一个用户是否它声称的那个人，可用于账号登录。
#         授权：授权决定一个通过了认证的用户被允许做什么。
# Django认证系统包含的内容：
#         用户：用户模型类、用户认证。
#         权限：标识一个用户是否可以做一个特定的任务，MIS系统常用到。
#         组：对多个具有相同权限的用户进行统一管理，MIS系统常用到。
#         密码：一个可配置的密码哈希系统，设置密码、密码校验。


# User类继承自AbstractUser,封装了username，password必选字段和其他可选字段以及部分方法，内含objects =UserManager()进行管理
# UserManager管理类封装了操作用户模型类User的方法：创建用户如create_user，create_superuser，用户认证(登录)如authenticate
# 处理密码的方法：
#         设置密码：set_password(raw_password)
#         校验密码：check_password(raw_password)
class User(AbstractUser):
    # 用户名和手机号都是唯一不可重复的
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    # 邮件是否激活(追加字段，需要给个默认值)
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    default_address = models.ForeignKey('Address', related_name='users', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='默认地址')


    # 内嵌类：定义元数据(不是字段的数据) -- 比如数据库表名，排序选项, admin选项，起别名等等
    class Meta():
        # 模型类在数据库中生成的表名默认是  应用名.类名(users.user)
        db_table = 'tb_user'                                  # 自定义表名
        verbose_name = '用户'                                 # verbose_name指定在admin管理界面中显示中文
        verbose_name_plural = verbose_name                    # verbose_name_plural表示复数形式的显示

    def __str__(self):
        return self.username


# 用户地址模型类
class Address(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')                  # 这里的related_name相当于user_set
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮件')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        # 查询时默认的排序方式，是一个列表，列举的排序方式
        ordering = ['-update_time']             # 按更新时间倒序排序

    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    # title = models.CharField(max_length=20, verbose_name='地址名称')
    # receiver = models.CharField(max_length=20, verbose_name='收货人')
    # province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    # city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    # district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')
    # place = models.CharField(max_length=50, verbose_name='地址')
    # mobile = models.CharField(max_length=11, verbose_name='手机')
    # tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    # email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮件')
    # is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')
































































































































































