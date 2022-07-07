# 自定义文件存储类的url方法
from django.core.files.storage import Storage
from django.conf import settings


# (官方文档)自定义文件存储类时必须重写 _open()和 _save() 方法 其他方法根据需求重写
class FastDFSStorage(Storage):

    # 文件存储类的初始化方法：option提供给外界传参的接口
    # def __init__(self, option=None):
    #     if not option:
    #         option = settings.CUSTOM_STORAGE_OPTIONS
    def __init__(self, fdfs_base_url=None):
        # if not fdfs_base_url:
        #     self.fdfs_base_url = settings.FDFS_BASE_URL
        # self.fdfs_base_url = fdfs_base_url
        self.fdfs_base_url = fdfs_base_url or settings.FDFS_BASE_URL

    # 打开文件时会被调用(官方文档required)：参数name为文件路径，mode为打开方式
    def _open(self, name, mode='rb'):
        # 当前需求不是打开某个文件，此方法目前无用，但又必须重写
        pass

    # 保存文件时会被调用(required)
    def _save(self, name, content):
        # 当前无需求，但必须重写，后续学习后台管理系统时再具体重写，实现文件上传到FastDFS服务器
        pass

    # url()方法 返回name所代表的文件内容的URL   参数name为传入的目录，缺少协议,ip,端口
    # 表面上调用的是ImageField的url方法。但是内部会去调用文件存储类的url()方法
    def url(self, name):
        # 需求：返回全路径 http://192.168.94.131:8888/group1/M00/00/00/wKhnnlxw_gmAcoWmAAEXU5wmjPs35.jpeg
        # return 'http://192.168.94.131:8888/' + name
        # return settings.FDFS_BASE_URL + name
        return self.fdfs_base_url + name

    # 自定义重写
    # Storage.delete()
    # Storage.exists()
    # Storage.listdir()
    # Storage.size()
    # Storage.url()
