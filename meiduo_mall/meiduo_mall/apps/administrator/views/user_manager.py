from rest_framework.generics import ListAPIView, CreateAPIView, ListCreateAPIView
from administrator.serializers.user_manager import UserManagerSerializer, UserAddSerializer
from administrator.utils import CustomPagination
from users.models import User


class UserQuerySearchView(ListCreateAPIView):
    """
    用户查询，指定keyword搜索
    """

    pagination_class = CustomPagination

    # serializer_class = UserManagerSerializer
    def get_serializer_class(self):
        # 请求方式是GET，则是获取用户数据返回UserSerializer
        if self.request.method == 'GET':
            return UserManagerSerializer
        else:
            # POST请求，完成保存用户，返回UserAddSerializer
            return UserAddSerializer

    # 重写get_queryset方法，根据前端是否传递keyword值返回不同查询结果， 必须返回一个查询集query_set
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if not keyword or keyword == '':
            return User.objects.all()
        else:
            return User.objects.filter(username=keyword)


