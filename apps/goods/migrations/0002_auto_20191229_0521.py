# Generated by Django 3.0.1 on 2019-12-28 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goodstype',
            name='image',
            field=models.CharField(max_length=255, verbose_name='商品类型图片'),
        ),
    ]
