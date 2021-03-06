from django.shortcuts import render
from django.views import View
from areas.models import Area
from django import http
from meiduo_mall.utils.response_code import RETCODE
import logging
from django.core.cache import cache                # 进入可看到DEFAULT_CACHE_ALIAS = 'default' 即Django默认缓存位置为'default'


logger = logging.getLogger('django')

# 接收前端axios请求查询省、市区数据：省份数据会在页面加载完成就触发axios请求，而市区数据则由vue监听用户操作下拉框时发送请求
class AreasView(View):
    def get(self, request):
        area_id = request.GET.get('area_id')                   # area_id为前端传过来的省市id
        # 判断当前需要查询的是省份数据还是市区数据
        if not area_id:          # 当前需要省级数据
            # 先判断是否有缓存数据
            province_list = cache.get('province_list')                    # redis 'default' 0号库
            if not province_list:
                # 没有缓存数据则查库获取省级数据
                try:
                    province_model_list = Area.objects.filter(parent_id__isnull=True)
                    # 需要将模型类列表(json无法识别)转成字典列表：
                    # province_list = []
                    # for province_model in province_model_list:
                    #     province_dict = {'id': province_model.id, 'name': province_model.name}
                    #     province_list.append(province_dict)
                    # 列表推导式简写
                    province_list = [{'id': province_model.id, 'name': province_model.name} for province_model in province_model_list]

                    # 缓存省份字典列表数据到cache：即存储到redis默认的'default'配置中(0号库)
                    cache.set('province_list', province_list, 3600)

                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '查询省份数据错误'})

            # 响应省份json数据
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})

        else:               # 当前需要市区县级数据
            # 先判断是否有缓存数据
            sub_data = cache.get('sub_area_' + area_id)
            if not sub_data:
                # 没有缓存数据则查库获取市或区县数据
                try:
                    # 需求的json数据：sub_data = {"id":130000, "name":"河北省", "subs":[{"id":130100, "name":"石家庄市"}, {}, {}, {"id":130104, "name":"桥西区"}]}
                    area = Area.objects.get(id=area_id)
                    sub_area_list = area.sub.all()                                              # 子地区对象列表
                    # sub_area_list = Area.objects.filter(parent_id=area_id)                    # 亦可

                    # 将模型类列表转成字典列表
                    # subs = []
                    # for sub_area in sub_area_list:
                    #     sub_area_dict = {'id': sub_area.id, 'name': sub_area.name}
                    #     subs.append(sub_area_dict)
                    # sub_data = {'id': area.id, 'name': area.name, 'subs': subs}
                    # 使用列表推导式更简洁
                    sub_data = {'id': area.id, 'name': area.name, 'subs': [{'id': sub_area.id, 'name': sub_area.name} for sub_area in sub_area_list]}

                    # 缓存数据到cache
                    cache.set('sub_area_' + area_id, sub_data, 3600)

                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '城市或区县数据错误'})

            # 响应json数据
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})


















































































