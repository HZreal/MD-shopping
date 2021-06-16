from django.urls import path, re_path
from verifications import views

urlpatterns = [
    # 生成图形验证码(接收请求图片数据)
    re_path(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),

    # 短信验证码
    re_path(r'^sms_codes/(?P<mobile>1[34578]\d{9})/$', views.SMSCodeView.as_view()),

]














