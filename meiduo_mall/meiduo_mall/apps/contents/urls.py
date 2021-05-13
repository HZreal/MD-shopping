from django.urls import path, re_path
from contents import views
urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    # path('', views.IndexView.as_view(), name='index'),




]