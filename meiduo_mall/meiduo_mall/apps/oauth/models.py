from django.db import models
from meiduo_mall.utils.models import BaseModel

# qq登录用户模型类

class OAuthQQUser(BaseModel):
    # TODO 写法'users.User'因为关联字段在其他子应用下的模型类中
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')       # Django对于外键在数据库中的字段会默认在变量名后加_id
    # openid是此网站上唯一对应用户qq身份的标识，网站可将此ID进行存储便于用户下次登录时辨识其身份，或将其与用户在网站上的原有账号进行绑定。
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)              # db_index=True表示为此字段创建索引

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'                                        # verbose_name指定在admin管理界面中显示中文，verbose_name表示单数形式的显示
        verbose_name_plural = verbose_name                                     # verbose_name_plural表示复数形式的显示，中文的单数和复数一般不作区别
































































