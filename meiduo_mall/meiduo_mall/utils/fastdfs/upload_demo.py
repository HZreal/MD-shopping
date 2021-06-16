# 上传文件测试

# 可以进入Python shell进行测试
# python manage.py shell


# 1. 导入FastDFS客户端扩展
from fdfs_client.client import Fdfs_client

# 2. 创建FastDFS客户端实例：加载配置文件(tracker服务器端口22122)
client = Fdfs_client('meiduo_mall/utils/fastdfs/client.conf')

# 3. 调用FastDFS客户端上传文件方法
ret = client.upload_by_filename('E:/Users/huangzhen/Desktop/pic/carton.png')



# ret = {
#     'Group name': 'group1',
#     'Remote file_id': 'group1/M00/00/00/wKhnnlxw_gmAcoWmAAEXU5wmjPs35.jpeg',
#     'Status': 'Upload successed.',
#     'Local file name': '/Users/zhangjie/Desktop/kk.jpeg',
#     'Uploaded size': '69.00KB',
#     'Storage IP': '192.168.103.158'
#  }

# ret = {
#     'Group name': 'Storage组名',
#     'Remote file_id': '文件索引，可用于下载',
#     'Status': '文件上传结果反馈',
#     'Local file name': '上传文件全路径',
#     'Uploaded size': '文件大小',
#     'Storage IP': 'Storage地址'
#  }


# 图片数据一般都会放到storage中存储
# 本项目图片数据包放在storage目录下解压


# 因为FastDFS擅长存储静态文件，但是不擅长提供静态文件的下载服务，
# 所以我们一般会将Nginx代理服务器(8888)绑定到Storage，提升下载性能
# 直接浏览器输入下载 http://192.168.94.131:8888/group1/M00/00/00/CtM3BVnifxeAPTodAAPWWMjR7sE487.jpg










