# areas.url
from django.urls import path, re_path
from areas import views


urlpatterns = [
    # 接收前端axios请求查询省份数据或者市区数据
    path('areas/', views.AreasView.as_view()),


]
















