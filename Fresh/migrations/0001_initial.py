# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-29 19:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shop', '0008_auto_20170724_2240'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='shop.Order')),
                ('owner', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'User order',
                'verbose_name_plural': 'User orders',
                'permissions': (('view_all_userorders', 'Can see all user orders'),),
            },
        ),
        migrations.CreateModel(
            name='UserOrderItem',
            fields=[
                ('orderitem', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='shop.OrderItem')),
                ('shipped', models.BooleanField(default=False, verbose_name='Shipped')),
                ('userorder', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='Fresh.UserOrder')),
            ],
            options={
                'verbose_name': 'User order item',
                'verbose_name_plural': 'User order items',
            },
        ),
        migrations.CreateModel(
            name='UserProduct',
            fields=[
                ('product', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='shop.Product')),
                ('owner', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
        ),
        migrations.CreateModel(
            name='ExtendedProduct',
            fields=[
            ],
            options={
                'permissions': (('view_all_products', 'Can see all products'),),
                'proxy': True,
            },
            bases=('shop.product',),
        ),
    ]
