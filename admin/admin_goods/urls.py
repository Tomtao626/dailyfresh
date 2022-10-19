"""dailyfresh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.conf.urls import url
from .views import GoodsTypeView, GoodsTypeJsonView

urlpatterns = [
    url(r'^goodsTypeForm$', GoodsTypeView.as_view({'get': 'list', 'post': 'create', 'put': 'update'}),
        name='admin_good_type_form'),  # 商品类型方法
    url(r'^goodsTypeJson$', GoodsTypeJsonView.as_view({'patch': 'partial_update', 'delete': 'destroy'}),
        name='admin_good_type_json'),  # 商品类型方法
    # path('addGoodsType', views.addGoodsType, name='admin_goods_type_add'),  # 添加商品类型
    # path('modifyGoodsType', views.modifyGoodsType, name='admin_goods_type_modify'),     # 修改商品类型
    # path('deleteGoodsType', views.deleteGoodsType, name='admin_goods_type_delete'),
    # path('trueDeleteGoodsType', views.trueDeleteGoodsType, name='admin_goods_type_true_delete')
]
