# 为什么这些都是from django. 系统都能找到？因为系统导包路径列表中有一个指向了site-package
# print(sys.path)    # 查看导包路径列表

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
