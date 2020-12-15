from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password

from apps.goods.models import GoodsType
from apps.user.models import User


class AdminLoginView(View):
    """后台登录接口"""

    def post(self, request):
        """管理界面登录接口"""
        # 初始化返回结果
        response = {
            'code': 1,
            'data': [],
            'msg': ''
        }
        # 获取数据
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 逻辑处理
        if not all([username, password]):
            response['msg'] = '数据不完整'
            return JsonResponse(response)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user is not None:
            pwd = user.password
            if check_password(password, pwd):
                if user.is_superuser:
                    login(request, user)
                    response['code'] = 0
                    response['msg'] = '登录成功'
                    response['data'] = []
                    # 判断是否需要记住用户名
                    return JsonResponse(response)
                else:
                    response['msg'] = '不是超级管理员'
                    return JsonResponse(response)
                # 记录用户的登录状态
            else:
                response['msg'] = '密码不正确'
                return JsonResponse(response)
        else:
            response['msg'] = '用户不存在'
            return JsonResponse(response)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(AdminLoginView, self).dispatch(*args, **kwargs)
