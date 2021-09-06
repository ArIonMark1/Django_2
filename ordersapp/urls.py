from django.urls import path

import users.views as auth
from django.contrib.auth.decorators import login_required
from ordersapp.views import OrderList, OrderItemCreate, OrderItemUpdate, OrderItemsDelete, OrderItemsRead, \
    order_forming_complete

app_name = 'ordersapp'

urlpatterns = [
    path('', OrderList.as_view(), name='orders_list'),
    path('read/<pk>/', OrderItemsRead.as_view(), name='order_read'),
    path('update/<pk>/', OrderItemUpdate.as_view(), name='order_update'),
    path('delete/<pk>/', OrderItemsDelete.as_view(), name='order_delete'),
    path('create/', OrderItemCreate.as_view(), name='order_create'),
    path('forming/complete/<pk>/', order_forming_complete, name='order_forming_complete'),
]
