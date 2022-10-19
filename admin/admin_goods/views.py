from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.decorators import action, api_view
from drf_yasg.utils import swagger_auto_schema, no_body
from drf_yasg import openapi
from apps.goods.models import GoodsType
from utils.fdfs_storage import fastDFSStorage
from .serializers import GoodsTypeSerializer
from django.views.decorators.csrf import csrf_exempt
from utils.handle_data import body_data_handle
import json


class GoodsTypeView(viewsets.ViewSet):
    """商品类型视图类"""
    # parser_classes = [FormParser]
    parser_classes = [MultiPartParser]
    get_param = [
        openapi.Parameter("id", openapi.IN_QUERY, description="商品类型ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter("name", openapi.IN_QUERY, description="商品类型名称", type=openapi.TYPE_STRING),
        openapi.Parameter("pageNo", openapi.IN_QUERY, description="页数", type=openapi.TYPE_INTEGER),
        openapi.Parameter("pageSize", openapi.IN_QUERY, description="个数", type=openapi.TYPE_INTEGER),
    ]

    @swagger_auto_schema(operation_description="获取商品类型列表",
                         operation_id="获取商品类型列表",
                         responses={404: 'id not found'},
                         manual_parameters=get_param)
    @csrf_exempt
    @action(detail=True, methods=['GET'])
    def list(self, request):
        """获取商品类型列表"""
        response = {
            'code': 1,
            'data': [],
            'msg': ''
        }
        if request.method == 'GET':
            id = request.GET.get('id')  # 商品类型ID
            name = request.GET.get('name')  # 商品类型名称
            page_no = request.GET.get('pageNo')  # 页数
            page_size = request.GET.get('pageSize')  # 个数
            # 返回初始值
            try:
                goodsType = GoodsType.objects.filter(is_delete=False)
            except GoodsType.DoesNotExist:
                goodsType = None

            if goodsType:
                if all([page_no, page_size]):
                    page_no = int(page_no)
                    page_size = int(page_size)
                    if name:
                        goodsType = goodsType.filter(name__contains=name)

                    total = goodsType.count()
                    goodsType = goodsType[(page_no - 1) * page_size: page_size]


                    if goodsType:
                        data = GoodsTypeSerializer(goodsType, many=True).data
                    else:
                        data = []
                    response['code'] = 0
                    response['data'] = data
                    response['total'] = total
                    response['pageNo'] = page_no
                    response['pageSize'] = page_size
                    response['msg'] = '获取商品类型列表成功'
                    return JsonResponse(response)
                elif id:
                    goodsType = goodsType.get(id=id)
                    response['code'] = 0
                    response['data'] = GoodsTypeSerializer(goodsType, many=True).data
                    response['msg'] = '获取单个商品类型成功'
                    return JsonResponse(response)
                else:
                    if name:
                        goodsType = goodsType.objects.filter(name__contains=name)
                    response['code'] = 0
                    response['data'] = GoodsTypeSerializer(goodsType, many=True).data
                    response['msg'] = '获取商品类型列表成功'
                    return JsonResponse(response)
            else:
                response['msg'] = '商品类型列表为空'
                return JsonResponse(response)
        else:
            response['msg'] = '请求格式不正确, 应该是GET'
            return JsonResponse(response)

    post_param = [
        openapi.Parameter("name", openapi.IN_FORM, description="商品类型名字", type=openapi.TYPE_STRING),
        openapi.Parameter("logo", openapi.IN_FORM, description="商品类型class", type=openapi.TYPE_STRING),
        openapi.Parameter("file", openapi.IN_FORM, description="image图片", type=openapi.TYPE_FILE),
    ]

    @swagger_auto_schema(operation_description="添加商品类型列表",
                         operation_id="添加商品类型列表",
                         responses={404: 'id not found'},
                         manual_parameters=post_param,
                         )
    @csrf_exempt
    @action(detail=True, methods=['POST'])
    def create(self, request):
        """添加商品类型列表"""
        response = {
            'code': 1,
            'data': [],
            'msg': ''
        }
        if request.method == 'POST':
            name = request.POST.get('name')
            logo = request.POST.get('logo')
            file = request.FILES.get('file')

            # 逻辑判断
            if not all([name, logo, file]):
                response['msg'] = '数据不完全'
                return JsonResponse(response)
            image = fastDFSStorage('', file)
            print(image)
            try:
                goods_type = GoodsType.objects.create(name=name, logo=logo, image=image)
            except GoodsType.DoesNotExist:
                goods_type = None

            if goods_type:
                response['code'] = 0
                response['msg'] = '保存成功'
                return JsonResponse(response)
            else:
                response['msg'] = '图片保存失败'
                return JsonResponse(response)
        else:
            response['msg'] = '请求格式不正确, 应该是GET'
            return JsonResponse(response)

    put_param = [
        openapi.Parameter("id", openapi.IN_FORM, description="商品类型ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter("name", openapi.IN_FORM, description="商品类型名字", type=openapi.TYPE_STRING),
        openapi.Parameter("logo", openapi.IN_FORM, description="商品类型class", type=openapi.TYPE_STRING),
        openapi.Parameter("file", openapi.IN_FORM, description="image图片", type=openapi.TYPE_FILE),
    ]

    @swagger_auto_schema(operation_description="修改商品类型列表",
                         operation_id="修改商品类型列表",
                         responses={404: 'id not found'},
                         manual_parameters=put_param,
                         )
    @csrf_exempt
    @action(detail=True, methods=['PUT'])
    def update(self, request):
        """修改商品类型列表"""
        response = {
            'code': 1,
            'data': [],
            'msg': ''
        }
        if request.method == 'PUT':
            goods_type_id = request.POST.get('id')
            goods_type_name = request.POST.get('name')
            goods_type_logo = request.POST.get('logo')
            goods_type_file = request.FILES.get('file')
            if not all([goods_type_file, goods_type_id, goods_type_logo, goods_type_name]):
                response['msg'] = '数据不完整'
                return JsonResponse(response)
            try:
                goods_type = GoodsType.objects.get(id=goods_type_id)
            except GoodsType.DoesNotExist:
                goods_type = None

            if goods_type:
                goods_type.name = goods_type_name
                goods_type.logo = goods_type_logo
                goods_type.image = fastDFSStorage('', goods_type_file)
                goods_type.save()
                response['code'] = 0
                response['msg'] = '修改成功'
                return JsonResponse(response)
            else:
                response['msg'] = '修改失败，id没有找到或者不正确'
                return JsonResponse(response)

        else:
            response['msg'] = '请求格式不正确, 应该是PUT'
            return JsonResponse(response)


class GoodsTypeJsonView(viewsets.ViewSet):
    parser_classes = [JSONParser]

    patch_param = openapi.Schema(type=openapi.TYPE_OBJECT, required=['id'], properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER, title="商品类型ID")
    })

    @swagger_auto_schema(operation_description="逻辑删除商品类型列表",
                         operation_id="逻辑删除商品类型列表",
                         request_body=patch_param,
                         security=[]
                         )
    @csrf_exempt
    @action(methods=['patch'], detail=True)
    def partial_update(self, request):
        """逻辑删除商品类型列表"""
        response = {
            'code': 1,
            'data': [],
            'msg': ''
        }
        if request.method == 'PATCH':
            data = json.loads(request.body.decode().replace("'", "\""))
            goods_type_id = data.get('id')

            if not goods_type_id:
                response['msg'] = '数据不完整'
                return JsonResponse(response)

            try:
                goods_type = GoodsType.objects.get(id=goods_type_id)
            except GoodsType.DoesNotExist:
                goods_type = None

            if goods_type:
                goods_type.is_delete = True
                goods_type.save()
                response['code'] = 0
                response['msg'] = '删除成功'
                return JsonResponse(response)
            else:
                response['msg'] = '删除失败，id没有找到或者不正确'
                return JsonResponse(response)
        else:
            response['msg'] = '请求格式不正确, 应该是PATCH'
            return JsonResponse(response)

    delete_param = openapi.Schema(type=openapi.TYPE_OBJECT, required=['id'], properties={
        'id': openapi.Schema(type=openapi.TYPE_INTEGER, title="商品类型ID")
    })

    @swagger_auto_schema(operation_description="真删商品类型列表",
                        operation_id='真删商品类型列表',
                         request_body=delete_param,
                         security=[],
                         )

    @csrf_exempt
    @action(detail=True, methods=['delete'])
    def destroy(self, request):
        """真删商品类型列表"""
        response = {
            'code': 1,
            'data': [],
            'msg': ''
        }
        if request.method == 'DELETE':

            data = json.loads(request.body.decode().replace("'", "\""))
            print(data)
            goods_type_id = data.get('id')

            if not goods_type_id:
                response['msg'] = '数据不完整'
                return JsonResponse(response)

            try:
                goods_type = GoodsType.objects.get(id=goods_type_id)
            except GoodsType.DoesNotExist:
                goods_type = None

            if goods_type:
                goods_type.delete()
                response['code'] = 0
                response['msg'] = '删除成功'
                return JsonResponse(response)
            else:
                response['msg'] = '删除失败，id没有找到或者不正确'
                return JsonResponse(response)
        else:
            response['msg'] = '请求格式不正确, 应该是DELETE'
            return JsonResponse(response)