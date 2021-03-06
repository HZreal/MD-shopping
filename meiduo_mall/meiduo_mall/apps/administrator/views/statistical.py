# 数据统计
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import date, timedelta
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from administrator.serializers.statistical import GoodsCountSerializer
from administrator.utils import BasicAPIView
from goods.models import GoodsVisitCount
from users.models import User


class UserTotalCountView(BasicAPIView):
    """
    用户总量统计
    """

    # JWT认证以及DRF封装的Session、Basic认证
    # authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication]
    # JWT认证时，请求头中添加 key为Authorization   value为JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo2LCJ1c2VybmFtZSI6ImFkbWluIiwiZXhwIjoxNjM2Njk4OTEyLCJlbWFpbCI6Imh1YW5nemhlbkBxcS5jb20ifQ.h0zu-P2zK3xSBRneVLddlvFxMMcYYJ-eD1c-fJGm7Qc
    # 注意：value值前面有'JWT和空格'，可以在Django生成token值时加上前缀,则前端请求时无需额外加上

    # 指定管理员权限
    permission_classes = [IsAdminUser, ]

    def get(self, request):
        now_date = date.today()
        count = User.objects.all().count()
        data = {
            'count': count,
            'date': str(now_date),
        }
        return self.response_res(data=data)


class UserDayCountView(BasicAPIView):
    """
    日增用户统计
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        """

        :param request:
        :return:
        """
        now_date=date.today()
        # 获取当日注册用户数量 date_joined 记录创建账户时间
        count = User.objects.filter(date_joined__gte=now_date).count()
        data = {
            'count': count,
            'date': str(now_date),
        }
        return self.response_res(data)


class UserActiveCountView(BasicAPIView):
    """
    日活跃用户统计
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()
        # 获取当日登录用户数量  last_login记录最后登录时间
        count = User.objects.filter(last_login__gte=now_date).count()
        data = {
            'count': count,
            'date': str(now_date),
        }
        return self.response_res(data)


class UserOrderCountView(BasicAPIView):
    """
    日下单用户量统计
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()
        # 获取当日下单用户数量  orders__create_time 订单创建时间
        count = User.objects.filter(orders__create_time__gte=now_date).count()
        data = {
            'count': count,
            'date': str(now_date),
        }
        return self.response_res(data)


class UserMonthCountView(BasicAPIView):
    """
    月增用户统计
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        now_date = date.today()
        start_date = now_date - timedelta(days=29)

        res_list = []
        for i in range(30):
            index_date = start_date + timedelta(days=i)
            next_date = index_date + timedelta(days=1)
            # 查询条件是大于当前日期index_date，小于明天日期的用户cnext_date，得到当天用户量
            count = User.objects.filter(date_joined__gte=index_date, date_joined__lt=next_date).count()
            day_count = {
                'date': str(index_date),
                'count': count
            }
            res_list.append(day_count)

        return self.response_res(res_list)


class GoodsDayView(BasicAPIView):
    """
    日分类商品访问量
    """

    def get(self,request):
        now_date = date.today()
        queryset = GoodsVisitCount.objects.filter(date=now_date)

        # 查询集序列化返回
        s = GoodsCountSerializer(queryset, many=True)

        return self.response_res(s.data)
