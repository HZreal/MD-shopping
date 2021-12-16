from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response

# 自定义JWT认证成功后的返回值
def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': 'JWT ' + token,
        'id': user.id or request.user.id,
        'user': user.username or request.user.name,
    }


# 封装APIView响应数据类型
class BasicAPIView(APIView):

    def response_res(self, data):
        """

        :param data:
        :return:
        """
        res = {
            'code': 0,
            'msg': 'success'
        }
        res.update({'data': data})
        return Response(res)


# 自定义DRF分页器
class CustomPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100
    page_query_param = 'page'
    page_size_query_param = 'size'

    # 重写分页返回方法，按照指定的字段进行分页数据返回
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,        # 总数量
            'lists': data,                             # 用户数据
            'page': self.page.number,                  # 当前页数
            'pages': self.page.paginator.num_pages,    # 总页数
            'pagesize': self.page_size                 # 后端指定的页容量

        })




















