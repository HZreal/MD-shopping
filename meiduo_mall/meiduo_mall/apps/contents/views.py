from django.shortcuts import render


from django.views import View


# 首页
class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')
    def post(self, request):
        pass