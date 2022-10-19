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
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

from rest_framework import permissions
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
swagger_info = openapi.Info(
    title="天天生鲜后台 API",
    default_version='v1',
    description="""""",  # noqa
    terms_of_service="",
    contact=openapi.Contact(email="751825253@qq.com"),
    license=openapi.License(name="tomtao626"),
)

SchemaView = get_schema_view(
    validators=['ssv', 'flex'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('user/', include(('user.urls', 'user'), namespace='user')),
    path('cart/', include(('cart.urls', 'cart'), namespace='cart')),
    path('order/', include(('order.urls', 'order'), namespace='order')),
    path('', include(('goods.urls', 'goods'), namespace='goods')),
    path('api/', include('rest_framework.urls')),
    url(r'^swagger/', SchemaView.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # url(r'^redoc/', SchemaView.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('admin/goods/', include(('admin.admin_goods.urls', 'admin_goods'), namespace='admin_goods')),
    path('admin/user/', include(('admin.admin_user.urls', 'admin_user'), namespace='admin_user'))
]
