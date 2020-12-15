from apps.goods.models import GoodsType
from rest_framework import serializers


class GoodsTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GoodsType
        fields = ['id', 'name', 'logo', 'image']
