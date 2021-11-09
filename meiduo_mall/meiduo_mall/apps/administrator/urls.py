from django.urls import path, re_path
from rest_framework_jwt.views import obtain_jwt_token
from administrator.views import *


urlpatterns = [
    re_path(r'^authorizations/$', obtain_jwt_token),

]