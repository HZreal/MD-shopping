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