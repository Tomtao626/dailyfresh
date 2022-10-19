from django.shortcuts import render
from django.views.generic import View
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from django_redis import get_redis_connection

from apps.user.models import User, Address
from apps.goods.models import GoodsSKU
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from celery_tasks.chient import send_active_email
from utils.mixin import LoginRequiredMixin
from utils.handle_data import body_data_handle
import re


# Create your views here.
# /user/register

# 注册类
class RegisterView(View):

    def get(self, request):
        """显示注册界面"""
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('goods:index'))
        return render(request, 'register.html')

    def post(self, request):
        """pc客户端进行注册处理"""
        # 接收数据
        response = {
            'code': 1,
            'data': [],
            'msg': ''
        }
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 进行数据校验
        if not all([username, password, email]):
            # 数据不完整
            response['msg'] = '数据不完整'

            return JsonResponse(response)
            # return render(request, 'register.html', {'errmsg': '数据不完整'})

        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            response['msg'] = '邮箱格式不正确'

            return JsonResponse(response)

        if allow != 'on':
            response['msg'] = '请同意协议'

            return JsonResponse(response)

        try:
            user = User.objects.get(username=username)

        except User.DoesNotExist:
            user = None

        if user:
            response['msg'] = '用户名已存在'

            return JsonResponse(response)

        # 进行业务处理：进行用户注册

        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()
        # 发送激活邮件， 包含激活链接：/user/active/?Id=,username=,
        # 激活连接中需要包含用户的身份信息， 并且要把身份信息进行加密

        # 生成用户的身份信息， 生成激活token
        serializer = Serializer(settings.SECRET_KEY, 1800)
        info = {'confirm': user.id}
        token = serializer.dumps(info)
        token = token.decode('utf8')
        # 发邮件
        send_active_email.delay(email, username, token)
        # 返回应答, 跳转到首页
        response['code'] = 0
        response['data'] = [('url', reverse('goods:index'))]
        response['msg'] = '注册成功'

        return JsonResponse(response)


# 激活用户类
class ActiveView(View):
    """用户激活"""

    def get(self, request, token):
        """进行用户激活"""
        # 进行解密 获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 1800)
        try:
            info = serializer.loads(token)
            user_id = info['confirm']
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            return HttpResponseRedirect(reverse('user:login'))
            # 跳转到登录界面
        except SignatureExpired as e:
            # 激活链接已过期
            return JsonResponse('激活链接已过期')


# 登录类
class LoginView(View):
    """登录"""

    def get(self, request):
        """显示登录界面"""
        if request.user.is_authenticated:
            next_url = request.GET.get('next', reverse('goods:index'))
            return HttpResponseRedirect(next_url)
        if 'username' in request.COOKIES:
            username = request.COOKIES['username']
            checked = 'checked'
        else:
            username = ''
            checked = ''
        # 使用模版
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        """登录校验"""
        # 接收数据
        response = {
            'code': 1,
            'data': [],
            'msg': ''
        }
        username = request.POST.get('username')
        password = request.POST.get('pwd')
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
                if user.is_active:
                    login(request, user)
                    next_url = request.GET.get('next', reverse('goods:index'))
                    response['code'] = 0
                    response['msg'] = '登录成功'
                    response['data'] = [{'next': next_url}]
                    # 判断是否需要记住用户名
                    remember = request.POST.get('remember')
                    res = JsonResponse(response)
                    if remember == 'on':
                        res.set_cookie('username', username, max_age=7 * 24 * 3600)
                    else:
                        res.delete_cookie('username')
                    return res
                    # 记录用户的登录状态
                else:
                    response['msg'] = '账号未激活'
                    return JsonResponse(response)
            else:
                response['msg'] = '密码不正确'
                return JsonResponse(response)
        else:
            response['msg'] = '用户不存在'
            return JsonResponse(response)


# 登出类
class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('goods:index'))


# 用户信息类
class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        # 获取用户的个人信息
        user = request.user
        address = Address.objects.get_default_address(user)
        # 获取用户的历史浏览记录
        # StrictRedis(host='127.0.0.1', port='6379', db=9)
        con = get_redis_connection('default')

        # 取出用户浏览记录
        history_key = 'history_%d'%user.id

        # 获取用户最新浏览的5个商品的id
        sku_ids = con.lrange(history_key, 0, 4)

        # 从数据库中查询用户浏览的商品的具体信息
        # goods_li = GoodsSKU.objects.filter(id__in=sku_ids)
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)
        # 用户历史数据排序
        return render(request, 'user_center_info.html', {'page': 'user', 'address': address, 'goods_li': goods_li})


# 用户订单类
class UserOrderView(LoginRequiredMixin, View):
    def get(self, request):
        # 获取用户的订单信息
        return render(request, 'user_center_order.html', {'page': 'order'})


# 用户收货地址类
class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        # 获取用户的默认收货地址
        user = request.user
        try:
            address = Address.objects.filter(user=user, is_delete=False).order_by('-is_default')
        except Address.DoesNotExist:
            address = None

        return render(request, 'user_center_site.html', {'page': 'address', 'address': address})

    def post(self, request):
        """地址的添加"""
        # 接收数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        id = request.POST.get('id')
        # 校验数据
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})

        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机号不正确'})

        # 业务处理
        user = request.user

        if not id:
            address = Address.objects.get_default_address(user)
            if address:
                is_default = False
            else:
                is_default = True

            Address.objects.create(user=user, receiver=receiver, addr=addr, zip_code=zip_code, phone=phone,
                                   is_default=is_default)
        else:
            try:
                address = Address.objects.filter(id=id).update(user=user, receiver=receiver, addr=addr,
                                                               zip_code=zip_code, phone=phone)
            except Address.DoesNotExist:
                address = None

        # 返回应答
        return HttpResponseRedirect(reverse('user:address'))

    def patch(self, request):
        """修改默认 ， 逻辑删除"""
        response = {
            'code': 1,
            'data': [],
            'msg': ''
        }
        data = body_data_handle(request.body)
        user_id = data.get('userId')
        address_id = data.get('addressId')
        code = data.get('code')
        print(data.get('code'))

        # 数据判断
        if not all([user_id, address_id, code]):
            response['msg'] = '数据不完整'
            return JsonResponse(response)
        if not (code == 'address' or code == 'delete'):
            response['msg'] = 'code码不正确'
            return JsonResponse(response)

        # 逻辑判断
        if code == 'address':
            Address.objects.filter(user=int(user_id), is_default=True).update(is_default=False)
            Address.objects.filter(id=int(address_id)).update(is_default=True)
            response['code'] = 0
            response['data'] = [{'url': reverse('user:address')}]
            response['msg'] = '地址修改成功'
            return JsonResponse(response)
        if code == 'delete':
            Address.objects.filter(id=int(address_id)).update(is_delete=True)
            response['code'] = 0
            response['data'] = [{'url': reverse('user:address')}]
            response['msg'] = '地址删除成功'
            return JsonResponse(response)
